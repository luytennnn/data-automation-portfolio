# Smoke test das funcoes puras de data.py, sem servidor Streamlit
from pathlib import Path

import data as D

DATA_PATH = Path(__file__).parent / "data" / "sales.csv"


def run():
    assert DATA_PATH.exists(), "data/sales.csv missing - run generate_data.py first"

    df = D.load_data(DATA_PATH)

    # Estrutura basica
    assert len(df) >= 4000, f"expected ~5000 rows, got {len(df)}"
    for col in ["order_id", "order_date", "product", "category", "region",
                "channel", "units", "unit_price", "cost", "customer_id",
                "revenue", "profit", "month"]:
        assert col in df.columns, f"missing column {col}"

    # Sem nulos nas colunas chave
    assert df[["revenue", "profit", "units"]].notna().all().all(), "unexpected nulls"

    # KPIs sanos
    rev = D.total_revenue(df)
    prof = D.total_profit(df)
    mar = D.margin(df)
    units = D.total_units(df)
    orders = D.total_orders(df)
    aov = D.avg_order_value(df)

    assert rev > 0, "revenue must be positive"
    assert 0 < prof < rev, "profit must be positive and below revenue"
    assert 0 < mar < 100, f"margin out of range: {mar}"
    assert units > orders, "units should exceed order count"
    assert aov > 0, "AOV must be positive"

    # Identidade: receita = soma de revenue por linha
    assert abs(rev - (df["units"] * df["unit_price"]).sum()) < 1e-6, "revenue mismatch"

    # Agregacoes coerentes
    trend = D.monthly_trend(df)
    assert len(trend) == 12, f"expected 12 months, got {len(trend)}"
    assert abs(trend["revenue"].sum() - rev) < 1e-3, "monthly revenue must sum to total"

    top = D.top_products(df, n=10)
    assert len(top) == 10, "expected 10 top products"
    assert top["revenue"].is_monotonic_decreasing, "top products must be sorted desc"

    reg = D.by_region(df)
    assert abs(reg["revenue"].sum() - rev) < 1e-3, "region revenue must sum to total"

    cat = D.by_category(df)
    assert abs(cat["revenue"].sum() - rev) < 1e-3, "category revenue must sum to total"

    # filter_data reduz ou mantem
    f = D.filter_data(df, regions=["North"])
    assert len(f) < len(df), "region filter must reduce rows"
    assert set(f["region"].unique()) == {"North"}, "filter leaked other regions"

    # Filtro vazio devolve tudo
    assert len(D.filter_data(df)) == len(df), "empty filter must return all rows"

    print("OK - all assertions passed")
    print(f"  rows={len(df)}  revenue={rev:,.0f}  profit={prof:,.0f}  margin={mar:.1f}%  orders={orders}")


if __name__ == "__main__":
    run()
