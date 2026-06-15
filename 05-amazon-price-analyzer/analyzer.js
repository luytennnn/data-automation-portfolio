// Pure analysis logic for the SmartShop JSON — no DOM, so it runs in the browser AND in Node tests.

// Parse a European/Amazon price string ("1.299,00 €", "39,99 €", "€12.34") to a number, or null.
function parsePrice(raw) {
  if (raw == null) return null;
  let s = String(raw).replace(/[^\d.,]/g, ""); // keep digits, comma, dot
  if (!s) return null;
  const hasComma = s.includes(","), hasDot = s.includes(".");
  if (hasComma && hasDot) {
    // The last separator is the decimal one (handles "1.299,00" and "1,299.00").
    if (s.lastIndexOf(",") > s.lastIndexOf(".")) s = s.replace(/\./g, "").replace(",", ".");
    else s = s.replace(/,/g, "");
  } else if (hasComma) {
    s = s.replace(",", "."); // comma is the decimal separator (es-ES)
  }
  const n = parseFloat(s);
  return isFinite(n) ? n : null;
}

// Parse a rating ("4,5 de 5 estrellas", "4.5 out of 5") to a 0-5 number, or null.
function parseRating(raw) {
  if (raw == null) return null;
  const m = String(raw).replace(",", ".").match(/(\d+(?:\.\d+)?)/);
  if (!m) return null;
  const n = parseFloat(m[1]);
  return n >= 0 && n <= 5 ? n : null;
}

// Parse a reviews count ("2.145", "1,234 valoraciones", "1234 ratings") to an int, or null.
function parseReviews(raw) {
  if (raw == null) return null;
  const digits = String(raw).replace(/[.,\s]/g, "").match(/\d+/); // thousands sep stripped
  return digits ? parseInt(digits[0], 10) : null;
}

// Normalize one raw SmartShop item into typed fields.
function normalize(item) {
  return {
    name: (item.name || "").trim(),
    price: parsePrice(item.price),
    rating: parseRating(item.rating),
    reviews: parseReviews(item.reviews),
    url: item.url || "",
    details: item.details || "",
    priceRaw: item.price || "",
  };
}

// Compute summary KPIs over normalized items.
function summarize(items) {
  const prices = items.map(i => i.price).filter(p => p != null);
  const ratings = items.map(i => i.rating).filter(r => r != null);
  const avg = a => a.length ? a.reduce((x, y) => x + y, 0) / a.length : null;
  return {
    count: items.length,
    withPrice: prices.length,
    avgPrice: avg(prices),
    minPrice: prices.length ? Math.min(...prices) : null,
    maxPrice: prices.length ? Math.max(...prices) : null,
    avgRating: avg(ratings),
  };
}

// Value score = rating weighted by review confidence, penalized by price.
// Higher = better deal. Items without price or rating are excluded from ranking.
function rankByValue(items) {
  const scored = items
    .filter(i => i.price != null && i.price > 0 && i.rating != null)
    .map(i => {
      const confidence = Math.log10((i.reviews || 0) + 10); // dampen low-review items
      const score = (i.rating * confidence) / i.price;
      return Object.assign({}, i, { value: score });
    });
  scored.sort((a, b) => b.value - a.value);
  return scored;
}

// Export for Node tests; harmless in the browser.
if (typeof module !== "undefined" && module.exports) {
  module.exports = { parsePrice, parseRating, parseReviews, normalize, summarize, rankByValue };
}
