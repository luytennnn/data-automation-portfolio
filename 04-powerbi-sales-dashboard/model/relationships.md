# Star Schema — Relationships

A classic single-fact star schema: one central fact table surrounded by four
conformed dimensions. Every relationship is **one-to-many** from the dimension
(one) to the fact (many), with a **single** filter direction (dimension filters
fact). This is the recommended Power BI layout for performance and predictable
filtering.

## Diagram

```
                       +----------------+
                       |   dim_date     |
                       | PK date_key    |
                       +----------------+
                               | 1
                               |
                               | *
        +----------------+     v     +----------------+
        |  dim_product   |  +---------------------+   |  dim_customer  |
        | PK product_key |1*| fact_sales          |*1 | PK customer_key|
        +----------------+--| FK date_key         |---+----------------+
                            | FK product_key      |
                            | FK customer_key     |
                            | FK store_key        |
                            | units, unit_price,  |
                            | cost, sales_amount  |
                            +---------------------+
                               ^ *
                               |
                               | 1
                       +----------------+
                       |   dim_store    |
                       | PK store_key   |
                       +----------------+
```

## Relationship table

| From (one)      | Column        | To (many)            | Column        | Cardinality | Cross-filter | Active |
|-----------------|---------------|----------------------|---------------|-------------|--------------|--------|
| dim_date        | date_key      | fact_sales           | date_key      | 1 : *       | Single       | Yes    |
| dim_product     | product_key   | fact_sales           | product_key   | 1 : *       | Single       | Yes    |
| dim_customer    | customer_key  | fact_sales           | customer_key  | 1 : *       | Single       | Yes    |
| dim_store       | store_key     | fact_sales           | store_key     | 1 : *       | Single       | Yes    |

## Notes

- **Grain of `fact_sales`**: one row per sales line (`sale_id` is the unique key).
- **Date table**: `dim_date` covers the full 2024 calendar (366 rows, leap year)
  with no gaps, so it can be marked as the model's official date table.
- **No snowflaking**: `category`/`subcategory` and `city`/`region` live inside
  their dimension tables rather than separate sub-dimensions, keeping the schema
  flat and query-fast.
- **Single direction only**: avoids ambiguous filter paths and circular
  dependencies; if a many-to-many scenario ever appeared it would be modelled
  with a bridge table, not bidirectional cross-filtering.
