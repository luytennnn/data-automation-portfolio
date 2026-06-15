# Data Automation & Dashboard — Portfolio

**Francisco Pinto Alves Dias** — Data Automation & Dashboard Consultant
📍 Portugal · ✉️ franciscodias942@gmail.com · 🌐 available for freelance & contract work

I build the boring-but-valuable parts of a data workflow: pull messy data, clean it,
automate the report, and ship a dashboard a manager can actually read. Below are five
self-contained projects — each runs end to end on synthetic (but realistic) demo data,
each has its own README, and each was tested before being committed.

| # | Project | What a client gets | Stack |
|---|---------|--------------------|-------|
| 01 | [Automated Sales Report Generator](01-automated-report-generator) | One command → formatted multi-sheet **Excel** + print-ready **PDF** with charts. Schedulable (Task Scheduler). | Python · Pandas · XlsxWriter · Matplotlib · ReportLab |
| 02 | [Interactive Sales Dashboard](02-sales-dashboard-streamlit) | Live filterable web dashboard — KPI cards, trends, CSV export. Deployable to Streamlit Cloud (shareable link). | Streamlit · Plotly · Pandas |
| 03 | [Excel Data Cleaner & Formatter](03-excel-cleaner) | Messy spreadsheet → clean, formatted Excel + an automatic change-log sheet. | Python · openpyxl · Pandas |
| 04 | [Power BI Sales Analytics Model](04-powerbi-sales-dashboard) | Star-schema model + documented DAX library (YTD, YoY, margin, running totals). | Power BI · DAX · star schema |
| 05 | [Amazon Price & Competitor Analyzer](05-amazon-price-analyzer) | One-click scraper bookmarklet → instant price-vs-rating dashboard, 100% in-browser. | JavaScript · HTML/Canvas · Node (tests) |

## What I do for clients
- **Automated reporting** — turn a recurring manual report into a one-command (or scheduled) pipeline.
- **Dashboards** — Power BI, Streamlit, or standalone HTML; interactive, branded, shareable.
- **Data cleaning** — fix the messy Excel/CSV exports nobody wants to touch.
- **Data scraping & enrichment** — collect structured data from the web for analysis (politely, within limits).

## Run any project
Each folder has its own `README.md` and `requirements.txt`. Quick start:
```powershell
# 01 — report generator
cd "01-automated-report-generator"; python generate_data.py; python generate_report.py
# 02 — dashboard
cd "02-sales-dashboard-streamlit"; python generate_data.py; streamlit run app.py
# 03 — excel cleaner
cd "03-excel-cleaner"; python make_messy_file.py; python clean_excel.py
# 04 — power bi model
cd "04-powerbi-sales-dashboard"; python generate_data.py   # then import CSVs into Power BI Desktop
# 05 — amazon analyzer
cd "05-amazon-price-analyzer"; node test_analyzer.js        # then open index.html, "Load sample data"
```

## Notes
- All datasets are **synthetic**, produced by reproducible seeded scripts — no real or
  confidential client data is included.
- Verified before commit: 01 generates the Excel+PDF; 02's data layer passes its smoke test;
  03 cleans 427→400 rows with a change log; 04 passes FK-integrity + `pbi report validate`;
  05 passes 19 logic assertions.
- License: [MIT](LICENSE).
