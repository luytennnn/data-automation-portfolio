"""Generate a synthetic e-commerce sales dataset for the report generator demo."""
import logging
from pathlib import Path

import numpy as np
import pandas as pd

# Output path for the raw dataset
OUTPUT_CSV = Path(__file__).parent / "data" / "raw_sales.csv"
N_ROWS = 4000
SEED = 42

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger("generate_data")

# Product catalogue: (product, category, base_price, base_cost)
CATALOGUE = [
    ("Wireless Mouse", "Electronics", 25.0, 11.0),
    ("Mechanical Keyboard", "Electronics", 79.0, 38.0),
    ("USB-C Hub", "Electronics", 45.0, 19.0),
    ("Noise-Cancel Headphones", "Electronics", 149.0, 70.0),
    ("4K Webcam", "Electronics", 89.0, 41.0),
    ("Cotton T-Shirt", "Apparel", 19.0, 6.0),
    ("Running Shoes", "Apparel", 95.0, 42.0),
    ("Denim Jacket", "Apparel", 120.0, 55.0),
    ("Wool Beanie", "Apparel", 22.0, 7.0),
    ("Ceramic Mug", "Home", 14.0, 4.0),
    ("Scented Candle", "Home", 18.0, 6.0),
    ("Throw Blanket", "Home", 49.0, 20.0),
    ("Desk Lamp", "Home", 39.0, 16.0),
    ("Protein Powder", "Health", 55.0, 24.0),
    ("Yoga Mat", "Health", 35.0, 13.0),
    ("Water Bottle", "Health", 20.0, 7.0),
]
REGIONS = ["North", "South", "East", "West", "Central"]


def main():
    rng = np.random.default_rng(SEED)
    np.random.seed(SEED)

    # Spread orders across all of 2024 with a slight Q4 uplift
    start = pd.Timestamp("2024-01-01")
    day_offsets = rng.integers(0, 366, size=N_ROWS)
    dates = start + pd.to_timedelta(day_offsets, unit="D")

    # Pick products and derive plausible prices/costs with small noise
    idx = rng.integers(0, len(CATALOGUE), size=N_ROWS)
    products = [CATALOGUE[i][0] for i in idx]
    categories = [CATALOGUE[i][1] for i in idx]
    base_price = np.array([CATALOGUE[i][2] for i in idx])
    base_cost = np.array([CATALOGUE[i][3] for i in idx])

    price_noise = rng.normal(1.0, 0.05, size=N_ROWS).clip(0.85, 1.2)
    unit_price = (base_price * price_noise).round(2)
    unit_cost = (base_cost * rng.normal(1.0, 0.04, size=N_ROWS).clip(0.85, 1.2)).round(2)

    # Units skewed toward small basket sizes
    units = rng.integers(1, 9, size=N_ROWS)

    df = pd.DataFrame({
        "order_id": [f"ORD-{100000 + i}" for i in range(N_ROWS)],
        "order_date": dates.strftime("%Y-%m-%d"),
        "product": products,
        "category": categories,
        "region": rng.choice(REGIONS, size=N_ROWS),
        "units": units,
        "unit_price": unit_price,
        "cost": unit_cost,
    })

    # Inject a few intentional messy rows so the cleaning step has work to do
    df.loc[10, "units"] = np.nan          # null unit count
    df.loc[250, "unit_price"] = np.nan    # null price
    df.loc[777, "region"] = np.nan        # null region
    dupe = df.loc[[500]].copy()           # exact duplicate row
    df = pd.concat([df, dupe], ignore_index=True)

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_CSV, index=False)
    log.info("Wrote %d rows (incl. 1 duplicate, 3 nulls) to %s", len(df), OUTPUT_CSV)


if __name__ == "__main__":
    main()
