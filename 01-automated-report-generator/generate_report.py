"""Automated sales report generator: clean -> KPIs -> charts -> Excel + PDF."""
import logging
from pathlib import Path

import matplotlib
matplotlib.use("Agg")  # headless backend, no GUI needed for scheduling
import matplotlib.pyplot as plt
import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image,
)

# --- Paths (parameterized at top) ---
BASE = Path(__file__).parent
INPUT_CSV = BASE / "data" / "raw_sales.csv"
OUTPUT_DIR = BASE / "output"
CHARTS_DIR = OUTPUT_DIR / "charts"
EXCEL_PATH = OUTPUT_DIR / "Sales_Report.xlsx"
PDF_PATH = OUTPUT_DIR / "Sales_Report.pdf"

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("generate_report")


def load_and_clean(path):
    """Read the raw CSV and clean dupes/nulls, returning the tidy dataframe + cleaning stats."""
    if not path.exists():
        raise FileNotFoundError(f"Input not found: {path}. Run generate_data.py first.")
    df = pd.read_csv(path, parse_dates=["order_date"])
    raw_rows = len(df)

    # Drop exact duplicate orders
    df = df.drop_duplicates()
    after_dupes = len(df)

    # Drop rows missing any essential field
    essential = ["units", "unit_price", "region"]
    df = df.dropna(subset=essential)
    after_nulls = len(df)

    # Derive financial columns
    df["units"] = df["units"].astype(int)
    df["revenue"] = (df["units"] * df["unit_price"]).round(2)
    df["profit"] = (df["units"] * (df["unit_price"] - df["cost"])).round(2)
    df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()

    stats = {
        "raw_rows": raw_rows,
        "duplicates_removed": raw_rows - after_dupes,
        "null_rows_removed": after_dupes - after_nulls,
        "clean_rows": after_nulls,
    }
    log.info("Cleaning: %d raw -> %d clean (%d dupes, %d null rows removed)",
             stats["raw_rows"], stats["clean_rows"],
             stats["duplicates_removed"], stats["null_rows_removed"])
    return df, stats


def compute_kpis(df):
    """Compute headline KPIs and breakdown tables from the clean dataframe."""
    total_revenue = df["revenue"].sum()
    total_profit = df["profit"].sum()
    margin = (total_profit / total_revenue * 100) if total_revenue else 0.0

    top_products = (df.groupby("product")["revenue"].sum()
                    .sort_values(ascending=False).head(10).reset_index())
    by_region = (df.groupby("region")["revenue"].sum()
                 .sort_values(ascending=False).reset_index())
    by_category = (df.groupby("category")["revenue"].sum()
                   .sort_values(ascending=False).reset_index())
    monthly = (df.groupby("month")[["revenue", "profit"]].sum()
               .reset_index().sort_values("month"))
    monthly["month_label"] = monthly["month"].dt.strftime("%b %Y")

    kpis = {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "margin_pct": margin,
        "total_orders": len(df),
        "avg_order_value": total_revenue / len(df) if len(df) else 0.0,
    }
    log.info("KPIs: revenue=%.2f profit=%.2f margin=%.1f%% orders=%d",
             total_revenue, total_profit, margin, len(df))
    return kpis, top_products, by_region, by_category, monthly


def build_charts(top_products, by_region, by_category, monthly):
    """Render matplotlib charts to PNG and return their file paths."""
    CHARTS_DIR.mkdir(parents=True, exist_ok=True)
    paths = {}

    # Monthly revenue & profit trend
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.plot(monthly["month_label"], monthly["revenue"], marker="o", label="Revenue")
    ax.plot(monthly["month_label"], monthly["profit"], marker="o", label="Profit")
    ax.set_title("Monthly Revenue & Profit Trend (2024)")
    ax.set_ylabel("EUR")
    ax.legend()
    ax.grid(alpha=0.3)
    plt.xticks(rotation=45, ha="right")
    fig.tight_layout()
    paths["trend"] = CHARTS_DIR / "monthly_trend.png"
    fig.savefig(paths["trend"], dpi=120)
    plt.close(fig)

    # Top 10 products by revenue
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.barh(top_products["product"][::-1], top_products["revenue"][::-1], color="#2c6fbb")
    ax.set_title("Top 10 Products by Revenue")
    ax.set_xlabel("EUR")
    fig.tight_layout()
    paths["top"] = CHARTS_DIR / "top_products.png"
    fig.savefig(paths["top"], dpi=120)
    plt.close(fig)

    # Revenue by region
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.bar(by_region["region"], by_region["revenue"], color="#3aa76d")
    ax.set_title("Revenue by Region")
    ax.set_ylabel("EUR")
    fig.tight_layout()
    paths["region"] = CHARTS_DIR / "by_region.png"
    fig.savefig(paths["region"], dpi=120)
    plt.close(fig)

    # Revenue share by category
    fig, ax = plt.subplots(figsize=(5, 4))
    ax.pie(by_category["revenue"], labels=by_category["category"],
           autopct="%1.0f%%", startangle=90)
    ax.set_title("Revenue Share by Category")
    fig.tight_layout()
    paths["category"] = CHARTS_DIR / "by_category.png"
    fig.savefig(paths["category"], dpi=120)
    plt.close(fig)

    log.info("Saved %d charts to %s", len(paths), CHARTS_DIR)
    return paths


