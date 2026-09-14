/*
 * Photograph the editor for the hero section of the landing pages.
 *
 *   node tools/make-hero.js            (needs Playwright and a local server)
 *
 * Writes assets/hero-en.png and assets/hero-de.png. Run it again whenever the
 * editor's interface changes, otherwise the landing page shows an old version
 * of the product — which is the one thing a hero image must not do.
 *
 * Start the server first:  python3 tools/serve.py 8767
 */
const { chromium } = require(process.env.PLAYWRIGHT ||
  '/opt/node22/lib/node_modules/playwright');

const BASE = process.env.BASE || "http://localhost:8767";
const OUT = require('path').join(__dirname, '..', 'assets');

(async () => {
  const browser = await chromium.launch();
  for (const [lang, file] of [['en', 'hero-en.png'], ['de', 'hero-de.png']]) {
    const ctx = await browser.newContext({
      viewport: { width: 1500, height: 940 },
      deviceScaleFactor: 2,
    });
    const page = await ctx.newPage();
    await page.goto(`${BASE}/editor.html?lang=${lang}`, { waitUntil: 'networkidle' });
    await page.waitForTimeout(1400);
    await page.evaluate(() => {
      // The transient notices and the drag handles are not part of the product.
      const hint = document.getElementById('hint');
      if (hint) hint.style.display = 'none';
      document.body.style.background = '#eceae8';
    });
    await page.waitForTimeout(500);
    await page.screenshot({ path: require('path').join(OUT, file) });
    console.log('wrote assets/' + file);
    await ctx.close();
  }
  await browser.close();
})();
