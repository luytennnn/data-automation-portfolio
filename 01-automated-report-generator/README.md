# Automated Sales Report Generator

> One command turns a raw sales CSV into a polished, multi-sheet Excel workbook and a print-ready PDF — KPIs, charts, and data quality notes included.

A portfolio piece for **Data Automation & Dashboard** work: a small, dependable Python pipeline that ingests messy sales data, cleans it, computes the numbers a manager actually asks for, and ships two client-ready deliverables. Designed to run unattended (e.g. nightly via Windows Task Scheduler).

> **Note:** the dataset is **100% synthetic** — generated locally with a fixed random seed for reproducibility. No real customer or company data is used.

## What it does

- **Cleans** the raw CSV — removes exact duplicate orders and rows with missing critical fields, and reports exactly how many were dropped (data provenance).
- **Computes KPIs** — total revenue, total profit, profit margin %, total orders, average order value, top 10 products, monthly trend, and revenue by region & category.
- **Builds charts** with matplotlib — monthly revenue/profit trend, top products, revenue by region, category share (saved as PNGs).
- **Produces an Excel report** (`Sales_Report.xlsx`) — formatted Summary/KPI sheet with a top-products table, a Monthly Trend sheet with a **native Excel line chart**, By Region / By Category breakdowns, and a frozen-header full Data sheet with currency formatting.
- **Produces a PDF report** (`Sales_Report.pdf`) — title, styled KPI table, data-quality note, and all four charts embedded.
- **Logs every step** via the `logging` module, so a scheduled run leaves a clean audit trail.

## Stack

- **Python 3.13**
- **pandas** + **numpy** — data wrangling & KPIs
- **matplotlib** — chart rendering (headless `Agg` backend)
- **XlsxWriter** — formatted Excel workbook with a native chart
- **reportlab** — PDF assembly
- **openpyxl** — Excel reading/validation

## How to run

From the project folder (Windows PowerShell):

```powershell
pip install -r requirements.txt
python generate_data.py
python generate_report.py
```

Outputs land in `output/`:

```
output/Sales_Report.xlsx
output/Sales_Report.pdf
output/charts/*.png
```

## Sample output

**`Sales_Report.xlsx`** (5 sheets):

| Sheet | Contents |
|-------|----------|
| Summary | KPI block (revenue, profit, margin, orders, AOV) with currency/percent formats, top-10 products table, and a data-quality provenance note |
| Monthly Trend | Month-by-month revenue & profit table **plus an embedded native Excel line chart** |
| By Region | Revenue per region |
| By Category | Revenue per category |
| Data | Full cleaned dataset with derived `revenue` / `profit` columns, frozen header, currency formatting |

**`Sales_Report.pdf`** — a single document with the report title, a styled KPI summary table, a data-quality sentence, and the four charts embedded (monthly trend, top products, by region, category share).

On the bundled synthetic data the report shows roughly **EUR 1.0M revenue**, **EUR 566K profit**, and a **~56% margin** across **3,997 clean orders** (4,001 raw rows -> 1 duplicate + 3 null rows removed).

## Scheduling

The pipeline writes no prompts and uses a headless chart backend, so it runs unattended. To refresh the report nightly with **Windows Task Scheduler**:

1. Open Task Scheduler -> **Create Basic Task**.
2. Trigger: **Daily** (pick a time).
3. Action: **Start a program**
   - Program/script: `python`
   - Arguments: `generate_report.py`
   - Start in: the project folder path
4. (Optional) add a first action that runs `generate_data.py` if the source data is regenerated each cycle.

In production you would point `INPUT_CSV` at the top of `generate_report.py` to a real data export instead of the synthetic file.

## Project structure

```
01-automated-report-generator/
├── generate_data.py      # creates synthetic data/raw_sales.csv (seeded)
├── generate_report.py    # clean -> KPIs -> charts -> Excel + PDF
├── requirements.txt
├── README.md
├── data/
│   └── raw_sales.csv
└── output/
    ├── Sales_Report.xlsx
    ├── Sales_Report.pdf
    └── charts/
```

---
*Part of the [Data Automation & Dashboard portfolio](../README.md) — Francisco Pinto Alves Dias · franciscodias942@gmail.com*
