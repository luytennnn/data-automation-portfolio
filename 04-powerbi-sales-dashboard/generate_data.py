# Generates a synthetic retail sales star schema as reproducible CSVs.
import numpy as np
import pandas as pd
from pathlib import Path

# Fixed seed so the dataset is identical on every run.
SEED = 42
N_FACT = 8000
rng = np.random.default_rng(SEED)

DATA_DIR = Path(__file__).parent / "data"
DATA_DIR.mkdir(exist_ok=True)


def build_dim_date():
    # Full 2024 calendar, one row per day, surrogate key as yyyymmdd int.
    dates = pd.date_range("2024-01-01", "2024-12-31", freq="D")
    df = pd.DataFrame({"date": dates})
    df["date_key"] = df["date"].dt.strftime("%Y%m%d").astype(int)
    df["year"] = df["date"].dt.year
    df["quarter"] = "Q" + df["date"].dt.quarter.astype(str)
    df["month"] = df["date"].dt.month
    df["month_name"] = df["date"].dt.strftime("%B")
    df["week"] = df["date"].dt.isocalendar().week.astype(int)
    df["day_name"] = df["date"].dt.strftime("%A")
    df["date"] = df["date"].dt.strftime("%Y-%m-%d")
    return df[["date_key", "date", "year", "quarter", "month", "month_name", "week", "day_name"]]


def build_dim_product():
    # Small product catalogue across 3 categories.
    catalogue = {
        "Electronics": ["Phones", "Laptops", "Audio"],
        "Home": ["Kitchen", "Furniture", "Decor"],
        "Apparel": ["Men", "Women", "Kids"],
    }
    rows = []
    pk = 1
    for category, subcats in catalogue.items():
        for sub in subcats:
            for i in range(1, 6):  # 5 products per subcategory
                rows.append({
                    "product_key": pk,
                    "product": f"{sub} Item {i}",
                    "category": category,
                    "subcategory": sub,
                })
                pk += 1
    return pd.DataFrame(rows)


def build_dim_customer(n=400):
    # Synthetic customers tagged with a segment and region.
    segments = ["Consumer", "Corporate", "Home Office"]
    regions = ["North", "South", "East", "West"]
    return pd.DataFrame({
        "customer_key": np.arange(1, n + 1),
        "customer": [f"Customer {i:04d}" for i in range(1, n + 1)],
        "segment": rng.choice(segments, n),
        "region": rng.choice(regions, n),
    })


def build_dim_store():
    # Eight physical stores across cities/regions.
    stores = [
        ("Lisbon Central", "Lisbon", "South"),
        ("Porto Riverside", "Porto", "North"),
        ("Braga Plaza", "Braga", "North"),
        ("Faro Marina", "Faro", "South"),
        ("Coimbra Hill", "Coimbra", "East"),
        ("Aveiro Bay", "Aveiro", "West"),
        ("Setubal Port", "Setubal", "South"),
        ("Evora Old Town", "Evora", "East"),
    ]
    return pd.DataFrame({
        "store_key": np.arange(1, len(stores) + 1),
        "store": [s[0] for s in stores],
        "city": [s[1] for s in stores],
        "region": [s[2] for s in stores],
    })


def build_fact(dim_date, dim_product, dim_customer, dim_store):
    # Random transactions referencing valid surrogate keys only.
    date_keys = dim_date["date_key"].to_numpy()
    product_keys = dim_product["product_key"].to_numpy()
    customer_keys = dim_customer["customer_key"].to_numpy()
    store_keys = dim_store["store_key"].to_numpy()

    df = pd.DataFrame({
        "date_key": rng.choice(date_keys, N_FACT),
        "product_key": rng.choice(product_keys, N_FACT),
        "customer_key": rng.choice(customer_keys, N_FACT),
        "store_key": rng.choice(store_keys, N_FACT),
        "units": rng.integers(1, 11, N_FACT),
    })
    # Price between 5 and 500; cost is 55-85% of price (random margin).
    unit_price = np.round(rng.uniform(5, 500, N_FACT), 2)
    cost_ratio = rng.uniform(0.55, 0.85, N_FACT)
    df["unit_price"] = unit_price
    df["cost"] = np.round(unit_price * cost_ratio, 2)
    df["sales_amount"] = np.round(df["units"] * df["unit_price"], 2)
    df.insert(0, "sale_id", np.arange(1, N_FACT + 1))
    return df


def main():
    dim_date = build_dim_date()
    dim_product = build_dim_product()
    dim_customer = build_dim_customer()
    dim_store = build_dim_store()
    fact = build_fact(dim_date, dim_product, dim_customer, dim_store)

    outputs = {
        "dim_date.csv": dim_date,
        "dim_product.csv": dim_product,
        "dim_customer.csv": dim_customer,
        "dim_store.csv": dim_store,
        "fact_sales.csv": fact,
    }
    for name, df in outputs.items():
        df.to_csv(DATA_DIR / name, index=False)
        print(f"wrote {name}: {len(df)} rows")


if __name__ == "__main__":
    main()
