# Funcoes puras de dados e KPIs, separadas da UI para serem testaveis sem Streamlit
import pandas as pd


def load_data(path):
    # Le o CSV e deriva colunas de receita, lucro e mes
    df = pd.read_csv(path, parse_dates=["order_date"])
    df["revenue"] = df["units"] * df["unit_price"]
    df["profit"] = df["units"] * (df["unit_price"] - df["cost"])
    df["month"] = df["order_date"].dt.to_period("M").dt.to_timestamp()
    return df


def filter_data(df, date_range=None, regions=None, categories=None, channels=None):
    # Aplica filtros opcionais; None significa "sem filtro"
    out = df
    if date_range is not None:
        start, end = date_range
        start = pd.Timestamp(start)
        end = pd.Timestamp(end)
        out = out[(out["order_date"] >= start) & (out["order_date"] <= end)]
    if regions:
        out = out[out["region"].isin(regions)]
    if categories:
        out = out[out["category"].isin(categories)]
    if channels:
        out = out[out["channel"].isin(channels)]
    return out


def total_revenue(df):
    # Receita total
    return float(df["revenue"].sum())


def total_profit(df):
    # Lucro total
    return float(df["profit"].sum())


def total_units(df):
    # Unidades vendidas
    return int(df["units"].sum())


def total_orders(df):
    # Numero de encomendas
    return int(len(df))


def margin(df):
    # Margem de lucro em percentagem (0 se sem receita)
    rev = total_revenue(df)
    if rev == 0:
        return 0.0
    return total_profit(df) / rev * 100.0


def avg_order_value(df):
    # Valor medio por encomenda
    if len(df) == 0:
        return 0.0
    return total_revenue(df) / len(df)


def monthly_trend(df):
    # Receita e lucro agregados por mes, ordenados cronologicamente
    g = df.groupby("month", as_index=False).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
    )
    return g.sort_values("month").reset_index(drop=True)


def top_products(df, n=10):
    # Top-N produtos por receita
    g = df.groupby("product", as_index=False).agg(
        revenue=("revenue", "sum"),
        units=("units", "sum"),
    )
    return g.sort_values("revenue", ascending=False).head(n).reset_index(drop=True)


def by_region(df):
    # Receita por regiao
    g = df.groupby("region", as_index=False).agg(revenue=("revenue", "sum"))
    return g.sort_values("revenue", ascending=False).reset_index(drop=True)


def by_category(df):
    # Receita e lucro por categoria
    g = df.groupby("category", as_index=False).agg(
        revenue=("revenue", "sum"),
        profit=("profit", "sum"),
    )
    return g.sort_values("revenue", ascending=False).reset_index(drop=True)
