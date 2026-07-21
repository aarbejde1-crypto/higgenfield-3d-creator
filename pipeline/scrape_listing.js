#!/usr/bin/env node
// Best-effort scraper for a single Airbnb listing page.
// Usage: node scrape_listing.js <airbnb-url> > listing.json
//
// Airbnb's headless-browser bot detection resets connections from
// Playwright/Chromium even though the same environment can plain-fetch the
// page fine, so this fetches the raw HTML and reads the page's own
// server-rendered state (the `data-deferred-state-0` script tag), rather
// than driving a browser. Airbnb has no public listing API and this JSON
// shape is unofficial/internal, so treat this as best-effort — it may need
// updating if Airbnb changes their PDP data structure.

const UA =
  'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36';

function findAll(obj, typename, out = []) {
  if (Array.isArray(obj)) {
    for (const v of obj) findAll(v, typename, out);
  } else if (obj && typeof obj === 'object') {
    if (obj.__typename === typename) out.push(obj);
    for (const v of Object.values(obj)) findAll(v, typename, out);
  }
  return out;
}

function metaContent(html, prop) {
  const re = new RegExp(
    `<meta[^>]+(?:property|name)=["']${prop}["'][^>]+content=["']([^"']*)["']`,
    'i'
  );
  const m = html.match(re);
  return m ? m[1].replace(/&amp;/g, '&') : null;
}

async function main() {
  const url = process.argv[2];
  if (!url) {
    console.error('Usage: node scrape_listing.js <airbnb-url>');
    process.exit(1);
  }

  const res = await fetch(url, {
    headers: {
      'User-Agent': UA,
      'Accept-Language': 'en-US,en;q=0.9',
    },
  });
  if (!res.ok) {
    console.error(`Fetch failed: HTTP ${res.status}`);
    process.exit(1);
  }
  const html = await res.text();

  const title = metaContent(html, 'og:title') || null;
  const description = metaContent(html, 'og:description') || null;
  const heroImage = metaContent(html, 'og:image') || null;

  const stateMatch = html.match(
    /<script id="data-deferred-state-0"[^>]*>([\s\S]*?)<\/script>/
  );

  let rooms = [];
  let guests = null;
  let fullDescription = null;

  if (stateMatch) {
    let state;
    try {
      state = JSON.parse(stateMatch[1]);
    } catch (e) {
      console.error('Warning: failed to parse deferred state JSON:', e.message);
    }
    if (state) {
      const stops = findAll(state, 'MediaTourStop');
      const byName = new Map();
      for (const stop of stops) {
        const name = stop.name;
        if (!name) continue;
        const items = stop.items || [];
        const photoUrls = items
          .map((it) => it.image && it.image.uri)
          .filter(Boolean);
        if (!photoUrls.length) continue;
        const existing = byName.get(name);
        if (!existing || photoUrls.length > existing.photoUrls.length) {
          byName.set(name, { name, photoUrls });
        }
      }
      rooms = Array.from(byName.values());

      const capacityMatches = findAll(state, 'PassportListingPdpSection');
      const capMatch = JSON.stringify(state).match(/"personCapacity":\s*(\d+)/);
      guests = capMatch ? capMatch[1] : null;

      const descMatches = findAll(state, 'ReadMoreHtml');
      if (descMatches.length && descMatches[0].htmlText) {
        fullDescription = descMatches[0].htmlText.replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
      }
    }
  }

  const allPhotos = Array.from(
    new Set(rooms.flatMap((r) => r.photoUrls))
  );

  console.log(
    JSON.stringify(
      {
        source_url: url,
        scraped_at: new Date().toISOString(),
        title,
        description,
        fullDescription,
        heroImage,
        guests,
        rooms,
        photos: allPhotos.length ? allPhotos : (heroImage ? [heroImage] : []),
      },
      null,
      2
    )
  );
}

main().catch((err) => {
  console.error('Scrape failed:', err.message);
  process.exit(1);
});
