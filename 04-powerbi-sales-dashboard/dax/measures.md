# DAX Measure Library — Sales Analytics

All measures live in the `fact_sales` table. Paste each into Power BI Desktop
(Modeling > New Measure). They assume the star schema documented in
`../model/relationships.md` (date relationship on `date_key`).

> Note: the time-intelligence measures (`Sales YTD`, `Sales MTD`, `Sales PY`,
> `YoY %`, `Running Total`) require `dim_date` to be marked as a **Date table**
> in Power BI (Table tools > Mark as date table > `dim_date[date]`).

---

## Core measures

### Total Sales
Sum of all transaction sales amounts.
```dax
Total Sales = SUM ( fact_sales[sales_amount] )
```

### Total Cost
Total cost of goods sold (unit cost x units).
```dax
Total Cost = SUMX ( fact_sales, fact_sales[cost] * fact_sales[units] )
```

### Gross Profit
Sales minus cost — what is left before operating expenses.
```dax
Gross Profit = [Total Sales] - [Total Cost]
```

### Margin %
Gross profit as a share of sales; guarded against divide-by-zero.
```dax
Margin % = DIVIDE ( [Gross Profit], [Total Sales] )
```

### Total Units
Total quantity of items sold.
```dax
Total Units = SUM ( fact_sales[units] )
```

### Avg Order Value
Average sales amount per distinct transaction (order).
```dax
Avg Order Value = DIVIDE ( [Total Sales], DISTINCTCOUNT ( fact_sales[sale_id] ) )
```

### Sales per Customer
Average sales generated per distinct customer in the current filter context.
```dax
Sales per Customer = DIVIDE ( [Total Sales], DISTINCTCOUNT ( fact_sales[customer_key] ) )
```

---

## Time intelligence

### Sales YTD
Cumulative sales from the start of the year to the current date in context.
```dax
Sales YTD = TOTALYTD ( [Total Sales], dim_date[date] )
```

### Sales MTD
Cumulative sales from the start of the month to the current date in context.
```dax
Sales MTD = TOTALMTD ( [Total Sales], dim_date[date] )
```

### Sales PY
Same measure shifted back exactly one year (prior-year comparison baseline).
```dax
Sales PY = CALCULATE ( [Total Sales], SAMEPERIODLASTYEAR ( dim_date[date] ) )
```

### YoY %
Year-over-year growth: change versus the prior year as a percentage.
```dax
YoY % = DIVIDE ( [Total Sales] - [Sales PY], [Sales PY] )
```

### Running Total
Cumulative sales across all dates up to and including the current one.
```dax
Running Total =
CALCULATE (
    [Total Sales],
    FILTER (
        ALLSELECTED ( dim_date[date] ),
        dim_date[date] <= MAX ( dim_date[date] )
    )
)
```

---

## Ranking

### Top-N Product Rank
Ranks products by total sales (1 = best seller); used for Top-N visuals/filters.
```dax
Product Rank = RANKX ( ALL ( dim_product[product] ), [Total Sales], , DESC, DENSE )
```