def build_excel(df, stats, kpis, top_products, by_region, by_category, monthly):
    """Write a formatted multi-sheet Excel report with a native chart."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    with pd.ExcelWriter(EXCEL_PATH, engine="xlsxwriter") as writer:
        wb = writer.book

        # Reusable formats
        title_fmt = wb.add_format({"bold": True, "font_size": 16, "font_color": "#1f3864"})
        header_fmt = wb.add_format({"bold": True, "bg_color": "#1f3864", "font_color": "white",
                                    "border": 1, "align": "center", "valign": "vcenter"})
        label_fmt = wb.add_format({"bold": True})
        money_fmt = wb.add_format({"num_format": "€#,##0.00"})
        pct_fmt = wb.add_format({"num_format": "0.0%"})
        int_fmt = wb.add_format({"num_format": "#,##0"})

        # --- Summary / KPI sheet ---
        ws = wb.add_worksheet("Summary")
        ws.set_column("A:A", 26)
        ws.set_column("B:B", 18)
        ws.write("A1", "Sales Report - 2024 (Synthetic Demo Data)", title_fmt)
        rows = [
            ("Total Revenue", kpis["total_revenue"], money_fmt),
            ("Total Profit", kpis["total_profit"], money_fmt),
            ("Profit Margin", kpis["margin_pct"] / 100, pct_fmt),
            ("Total Orders", kpis["total_orders"], int_fmt),
            ("Avg Order Value", kpis["avg_order_value"], money_fmt),
        ]
        for i, (label, value, fmt) in enumerate(rows, start=3):
            ws.write(i, 0, label, label_fmt)
            ws.write(i, 1, value, fmt)

        # Cleaning provenance note
        note_row = 3 + len(rows) + 1
        ws.write(note_row, 0, "Data quality", label_fmt)
        ws.write(note_row + 1, 0, f"Raw rows: {stats['raw_rows']}")
        ws.write(note_row + 2, 0, f"Duplicates removed: {stats['duplicates_removed']}")
        ws.write(note_row + 3, 0, f"Null rows removed: {stats['null_rows_removed']}")
        ws.write(note_row + 4, 0, f"Clean rows: {stats['clean_rows']}")

        # Top products table on the summary sheet
        tp_start = 3
        ws.write(2, 4, "Top 10 Products", label_fmt)
        ws.write(tp_start, 4, "Product", header_fmt)
        ws.write(tp_start, 5, "Revenue", header_fmt)
        ws.set_column("E:E", 26)
        ws.set_column("F:F", 16)
        for i, r in top_products.iterrows():
            ws.write(tp_start + 1 + i, 4, r["product"])
            ws.write(tp_start + 1 + i, 5, r["revenue"], money_fmt)

        # --- Monthly trend sheet with native Excel chart ---
        monthly_out = monthly[["month_label", "revenue", "profit"]].rename(
            columns={"month_label": "Month", "revenue": "Revenue", "profit": "Profit"})
        monthly_out.to_excel(writer, sheet_name="Monthly Trend", index=False, startrow=0)
        ws_m = writer.sheets["Monthly Trend"]
        ws_m.set_column("A:A", 12)
        ws_m.set_column("B:C", 16, money_fmt)
        for col, name in enumerate(monthly_out.columns):
            ws_m.write(0, col, name, header_fmt)

        n = len(monthly_out)
        chart = wb.add_chart({"type": "line"})
        chart.add_series({
            "name": "Revenue",
            "categories": ["Monthly Trend", 1, 0, n, 0],
            "values": ["Monthly Trend", 1, 1, n, 1],
        })
        chart.add_series({
            "name": "Profit",
            "categories": ["Monthly Trend", 1, 0, n, 0],
            "values": ["Monthly Trend", 1, 2, n, 2],
        })
        chart.set_title({"name": "Monthly Revenue & Profit"})
        chart.set_size({"width": 640, "height": 360})
        ws_m.insert_chart("E2", chart)

        # --- Breakdown sheets ---
        by_region.rename(columns={"region": "Region", "revenue": "Revenue"}).to_excel(
            writer, sheet_name="By Region", index=False)
        by_category.rename(columns={"category": "Category", "revenue": "Revenue"}).to_excel(
            writer, sheet_name="By Category", index=False)
        for sheet, ncols in [("By Region", 2), ("By Category", 2)]:
            wsx = writer.sheets[sheet]
            wsx.set_column(0, 0, 20)
            wsx.set_column(1, 1, 16, money_fmt)

        # --- Full clean data sheet ---
        data_cols = ["order_id", "order_date", "product", "category", "region",
                     "units", "unit_price", "cost", "revenue", "profit"]
        df[data_cols].to_excel(writer, sheet_name="Data", index=False)
        ws_d = writer.sheets["Data"]
        for col, name in enumerate(data_cols):
            ws_d.write(0, col, name, header_fmt)
        ws_d.set_column("A:A", 14)
        ws_d.set_column("B:B", 12)
        ws_d.set_column("C:C", 26)
        ws_d.set_column("D:E", 14)
        ws_d.freeze_panes(1, 0)

    log.info("Wrote Excel report to %s", EXCEL_PATH)


def build_pdf(stats, kpis, chart_paths):
    """Assemble a PDF report with title, KPI table, and embedded charts."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle("title", parent=styles["Title"], textColor=colors.HexColor("#1f3864"))
    h2 = ParagraphStyle("h2", parent=styles["Heading2"], textColor=colors.HexColor("#1f3864"))

    doc = SimpleDocTemplate(str(PDF_PATH), pagesize=A4,
                            leftMargin=1.8 * cm, rightMargin=1.8 * cm,
                            topMargin=1.8 * cm, bottomMargin=1.8 * cm)
    flow = []
    flow.append(Paragraph("Sales Report - 2024", title_style))
    flow.append(Paragraph("Synthetic demo data - generated for portfolio purposes.", styles["Normal"]))
    flow.append(Spacer(1, 0.5 * cm))

    # KPI summary table
    flow.append(Paragraph("Key Performance Indicators", h2))
    kpi_data = [
        ["Metric", "Value"],
        ["Total Revenue", f"EUR {kpis['total_revenue']:,.2f}"],
        ["Total Profit", f"EUR {kpis['total_profit']:,.2f}"],
        ["Profit Margin", f"{kpis['margin_pct']:.1f}%"],
        ["Total Orders", f"{kpis['total_orders']:,}"],
        ["Avg Order Value", f"EUR {kpis['avg_order_value']:,.2f}"],
    ]
    table = Table(kpi_data, colWidths=[7 * cm, 7 * cm])
    table.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1f3864")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#eef3fa")]),
        ("PADDING", (0, 0), (-1, -1), 6),
    ]))
    flow.append(table)
    flow.append(Spacer(1, 0.3 * cm))
    flow.append(Paragraph(
        f"Data quality: {stats['raw_rows']} raw rows cleaned to {stats['clean_rows']} "
        f"({stats['duplicates_removed']} duplicate, {stats['null_rows_removed']} null rows removed).",
        styles["Italic"]))
    flow.append(Spacer(1, 0.4 * cm))

    # Embedded charts
    flow.append(Paragraph("Visual Analysis", h2))
    for key in ["trend", "top", "region", "category"]:
        img = chart_paths[key]
        flow.append(Image(str(img), width=15 * cm, height=7.5 * cm))
        flow.append(Spacer(1, 0.3 * cm))

    doc.build(flow)
    log.info("Wrote PDF report to %s", PDF_PATH)


def main():
    log.info("Starting automated sales report pipeline")
    df, stats = load_and_clean(INPUT_CSV)
    kpis, top_products, by_region, by_category, monthly = compute_kpis(df)
    chart_paths = build_charts(top_products, by_region, by_category, monthly)
    build_excel(df, stats, kpis, top_products, by_region, by_category, monthly)
    build_pdf(stats, kpis, chart_paths)
    log.info("Pipeline complete: %s + %s", EXCEL_PATH.name, PDF_PATH.name)


if __name__ == "__main__":
    main()
