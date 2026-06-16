# 📊 Interactive Sales Dashboard

🔗 **Live demo:** https://data-automation-portfolio-sajcxzwvzcxxhwt4ccqx9d.streamlit.app/

A polished, interactive sales analytics dashboard built with **Streamlit** and **Plotly**. Upload-free, deploy-ready, and fully interactive — pick a date range, slice by region, category and channel, and watch the KPIs and charts update in real time.

> Built as a portfolio piece for **Data Automation & Dashboard Consulting**. The data is **synthetic demo data** generated with a seeded script — no real customers involved.

## What it does

- **KPI cards** — revenue, profit, margin, order count and average order value, with contextual deltas vs. the full dataset.
- **Monthly revenue & profit trend** — interactive line chart across all 12 months of 2024.
- **Revenue by category** — horizontal bar breakdown.
- **Top 10 products** — best sellers by revenue.
- **Revenue by region** — donut chart.
- **Filtered orders table** — sortable, scrollable, with a **one-click CSV download** of exactly what you filtered.
- **Sidebar filters** — date range, region, category and channel, all combinable.

Performance: data loading and CSV export are cached with `@st.cache_data` so filtering stays instant.

## Tech stack

| Layer        | Tool |
|--------------|------|
| App / UI     | Streamlit 1.58 |
| Charts       | Plotly 6.7 |
| Data         | pandas / numpy |
| Architecture | Pure data/KPI logic in `data.py`, fully unit-testable without the server |

The logic is deliberately **separated from the UI**: every KPI and aggregation lives in `data.py` as a pure function, so it can be tested with `test_data.py` without ever starting Streamlit.

## Screenshot

![Dashboard screenshot](docs/screenshot.png)

*(Run locally and take a screenshot to replace this placeholder.)*

## Project structure

```
02-sales-dashboard-streamlit/
├── app.py              # Streamlit UI (imports from data.py)
├── data.py             # Pure data + KPI functions (testable)
├── generate_data.py    # Creates the synthetic dataset
├── test_data.py        # Smoke test for the data layer
├── requirements.txt
├── .streamlit/
│   └── config.toml     # Clean theme
└── data/
    └── sales.csv       # Generated dataset (~5000 rows)
```

## Run locally

```powershell
# 1. (Optional) install dependencies
pip install -r requirements.txt

# 2. Generate the synthetic dataset
python generate_data.py

# 3. Verify the data layer (no server needed)
python test_data.py

# 4. Launch the dashboard
streamlit run app.py
```

Then open the URL Streamlit prints (default http://localhost:8501).

## Deploy to Streamlit Community Cloud

1. Push this folder to a public **GitHub** repository.
2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in with GitHub.
3. Click **New app**, pick the repo/branch, and set the main file to `app.py`.
4. Deploy. Streamlit installs `requirements.txt` automatically and gives you a shareable public URL.

> `data/sales.csv` is committed, so the deployed app works out of the box. To regenerate the data, run `python generate_data.py` and commit the new CSV.

## Notes

- The dataset is **100% synthetic** and reproducible (seeded). It is not based on any real business.
- The data layer is decoupled from Streamlit, making it easy to swap in a real database or a different front end later.

---
*Part of the [Data Automation & Dashboard portfolio](../README.md) — Francisco Pinto Alves Dias · franciscodias942@gmail.com*
