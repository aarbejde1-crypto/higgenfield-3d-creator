#!/usr/bin/env node
// Best-effort scraper for a single Airbnb listing page.
// Usage: node scrape_listing.js <airbnb-url> > listing.json
//
// Airbnb is a JS-heavy SPA with no public listing API, so this reads
// whatever is present in the rendered DOM + meta tags. Selectors may need
// updating if Airbnb changes its markup — treat this as best-effort, not
// a stable integration.

const { chromium } = require('playwright-core');

const CHROME_PATH = '/opt/pw-browsers/chromium-1194/chrome-linux/chrome';

async function main() {
  const url = process.argv[2];
  if (!url) {
    console.error('Usage: node scrape_listing.js <airbnb-url>');
    process.exit(1);
  }

  const browser = await chromium.launch({
    executablePath: CHROME_PATH,
    args: ['--no-sandbox'],
  });
  const page = await browser.newPage({
    userAgent:
      'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    viewport: { width: 1400, height: 1000 },
  });

  await page.goto(url, { waitUntil: 'domcontentloaded', timeout: 45000 });
  await page.waitForTimeout(3000);

  const data = await page.evaluate(() => {
    const meta = (name) =>
      document.querySelector(`meta[property="${name}"], meta[name="${name}"]`)
        ?.content || null;

    const title = meta('og:title') || document.title || null;
    const description = meta('og:description') || null;
    const heroImage = meta('og:image') || null;

    // Collect candidate photo URLs from Airbnb's media CDN, de-duplicated
    // and stripped of size-limiting query params to prefer full-res.
    const imgs = Array.from(document.querySelectorAll('img'))
      .map((img) => img.currentSrc || img.src)
      .filter((src) => src && src.includes('muscache.com'));
    const uniquePhotos = Array.from(new Set(imgs));

    const bodyText = document.body.innerText || '';
    const grab = (re) => {
      const m = bodyText.match(re);
      return m ? m[0] : null;
    };

    return {
      title,
      description,
      heroImage,
      photos: uniquePhotos,
      rating: grab(/[0-5]\.\d{1,2}(?=\s*(?:·|\(|$|\s*rating))/i),
      bedrooms: grab(/\d+\s+bedrooms?/i),
      beds: grab(/\d+\s+beds?/i),
      baths: grab(/\d+(\.\d+)?\s+baths?/i),
      guests: grab(/\d+\s+guests?/i),
      pageText: bodyText.slice(0, 4000),
    };
  });

  await browser.close();

  console.log(
    JSON.stringify(
      {
        source_url: url,
        scraped_at: new Date().toISOString(),
        ...data,
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
