# Dashboard interativo de vendas em Streamlit, importa a logica pura de data.py
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

import data as D

DATA_PATH = Path(__file__).parent / "data" / "sales.csv"

# Configuracao da pagina
st.set_page_config(
    page_title="Sales Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded",
)


@st.cache_data
def get_data():
    # Carrega os dados uma vez e mantem em cache
    return D.load_data(DATA_PATH)


def fmt_money(x):
    # Formata valores monetarios de forma compacta
    if abs(x) >= 1_000_000:
        return f"${x/1_000_000:.2f}M"
    if abs(x) >= 1_000:
        return f"${x/1_000:.1f}K"
    return f"${x:,.0f}"


# Carrega dados ou avisa se o ficheiro nao existe
if not DATA_PATH.exists():
    st.error("Data file not found. Run `python generate_data.py` first to create data/sales.csv.")
    st.stop()

df = get_data()

# --- Sidebar: filtros ---
st.sidebar.header("Filters")

min_date = df["order_date"].min().date()
max_date = df["order_date"].max().date()
date_range = st.sidebar.date_input(
    "Date range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date,
)

regions = st.sidebar.multiselect("Region", sorted(df["region"].unique()))
categories = st.sidebar.multiselect("Category", sorted(df["category"].unique()))
channels = st.sidebar.multiselect("Channel", sorted(df["channel"].unique()))

st.sidebar.markdown("---")
st.sidebar.caption("Synthetic demo data. Built with Streamlit + Plotly.")

# Normaliza o date_input (pode vir um unico valor enquanto o user escolhe)
if isinstance(date_range, (list, tuple)) and len(date_range) == 2:
    dr = (date_range[0], date_range[1])
else:
    dr = (min_date, max_date)

# Aplica filtros via funcao pura
fdf = D.filter_data(df, date_range=dr, regions=regions, categories=categories, channels=channels)

# --- Cabecalho ---
st.title("📊 Interactive Sales Dashboard")
st.caption("E-commerce performance overview — 2024 (synthetic demo data)")

if len(fdf) == 0:
    st.warning("No data matches the selected filters. Adjust the filters in the sidebar.")
    st.stop()

# --- KPIs com deltas vs dataset completo ---
rev = D.total_revenue(fdf)
prof = D.total_profit(fdf)
mar = D.margin(fdf)
orders = D.total_orders(fdf)
aov = D.avg_order_value(fdf)

# Deltas comparam o subconjunto filtrado com o total
full_rev = D.total_revenue(df)
full_prof = D.total_profit(df)
rev_share = (rev / full_rev * 100) if full_rev else 0
prof_share = (prof / full_prof * 100) if full_prof else 0

c1, c2, c3, c4, c5 = st.columns(5)
c1.metric("Revenue", fmt_money(rev), f"{rev_share:.0f}% of total")
c2.metric("Profit", fmt_money(prof), f"{prof_share:.0f}% of total")
c3.metric("Margin", f"{mar:.1f}%")
c4.metric("Orders", f"{orders:,}")
c5.metric("Avg Order Value", f"${aov:,.2f}")

st.markdown("---")

# --- Linha 1: tendencia mensal + receita por categoria ---
left, right = st.columns([3, 2])

with left:
    st.subheader("Monthly Revenue Trend")
    trend = D.monthly_trend(fdf)
    fig_trend = px.line(
        trend,
        x="month",
        y=["revenue", "profit"],
        markers=True,
        labels={"value": "Amount ($)", "month": "Month", "variable": "Metric"},
    )
    fig_trend.update_layout(legend_title_text="", hovermode="x unified", margin=dict(t=10))
    st.plotly_chart(fig_trend, use_container_width=True)

with right:
    st.subheader("Revenue by Category")
    cat = D.by_category(fdf)
    fig_cat = px.bar(
        cat,
        x="revenue",
        y="category",
        orientation="h",
        color="revenue",
        color_continuous_scale="Blues",
        labels={"revenue": "Revenue ($)", "category": ""},
    )
    fig_cat.update_layout(coloraxis_showscale=False, margin=dict(t=10), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_cat, use_container_width=True)

# --- Linha 2: top produtos + receita por regiao ---
left2, right2 = st.columns([3, 2])

with left2:
    st.subheader("Top 10 Products")
    top = D.top_products(fdf, n=10)
    fig_top = px.bar(
        top,
        x="revenue",
        y="product",
        orientation="h",
        color="revenue",
        color_continuous_scale="Teal",
        labels={"revenue": "Revenue ($)", "product": ""},
    )
    fig_top.update_layout(coloraxis_showscale=False, margin=dict(t=10), yaxis=dict(autorange="reversed"))
    st.plotly_chart(fig_top, use_container_width=True)

with right2:
    st.subheader("Revenue by Region")
    reg = D.by_region(fdf)
    fig_reg = px.pie(reg, names="region", values="revenue", hole=0.45)
    fig_reg.update_layout(margin=dict(t=10))
    st.plotly_chart(fig_reg, use_container_width=True)

st.markdown("---")

# --- Tabela filtrada + download ---
st.subheader("Filtered Orders")
display_cols = [
    "order_id", "order_date", "product", "category",
    "region", "channel", "units", "unit_price", "revenue", "profit",
]
st.dataframe(
    fdf[display_cols].sort_values("order_date", ascending=False),
    use_container_width=True,
    height=320,
)


@st.cache_data
def to_csv(d):
    # Converte para CSV em cache para o botao de download
    return d.to_csv(index=False).encode("utf-8")


st.download_button(
    "⬇️ Download filtered data (CSV)",
    data=to_csv(fdf[display_cols]),
    file_name="filtered_sales.csv",
    mime="text/csv",
)
