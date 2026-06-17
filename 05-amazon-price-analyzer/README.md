# Amazon Price & Competitor Analyzer

> Scrape an Amazon search/product page with a one-click bookmarklet, then turn the data into
> an instant price-vs-rating dashboard — entirely in the browser, no install, no server.

A two-part **web-scraping → structured data → dashboard** automation, the classic Data
Automation consulting workflow:

1. **`SmartShop` bookmarklet** (`bookmarklet.js`) — runs on Amazon.es. On a product page it
   grabs one product; on a results page it scrapes every card and then **auto-fetches the first
   16 product pages** (same-origin, throttled 400 ms) to enrich each with full details, showing
   a progress overlay. Copies a clean JSON array to the clipboard.
2. **Analyzer tool** (`index.html`) — paste that JSON (or load the sample) and get KPI cards,
   a price-vs-rating bubble chart (bubble size = review count), a "best value" ranking, and a
   sortable, filterable product table. Pure vanilla JS + `<canvas>` — opens offline, zero deps.

## What it answers
- Which product is the **best value** (rating weighted by review confidence, divided by price)?
- How do competitors cluster on **price vs. rating**? Who is overpriced for their rating?
- What is the price range, average price and average rating across the listing?

## Stack
JavaScript (vanilla) · HTML/CSS · Canvas · clipboard/`fetch`/`DOMParser` (bookmarklet) ·
Node.js (tests). No build step, no frameworks, no network calls in the analyzer.

## How to run
```powershell
# Open the dashboard (from inside this folder so it can load the sample):
start index.html        # then click "Load sample data"
# Verify the analysis logic:
node test_analyzer.js   # 19 assertions
```
To use real data: install `bookmarklet.js` as a browser bookmark (minify to one line, prefix
`javascript:`), run it on Amazon.es, then paste the copied JSON into the page and click **Analyze**.

## JSON contract (bookmarklet → tool)
```json
[{ "name": "...", "price": "39,99 €", "rating": "4,5 de 5 estrellas",
   "reviews": "1.234", "url": "https://www.amazon.es/dp/ASIN", "details": "..." }]
```
The analyzer parses messy real-world formats: es-ES prices (`1.299,00 €`), US prices
(`$1,299.00`), ratings in several locales, and thousands-separated review counts.

## Notes
- `sample_data.json` is **synthetic** demo data (headphones category) for showcasing the tool.
- Selectors target Amazon's DOM, which changes often — hence the bookmarklet is versioned.
- Intended for **personal product research**; the bookmarklet caps at 16 products and throttles
  requests to stay polite. Not for bulk/commercial scraping.

---
*Part of the Data Automation & Dashboard portfolio —  · franciscodias942@gmail.com*
