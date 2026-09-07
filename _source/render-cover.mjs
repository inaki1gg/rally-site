/*
  Renders _source/cover.html to /assets/og/rally-cover.png at exactly 1200x630.

      node _source/render-cover.mjs

  The PNG is committed; this script exists so the cover is reproducible rather
  than a file nobody can regenerate. Edit cover.html, re-run, commit both.

  The page is served over http rather than opened as file://, because Chromium
  applies CORS to file:// font requests and the woff2 faces would silently fall
  back to Helvetica — which would ship a cover in the wrong typeface without
  failing. The gate at the bottom catches that anyway.
*/
import { createRequire } from 'node:module';
import { execSync } from 'node:child_process';
import { createServer } from 'node:http';
import { readFile } from 'node:fs/promises';
import { extname, join, normalize } from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const ROOT = fileURLToPath(new URL('..', import.meta.url));
const OUT = join(ROOT, 'assets/og/rally-cover.png');

// playwright lives in the global prefix in CI images; fall back to it if the
// repo has no local node_modules (it has none — this is a static site).
function loadPlaywright() {
  try { return require('playwright'); }
  catch { return require(join(execSync('npm root -g').toString().trim(), 'playwright')); }
}

const TYPES = { '.html': 'text/html; charset=utf-8', '.woff2': 'font/woff2',
                '.css': 'text/css; charset=utf-8', '.png': 'image/png', '.jpg': 'image/jpeg' };

const server = createServer(async (req, res) => {
  const path = normalize(decodeURIComponent(req.url.split('?')[0])).replace(/^(\.\.[/\\])+/, '');
  try {
    const body = await readFile(join(ROOT, path));
    res.writeHead(200, { 'Content-Type': TYPES[extname(path)] ?? 'application/octet-stream' });
    res.end(body);
  } catch {
    res.writeHead(404).end('not found');
  }
});

await new Promise((r) => server.listen(0, '127.0.0.1', r));
const origin = `http://127.0.0.1:${server.address().port}`;

const { chromium } = loadPlaywright();
const browser = await chromium.launch();
const page = await browser.newPage({
  viewport: { width: 1200, height: 630 },
  deviceScaleFactor: 1,           // declared og:image:width must equal real pixels
});

await page.goto(`${origin}/_source/cover.html`, { waitUntil: 'networkidle' });
await page.evaluate(() => document.fonts.ready);

// Gates. A cover that overflows or renders in the wrong face must fail loudly,
// not ship: nobody re-reads a share card before a launch.
const report = await page.evaluate(() => {
  const inset = 64, W = 1200, H = 630;
  const box = (sel) => { const r = document.querySelector(sel).getBoundingClientRect();
                         return { l: +r.left.toFixed(1), r: +r.right.toFixed(1),
                                  t: +r.top.toFixed(1), b: +r.bottom.toFixed(1) }; };
  // .tier is display:block, so its own box is always the full column. Measure the
  // glyphs with a Range or the overflow gate below can never fail.
  const tiers = [...document.querySelectorAll('.tier')].map((el) => {
    const range = document.createRange();
    range.selectNodeContents(el);
    const r = range.getBoundingClientRect();
    return { text: el.textContent, left: +r.left.toFixed(1), right: +r.right.toFixed(1),
             width: +r.width.toFixed(1) };
  });
  return {
    face: getComputedStyle(document.querySelector('.tier')).fontFamily.split(',')[0],
    montserratLoaded: document.fonts.check('900 112px Montserrat'),
    tiers,
    stage: box('.stage'),
    en: box('.en'),
    wm: box('.wm'),
    limits: { inset, W, H },
  };
});

const fail = [];
if (!report.montserratLoaded) fail.push('Montserrat 900 did not load — the cover would ship in a fallback face');
for (const t of report.tiers) {
  if (t.right > 1200 - 64) fail.push(`tier overflows the 64px inset: "${t.text}" ends at ${t.right}`);
}
if (report.stage.t < 24) fail.push(`statement block is too high: top ${report.stage.t}`);
if (report.en.b > report.wm.t) fail.push(`the EN line collides with the wordmark (${report.en.b} > ${report.wm.t})`);

console.log(JSON.stringify(report, null, 2));
if (fail.length) { console.error('\nFAILED:\n- ' + fail.join('\n- ')); await browser.close(); server.close(); process.exit(1); }

await page.screenshot({ path: OUT, type: 'png' });
await browser.close();
server.close();
console.log(`\nwrote ${OUT}`);
