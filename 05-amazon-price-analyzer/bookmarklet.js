// SmartShop — readable source of the browser bookmarklet (companion to index.html).
// To install: minify this into a single line, prefix with "javascript:" and save as a bookmark.
// Use it on an Amazon.es product page OR a search-results page; it copies a JSON array to your
// clipboard. Then paste that JSON into index.html ("Analyze"). All fetches are same-origin and
// throttled (max 16 products, 400 ms apart) so it stays polite — for personal research only.
(async () => {
  const T = e => e ? (e.innerText || e.textContent).trim().replace(/\s+/g, " ") : "";
  const DET_IDS = ["feature-bullets","productOverview_feature_div","detailBullets_feature_div",
    "prodDetails","productDescription","important-information","techSpec_section_1","tech"];
  const detsOf = doc => DET_IDS.map(id => T(doc.getElementById(id))).filter(Boolean).join(" | ").slice(0, 4000);
  const items = [];

  if (document.getElementById("productTitle")) {
    // PRODUCT PAGE MODE — scrape the single product.
    const name = T(document.getElementById("productTitle"));
    const pr = document.querySelector("#corePriceDisplay_desktop_feature_div .a-price .a-offscreen, #corePrice_feature_div .a-price .a-offscreen, .a-price .a-offscreen")?.textContent?.trim() || "";
    const ra = document.querySelector("#acrPopover")?.getAttribute("title") || T(document.querySelector("#acrPopover .a-icon-alt")) || "";
    const rv = T(document.getElementById("acrCustomerReviewText"));
    const m = location.pathname.match(/\/dp\/([A-Z0-9]{10})/);
    if (name) items.push({ name, price: pr, rating: ra, reviews: rv, details: detsOf(document),
      url: m ? "https://www.amazon.es/dp/" + m[1] : location.href.split("?")[0] });
  } else {
    // SEARCH RESULTS MODE — scrape each card, then enrich the first 16 with their detail pages.
    let els = [...document.querySelectorAll('div[data-component-type="s-search-result"]')];
    if (!els.length) els = [...document.querySelectorAll('div[data-asin]:not([data-asin=""])')];
    const seen = new Set();
    for (const e of els) {
      const asin = e.dataset.asin;
      if (!asin || seen.has(asin)) continue;
      const t = e.querySelector("h2 span, h2")?.innerText?.trim().replace(/\s+/g, " ");
      const pr = e.querySelector(".a-price .a-offscreen")?.textContent?.trim();
      if (!t || !pr) continue;
      seen.add(asin);
      const ra = e.querySelector(".a-icon-alt")?.textContent?.trim() || "";
      let rv = "";
      const rvEl = e.querySelector('a[href*="customerReviews"]') || e.querySelector("span.a-size-base.s-underline-text");
      if (rvEl) rv = rvEl.innerText.trim();
      if (!rv) {
        const al = e.querySelector('a[aria-label*="classifica"],a[aria-label*="valorac"],a[aria-label*="rating"]');
        if (al) rv = al.getAttribute("aria-label") || "";
      }
      items.push({ name: t, price: pr, rating: ra, reviews: rv, url: "https://www.amazon.es/dp/" + asin });
    }
    if (items.length) {
      const MAX = Math.min(items.length, 16);
      const ov = document.createElement("div");
      ov.style.cssText = "position:fixed;top:12px;left:50%;transform:translateX(-50%);z-index:99999;background:#0f1419;color:#4fc3f7;padding:10px 22px;border-radius:10px;font:14px sans-serif;box-shadow:0 4px 18px rgba(0,0,0,.4)";
      document.body.appendChild(ov);
      const parser = new DOMParser();
      for (let i = 0; i < MAX; i++) {
        ov.textContent = "SmartShop: fetching details " + (i + 1) + "/" + MAX + "... (don't close the page)";
        try {
          const r = await fetch(items[i].url, { credentials: "same-origin" });
          if (r.ok) {
            const doc = parser.parseFromString(await r.text(), "text/html");
            const det = detsOf(doc);
            if (det) items[i].details = det;
          }
        } catch (err) {}
        await new Promise(res => setTimeout(res, 400)); // polite throttle
      }
      ov.remove();
    }
  }

  if (!items.length) { alert("SmartShop: no products found. Use it on an Amazon.es results or product page."); return; }
  const nDet = items.filter(x => x.details).length;
  const j = JSON.stringify(items);
  const done = () => alert("SmartShop: " + items.length + " product(s) copied, " + nDet + " with full details! Paste into the tool (Ctrl+V).");
  if (navigator.clipboard && navigator.clipboard.writeText) {
    navigator.clipboard.writeText(j).then(done).catch(() => prompt("Copy manually:", j));
  } else prompt("Copy manually:", j);
})();
