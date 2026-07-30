import { chromium } from 'playwright';
import { readFile, writeFile, mkdir } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { FRAME, TYPE } from '../canon.ts';
import { buildHtml } from './rank-in-group.ts';

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, '../..');

const OUT = resolve(repoRoot, 'out/social/rally-2nd-of-8-1080x1920.png');
const MANIFEST = resolve(repoRoot, 'out/social/rally-2nd-of-8-1080x1920.json');

async function loadFonts(): Promise<Record<number, string>> {
  const entries = await Promise.all(
    Object.entries(TYPE.fontFiles).map(async ([weight, rel]) => {
      const buf = await readFile(resolve(here, '..', rel));
      return [Number(weight), buf.toString('base64')] as const;
    }),
  );
  return Object.fromEntries(entries);
}

/** Measured ink bounds of every visible element, in frame px. */
interface Measured {
  label: string;
  x: number;
  y: number;
  w: number;
  h: number;
}

async function main() {
  const fonts = await loadFonts();
  const html = buildHtml({ fonts });

  const browser = await chromium.launch();
  const page = await browser.newPage({
    viewport: { width: FRAME.width, height: FRAME.height },
    deviceScaleFactor: FRAME.scale,
  });

  await page.setContent(html, { waitUntil: 'load' });
  await page.evaluate(() => (document as any).fonts.ready);

  const measured: Measured[] = await page.evaluate(() => {
    const sel = '.wordmark, .statement, .hero-pos, .hero-of, .eyebrow, .standings, .payoff';
    return [...document.querySelectorAll(sel)].map((el) => {
      const r = el.getBoundingClientRect();
      return {
        label: el.className || el.tagName.toLowerCase(),
        x: Math.round(r.left),
        y: Math.round(r.top),
        w: Math.round(r.width),
        h: Math.round(r.height),
      };
    });
  });

  await mkdir(dirname(OUT), { recursive: true });
  await page.screenshot({ path: OUT, type: 'png' });
  await browser.close();

  const manifest = {
    file: OUT.replace(repoRoot + '/', ''),
    width: FRAME.width,
    height: FRAME.height,
    elements: measured,
  };
  await writeFile(MANIFEST, JSON.stringify(manifest, null, 2) + '\n');

  console.log(`rendered ${manifest.file}  ${FRAME.width}x${FRAME.height}`);
  for (const m of measured) {
    const right = FRAME.width - (m.x + m.w);
    const bottom = FRAME.height - (m.y + m.h);
    console.log(
      `  ${m.label.padEnd(12)} x=${String(m.x).padStart(4)} y=${String(m.y).padStart(4)} ` +
        `w=${String(m.w).padStart(4)} h=${String(m.h).padStart(4)}  ` +
        `gaps L${m.x} R${right} T${m.y} B${bottom}`,
    );
  }
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
