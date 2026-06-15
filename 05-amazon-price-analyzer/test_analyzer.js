// Node smoke test for analyzer.js — run: node test_analyzer.js
const A = require("./analyzer.js");
let pass = 0, fail = 0;
function eq(label, got, want) {
  const ok = JSON.stringify(got) === JSON.stringify(want);
  if (ok) { pass++; } else { fail++; console.log(`FAIL ${label}: got ${JSON.stringify(got)} want ${JSON.stringify(want)}`); }
}
function approx(label, got, want, tol) {
  const ok = got != null && Math.abs(got - want) <= tol;
  if (ok) { pass++; } else { fail++; console.log(`FAIL ${label}: got ${got} want ~${want}`); }
}

// Price parsing across formats
eq("price es-ES decimal", A.parsePrice("39,99 €"), 39.99);
eq("price thousands", A.parsePrice("1.299,00 €"), 1299);
eq("price us format", A.parsePrice("$1,299.00"), 1299);
eq("price plain", A.parsePrice("49"), 49);
eq("price junk", A.parsePrice("Precio no disponible"), null);

// Rating parsing
eq("rating es", A.parseRating("4,5 de 5 estrellas"), 4.5);
eq("rating en", A.parseRating("4.3 out of 5 stars"), 4.3);
eq("rating oob", A.parseRating("9 de 5"), null);
eq("rating empty", A.parseRating(""), null);

// Reviews parsing
eq("reviews dot-thousands", A.parseReviews("12.480"), 12480);
eq("reviews with text", A.parseReviews("1.234 valoraciones"), 1234);
eq("reviews empty", A.parseReviews(""), null);

// End-to-end on the real sample file
const raw = require("./sample_data.json");
const items = raw.map(A.normalize);
const s = A.summarize(items);
eq("count", s.count, 12);
eq("withPrice", s.withPrice, 12);
approx("avgRating in range", s.avgRating, 4.3, 0.4);
eq("minPrice", s.minPrice, 12.49);
eq("maxPrice", s.maxPrice, 419);

const ranked = A.rankByValue(items);
eq("ranked length (all have price+rating)", ranked.length, 12);
// Best value should be a cheap, well-rated, high-review item — not the 419€ AirPods.
const top = ranked[0];
console.log(`  best value: ${top.name} (${top.priceRaw}, ${top.rating}*, ${top.reviews} reviews)`);
if (top.price > 100) { fail++; console.log("FAIL: top value item is expensive, ranking looks wrong"); } else pass++;

console.log(`\n${fail === 0 ? "OK" : "FAILED"} - ${pass} passed, ${fail} failed`);
process.exit(fail === 0 ? 0 : 1);
