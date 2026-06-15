# Excel Data Cleaner & Formatter

**Turn messy spreadsheets into clean, analysis-ready data automatically.**

Clients send Excel files exported from legacy systems, POS terminals, and manual data entry. They are full of inconsistent casing, stray whitespace, duplicate rows, missing values, dates stored as text, and prices with currency symbols. This tool ingests that mess and produces a clean, formatted workbook in seconds — plus an audit sheet documenting exactly what was changed.

## What it cleans

- **Junk header rows** — auto-detects and skips title/banner rows sitting above the real headers
- **Inconsistent text** — trims whitespace and title-cases names, cities, products, statuses
- **Duplicate rows** — detects and removes exact duplicates
- **Empty columns & rows** — drops fully-blank columns and rows
- **Dates as text** — parses mixed formats (`2023-01-31`, `31/01/2023`, `Jan 31 2023`, ...) into real datetimes
- **Numbers stored as text** — strips currency symbols (`€`, `$`), thousands separators and spaces, coerces to numeric
- **Missing values** — fills numeric blanks with `0` and flags missing text with `MISSING`

## Output

A formatted `.xlsx` with two sheets:

1. **Cleaned Data** — frozen bold header row, auto-fitted column widths, date and currency number formats.
2. **Cleaning Report** — line-by-line audit: rows/columns dropped, duplicates removed, columns coerced, missing values handled, final row count.

## Stack

Python 3.13 · pandas · numpy · openpyxl · XlsxWriter

## How to run

```powershell
pip install -r requirements.txt

# 1. (optional) generate a synthetic messy sample
python make_messy_file.py

# 2. clean it (defaults shown; override with your own paths)
python clean_excel.py --input samples/messy_input.xlsx --output output/cleaned.xlsx
```

`clean_excel.py` also exposes `clean_workbook(input_path, output_path)` for use as a library.

## Before / After

**Before** (`samples/messy_input.xlsx`) — 427 sheet rows including a junk banner row and the real header, 11 columns. Text like `"  Sofia"`, `"AHMED"`, `"PORTO "`; prices like `"€227.80"`, `"$1,205.50"`; dates like `"17 Aug 2023"` stored as text; one fully-empty column; 5 blank rows; 20 duplicate rows; ~250 missing values.

**After** (`output/cleaned.xlsx`) — 400 clean data rows, 10 columns. Names title-cased and trimmed (`Sofia`, `Ahmed`, `Porto`), prices as floats (`227.80`), dates as real datetimes, blank column/rows dropped, duplicates removed, missing values filled/flagged — all formatted and frozen, with the Cleaning Report sheet logging every change.

> **Note:** the sample data is generated synthetic data (`make_messy_file.py`, seeded for reproducibility). No real customer data is included.

---
*Part of the [Data Automation & Dashboard portfolio](../README.md) — Francisco Pinto Alves Dias · franciscodias942@gmail.com*
