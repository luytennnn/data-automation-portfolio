# Power BI Sales Analytics — Star Schema + DAX Library

A portfolio piece for a **Data Automation & Dashboard Consultant**. It delivers
the parts of a Power BI project that are the real engineering work and that can
be validated outside of a GUI: a clean, reproducible **star-schema dataset**, a
documented **relationship model**, and a professional **DAX measure library**
ready to paste into Power BI Desktop.

## What it demonstrates

- **Dimensional modelling** — a textbook single-fact star schema with conformed
  dimensions, correct surrogate keys and referential integrity.
- **Reproducible data engineering** — a seeded Python generator (pandas/numpy)
  that produces an identical 8,000-row sales dataset on every run, plus an
  automated integrity check.
- **DAX fluency** — 14 production-grade measures covering aggregation, profit
  math, time intelligence (YTD/MTD/PY/YoY/running total) and ranking.
- **Tooling discipline** — a PBIR report project scaffolded and structurally
  validated with `pbi-cli`, with an honest boundary on what still needs the GUI.

## The star schema

One central fact table, four dimensions, all one-to-many with single-direction
filtering. Full details and an ASCII diagram in
[`model/relationships.md`](model/relationships.md).

| Table          | Rows  | Grain / role                                  |
|----------------|-------|-----------------------------------------------|
| `fact_sales`   | 8,000 | One row per sales line (`sale_id`)            |
| `dim_date`     | 366   | Full 2024 calendar (leap year)                |
| `dim_product`  | 45    | Product → subcategory → category              |
| `dim_customer` | 400   | Customer → segment, region                    |
| `dim_store`    | 8     | Store → city, region                          |

`fact_sales` columns: `sale_id, date_key, product_key, customer_key, store_key,
units, unit_price, cost, sales_amount`.

## How to use it (Power BI Desktop)

### 1. Generate the data
```powershell
pip install -r requirements.txt
python generate_data.py      # writes the 5 CSVs into data/
python verify_data.py        # confirms row counts + FK integrity
```

### 2. Build the model
1. **Get Data → Text/CSV** and import all five files from `data/`.
2. **Model view → create relationships** exactly as in
   `model/relationships.md`:
   - `dim_date[date_key]  -> fact_sales[date_key]`
   - `dim_product[product_key]  -> fact_sales[product_key]`
   - `dim_customer[customer_key]  -> fact_sales[customer_key]`
   - `dim_store[store_key]  -> fact_sales[store_key]`
   - Each: cardinality **One-to-many**, cross-filter **Single**.
3. **Mark `dim_date` as a date table** (Table tools → Mark as date table →
   `dim_date[date]`) so time-intelligence measures work.
4. **Add the measures** from [`dax/measures.md`](dax/measures.md)
   (Modeling → New Measure, paste one at a time).

### 3. Build the visuals
Suggested layout (one page): KPI cards for *Total Sales / Gross Profit /
Margin % / Avg Order Value*; a line chart of *Total Sales* + *Sales PY* by month;
a bar chart of *Total Sales* by category; a map/bar by region; a Top-N product
table using *Product Rank*.

### Optional: open the scaffolded report project
A PBIR report shell lives in `report/SalesAnalytics.pbip`. Open it in Power BI
Desktop, then point it at the imported model and lay out the visuals above.

## Repository layout
```
04-powerbi-sales-dashboard/
├── generate_data.py          # seeded synthetic data generator
├── verify_data.py            # existence + FK integrity check
├── requirements.txt
├── data/                     # generated CSVs (run generate_data.py)
├── dax/measures.md           # documented DAX library (14 measures)
├── model/relationships.md    # star-schema documentation + diagram
└── report/                   # pbi-cli scaffolded PBIR project (.pbip)
```

## Status — what is verified vs. what needs Power BI Desktop

**Verified on this machine (reproducible):**
- `generate_data.py` runs and writes all 5 CSVs — confirmed row counts:
  `fact_sales` 8000, `dim_date` 366, `dim_product` 45, `dim_customer` 400,
  `dim_store` 8.
- `verify_data.py` confirms **0 orphan rows** for all four foreign keys
  (`product_key`, `customer_key`, `store_key`, `date_key`) and that
  `sales_amount == units * unit_price`.
- The PBIR report project was scaffolded with `pbi report create` and passes
  `pbi report validate --full` (**valid: True, 0 errors, 0 warnings**).
- The DAX in `dax/measures.md` is hand-written, correct, standard DAX.

**Requires Power BI Desktop (one-time, GUI):**
- Importing the CSVs and creating the relationships (a 5-minute click-through
  following `model/relationships.md`).
- Pasting the measures and marking `dim_date` as the date table.
- Rendering and laying out the actual visuals. The DAX was **not** executed
  against a live model here, and visuals were **not** hand-edited into the PBIR
  JSON — editing report JSON to render charts is fragile and cannot be visually
  confirmed without the GUI, so it was deliberately left out rather than faked.

> **Data is 100% synthetic** — generated with a fixed seed (`SEED = 42`) for a
> realistic retail scenario. It contains no real customers, stores, or sales.

---
*Part of the [Data Automation & Dashboard portfolio](../README.md) — Francisco Pinto Alves Dias · franciscodias942@gmail.com*
