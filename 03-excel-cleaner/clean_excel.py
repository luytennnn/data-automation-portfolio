"""Excel Data Cleaner & Formatter — turn messy spreadsheets into clean, analysis-ready data."""
import argparse
import logging
import re
import sys

import numpy as np
import pandas as pd

sys.stdout.reconfigure(encoding="utf-8")

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
log = logging.getLogger("clean_excel")

# Columns we treat as text (will be trimmed + title-cased)
TEXT_HINTS = ["name", "first", "last", "city", "product", "status", "customer"]
# Columns we try to parse as dates
DATE_HINTS = ["date"]
# Columns we try to coerce to numbers
NUM_HINTS = ["price", "amount", "total", "quantity", "qty", "cost"]


def detect_header_row(raw):
    """Pick the row with the most non-null, mostly-text cells as the real header."""
    best_idx, best_score = 0, -1
    for i in range(min(5, len(raw))):
        row = raw.iloc[i]
        non_null = row.notna().sum()
        # Header rows are wide and textual; junk title rows are sparse
        if non_null > best_score:
            best_score, best_idx = non_null, i
    return best_idx


def clean_text(series):
    """Trim whitespace and title-case text values."""
    return series.apply(lambda v: " ".join(str(v).split()).title() if pd.notna(v) and str(v).strip() else np.nan)


def coerce_numeric(series):
    """Strip currency symbols, thousands separators and spaces, then convert to float."""
    def parse(v):
        if pd.isna(v):
            return np.nan
        s = re.sub(r"[^\d.\-]", "", str(v))  # keep digits, dot, minus
        try:
            return float(s) if s not in ("", "-", ".") else np.nan
        except ValueError:
            return np.nan
    return series.apply(parse)


def coerce_dates(series):
    """Parse mixed text date formats into real datetimes."""
    return pd.to_datetime(series, errors="coerce", dayfirst=True, format="mixed")


def clean_workbook(input_path, output_path):
    """Read a messy workbook, clean it, and write a formatted .xlsx with a Cleaning Report."""
    log.info("Reading %s", input_path)
    raw = pd.read_excel(input_path, header=None)

    report = []  # list of (action, detail) tuples for the report sheet

    # 1. Detect and skip junk header rows
    header_idx = detect_header_row(raw)
    log.info("Detected real header at row %d (0-based)", header_idx)
    report.append(("Junk rows skipped above header", header_idx))
    headers = raw.iloc[header_idx].tolist()
    df = raw.iloc[header_idx + 1:].copy()
    df.columns = [str(h).strip() if pd.notna(h) else f"col_{j}" for j, h in enumerate(headers)]
    df = df.reset_index(drop=True)
    rows_start = len(df)
    report.append(("Rows read (after header)", rows_start))

    # 2. Drop fully-empty columns
    before_cols = df.shape[1]
    df = df.dropna(axis=1, how="all")
    dropped_cols = before_cols - df.shape[1]
    if dropped_cols:
        log.info("Dropped %d fully-empty column(s)", dropped_cols)
    report.append(("Fully-empty columns dropped", dropped_cols))

    # 3. Drop fully-empty rows
    before_rows = len(df)
    df = df.dropna(axis=0, how="all")
    dropped_rows = before_rows - len(df)
    if dropped_rows:
        log.info("Dropped %d fully-empty row(s)", dropped_rows)
    report.append(("Fully-empty rows dropped", dropped_rows))

    # 4. Coerce types column by column
    coerced_log = []
    for col in df.columns:
        low = col.lower()
        if any(h in low for h in DATE_HINTS):
            df[col] = coerce_dates(df[col])
            coerced_log.append(f"{col} -> datetime")
        elif any(h in low for h in NUM_HINTS):
            df[col] = coerce_numeric(df[col])
            coerced_log.append(f"{col} -> numeric")
        elif any(h in low for h in TEXT_HINTS):
            df[col] = clean_text(df[col])
            coerced_log.append(f"{col} -> trimmed + title-case")
    for entry in coerced_log:
        log.info("Coerced %s", entry)
    report.append(("Columns coerced", "; ".join(coerced_log) if coerced_log else "none"))

    # 5. Remove duplicate rows
    before_dupes = len(df)
    df = df.drop_duplicates().reset_index(drop=True)
    dupes_removed = before_dupes - len(df)
    if dupes_removed:
        log.info("Removed %d duplicate row(s)", dupes_removed)
    report.append(("Duplicate rows removed", dupes_removed))

    # 6. Handle missing values: numeric -> 0, text/date -> "MISSING" flag
    nulls_handled = 0
    for col in df.columns:
        n = int(df[col].isna().sum())
        if n == 0:
            continue
        nulls_handled += n
        if pd.api.types.is_numeric_dtype(df[col]):
            df[col] = df[col].fillna(0)
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            pass  # leave dates as NaT (Excel shows blank)
        else:
            df[col] = df[col].fillna("MISSING")
    log.info("Filled/flagged %d missing value(s)", nulls_handled)
    report.append(("Missing values handled", nulls_handled))
    report.append(("Final clean rows", len(df)))
    report.append(("Final columns", df.shape[1]))

    # 7. Write formatted output with XlsxWriter
    log.info("Writing %s", output_path)
    with pd.ExcelWriter(output_path, engine="xlsxwriter", datetime_format="yyyy-mm-dd") as writer:
        df.to_excel(writer, sheet_name="Cleaned Data", index=False)
        wb = writer.book
        ws = writer.sheets["Cleaned Data"]

        # Header style: bold, white on dark blue
        header_fmt = wb.add_format({"bold": True, "font_color": "white", "bg_color": "#1F4E78",
                                    "border": 1, "align": "center", "valign": "vcenter"})
        date_fmt = wb.add_format({"num_format": "yyyy-mm-dd"})
        money_fmt = wb.add_format({"num_format": "#,##0.00"})

        # Re-write header row with style
        for c, name in enumerate(df.columns):
            ws.write(0, c, name, header_fmt)

        # Freeze header row
        ws.freeze_panes(1, 0)

        # Auto column widths + number/date formats
        for c, name in enumerate(df.columns):
            maxlen = max([len(str(name))] + [len(str(v)) for v in df[name].head(200)])
            width = min(max(maxlen + 2, 10), 40)
            low = name.lower()
            if pd.api.types.is_datetime64_any_dtype(df[name]):
                ws.set_column(c, c, width, date_fmt)
            elif any(h in low for h in NUM_HINTS) and pd.api.types.is_numeric_dtype(df[name]):
                ws.set_column(c, c, width, money_fmt)
            else:
                ws.set_column(c, c, width)

        # Cleaning Report sheet
        rep_df = pd.DataFrame(report, columns=["What was changed", "Value"])
        rep_df.to_excel(writer, sheet_name="Cleaning Report", index=False)
        rws = writer.sheets["Cleaning Report"]
        for c, name in enumerate(rep_df.columns):
            rws.write(0, c, name, header_fmt)
        rws.set_column(0, 0, 35)
        rws.set_column(1, 1, 55)
        rws.freeze_panes(1, 0)

    log.info("Done. %d rows x %d cols written to %s", len(df), df.shape[1], output_path)
    return df, report


def main():
    p = argparse.ArgumentParser(description="Clean and format a messy Excel file.")
    p.add_argument("--input", default="samples/messy_input.xlsx", help="Path to messy input .xlsx")
    p.add_argument("--output", default="output/cleaned.xlsx", help="Path for cleaned .xlsx")
    args = p.parse_args()
    clean_workbook(args.input, args.output)


if __name__ == "__main__":
    main()
