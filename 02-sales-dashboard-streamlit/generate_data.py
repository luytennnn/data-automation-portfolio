# Gera dataset sintetico de vendas e-commerce (seeded, reproduzivel)
import numpy as np
import pandas as pd
from pathlib import Path

# Seed fixa para reproducibilidade
SEED = 42
N_ROWS = 5000
YEAR = 2024

# Catalogo de produtos por categoria com preco base e custo base
PRODUCTS = {
    "Electronics": [
        ("Wireless Earbuds", 79.0, 38.0),
        ("Smartphone Case", 19.0, 6.0),
        ("USB-C Charger", 25.0, 9.0),
        ("Bluetooth Speaker", 59.0, 27.0),
        ("4K Webcam", 89.0, 44.0),
    ],
    "Home & Kitchen": [
        ("Coffee Maker", 119.0, 64.0),
        ("Air Fryer", 99.0, 52.0),
        ("Knife Set", 49.0, 21.0),
        ("Vacuum Cleaner", 199.0, 110.0),
    ],
    "Apparel": [
        ("Running Shoes", 89.0, 40.0),
        ("Cotton T-Shirt", 22.0, 7.0),
        ("Winter Jacket", 139.0, 70.0),
        ("Denim Jeans", 65.0, 28.0),
    ],
    "Sports": [
        ("Yoga Mat", 35.0, 14.0),
        ("Dumbbell Set", 79.0, 41.0),
        ("Water Bottle", 18.0, 5.0),
    ],
    "Beauty": [
        ("Face Serum", 45.0, 18.0),
        ("Hair Dryer", 69.0, 33.0),
        ("Lipstick Set", 29.0, 11.0),
    ],
}

REGIONS = ["North", "South", "East", "West", "Central"]
CHANNELS = ["Online", "Retail", "Marketplace"]

# Pesos sazonais por mes (pico em Nov/Dez por epoca festiva)
SEASONAL = np.array([0.8, 0.75, 0.9, 0.95, 1.0, 1.05, 1.0, 0.95, 1.0, 1.1, 1.4, 1.6])


def generate():
    rng = np.random.default_rng(SEED)

    # Achata catalogo em listas paralelas
    flat = [(cat, name, price, cost) for cat, items in PRODUCTS.items() for (name, price, cost) in items]
    cats = [r[0] for r in flat]
    names = [r[1] for r in flat]
    base_prices = np.array([r[2] for r in flat])
    base_costs = np.array([r[3] for r in flat])

    # Datas: amostra ponderada por sazonalidade ao longo de 2024
    start = np.datetime64(f"{YEAR}-01-01")
    days_in_year = 366  # 2024 e ano bissexto
    day_offsets = np.arange(days_in_year)
    months = (start + day_offsets.astype("timedelta64[D]")).astype("datetime64[M]").astype(int) % 12
    day_weights = SEASONAL[months]
    day_weights = day_weights / day_weights.sum()
    chosen_days = rng.choice(day_offsets, size=N_ROWS, p=day_weights)
    order_dates = start + chosen_days.astype("timedelta64[D]")

    # Produtos: alguns vendem mais que outros
    prod_pop = rng.dirichlet(np.ones(len(flat)) * 2.0)
    prod_idx = rng.choice(len(flat), size=N_ROWS, p=prod_pop)

    # Variacao de preco +/- 8% por encomenda (promos/descontos)
    price_jitter = rng.normal(1.0, 0.04, N_ROWS).clip(0.85, 1.15)
    unit_price = (base_prices[prod_idx] * price_jitter).round(2)
    unit_cost = base_costs[prod_idx].round(2)

    # Unidades: maioria 1-3, cauda ate ~8
    units = (rng.gamma(2.0, 1.1, N_ROWS).round().astype(int) + 1).clip(1, 8)

    # Regiao e canal com pesos realistas
    region = rng.choice(REGIONS, size=N_ROWS, p=[0.24, 0.21, 0.19, 0.20, 0.16])
    channel = rng.choice(CHANNELS, size=N_ROWS, p=[0.55, 0.25, 0.20])

    # Clientes: ~1200 unicos, alguns recorrentes
    customer_id = rng.integers(1000, 2200, size=N_ROWS)

    df = pd.DataFrame({
        "order_id": np.arange(100000, 100000 + N_ROWS),
        "order_date": pd.to_datetime(order_dates),
        "product": [names[i] for i in prod_idx],
        "category": [cats[i] for i in prod_idx],
        "region": region,
        "channel": channel,
        "units": units,
        "unit_price": unit_price,
        "cost": unit_cost,
        "customer_id": customer_id,
    })

    # Ordena por data para realismo
    df = df.sort_values("order_date").reset_index(drop=True)
    df["order_id"] = np.arange(100000, 100000 + len(df))
    return df


def main():
    out_dir = Path(__file__).parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "sales.csv"
    df = generate()
    df.to_csv(out_path, index=False)
    print(f"Wrote {len(df)} rows to {out_path}")
    print(df.head())


if __name__ == "__main__":
    main()
