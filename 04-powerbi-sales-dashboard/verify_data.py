# Confirms all CSVs exist and that every fact key resolves to a dimension.
import sys
from pathlib import Path
import pandas as pd

DATA_DIR = Path(__file__).parent / "data"
FILES = ["fact_sales.csv", "dim_date.csv", "dim_product.csv", "dim_customer.csv", "dim_store.csv"]


def main():
    # Existence + row counts.
    print("=== FILE EXISTENCE / ROW COUNTS ===")
    for f in FILES:
        p = DATA_DIR / f
        if not p.exists():
            print(f"MISSING: {f}")
            sys.exit(1)
        n = sum(1 for _ in open(p, encoding="utf-8")) - 1  # minus header
        print(f"OK  {f:20s} {n} rows")

    fact = pd.read_csv(DATA_DIR / "fact_sales.csv")
    dims = {
        "product_key": pd.read_csv(DATA_DIR / "dim_product.csv")["product_key"],
        "customer_key": pd.read_csv(DATA_DIR / "dim_customer.csv")["customer_key"],
        "store_key": pd.read_csv(DATA_DIR / "dim_store.csv")["store_key"],
        "date_key": pd.read_csv(DATA_DIR / "dim_date.csv")["date_key"],
    }

    # FK integrity: every fact key must exist in its dimension.
    print("\n=== FOREIGN KEY INTEGRITY ===")
    all_ok = True
    for key, dim_keys in dims.items():
        orphans = (~fact[key].isin(set(dim_keys))).sum()
        status = "OK" if orphans == 0 else "FAIL"
        if orphans != 0:
            all_ok = False
        print(f"{status}  fact.{key:13s} -> dim: {orphans} orphan rows")

    # Sanity: sales_amount == units * unit_price.
    calc_ok = (fact["sales_amount"] - (fact["units"] * fact["unit_price"]).round(2)).abs().max() < 0.01
    print(f"\n=== MEASURE SANITY ===")
    print(f"{'OK' if calc_ok else 'FAIL'}  sales_amount == units * unit_price")

    print(f"\nRESULT: {'ALL CHECKS PASSED' if all_ok and calc_ok else 'CHECKS FAILED'}")
    sys.exit(0 if all_ok and calc_ok else 1)


if __name__ == "__main__":
    main()
