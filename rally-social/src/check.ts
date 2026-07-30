import { chromium } from 'playwright';
import { readFile } from 'node:fs/promises';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

import { ACID_REGIONS, COLOR, FORBIDDEN_COLORS, FRAME } from '../canon.ts';

/**
 * Static checker. Operates on the exported PNG's pixels — not the source —
 * so it cannot be fooled by markup that "looks" compliant.
 *
 *   1. frame is exactly 1080×1920
 *   2. field is #0D0D0D
 *   3. no ink within FRAME.edgeGuard (64px) of any edge
 *   4. acid #CCFF00 forms exactly two clusters, each inside a permitted region
 *   5. no forbidden red anywhere
 */

const here = dirname(fileURLToPath(import.meta.url));
const repoRoot = resolve(here, '../..');
/** Defaults to the canonical export; pass a path to audit any other frame. */
const TARGET = process.argv[2]
  ? resolve(process.cwd(), process.argv[2])
  : resolve(repoRoot, 'out/social/rally-2nd-of-8-1080x1920.png');

interface Report {
  width: number;
  height: number;
  fieldMismatch: number;
  edgeInk: { count: number; sample: [number, number, number, number, number][] };
  acidClusters: { x: number; y: number; w: number; h: number; px: number }[];
  forbidden: { hex: string; count: number }[];
}

function hexToRgb(hex: string): [number, number, number] {
  const h = hex.replace('#', '');
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}

async function analyse(): Promise<Report> {
  const png = await readFile(TARGET);
  const dataUri = `data:image/png;base64,${png.toString('base64')}`;

  const browser = await chromium.launch();
  const page = await browser.newPage();
  try {
    return await page.evaluate(
      async ({ dataUri, acid, field, forbidden, guard, mergeGap, tol }) => {
        const img = new Image();
        img.src = dataUri;
        await img.decode();

        const w = img.naturalWidth;
        const h = img.naturalHeight;
        const canvas = document.createElement('canvas');
        canvas.width = w;
        canvas.height = h;
        const ctx = canvas.getContext('2d', { willReadFrequently: true })!;
        ctx.drawImage(img, 0, 0);
        const { data } = ctx.getImageData(0, 0, w, h);

        const dist = (i: number, c: number[]) =>
          Math.abs(data[i] - c[0]) + Math.abs(data[i + 1] - c[1]) + Math.abs(data[i + 2] - c[2]);

        // ── field + edge guard ──
        let fieldMismatch = 0;
        const edgeSample: [number, number, number, number, number][] = [];
        let edgeInk = 0;

        for (let y = 0; y < h; y++) {
          for (let x = 0; x < w; x++) {
            const i = (y * w + x) * 4;
            const off = dist(i, field);
            if (off > tol) fieldMismatch++;
            const inGuard = x < guard || y < guard || x >= w - guard || y >= h - guard;
            if (inGuard && off > tol) {
              edgeInk++;
              if (edgeSample.length < 12)
                edgeSample.push([x, y, data[i], data[i + 1], data[i + 2]]);
            }
          }
        }

        // ── acid pixels ──
        const acidPx: [number, number][] = [];
        for (let y = 0; y < h; y++) {
          for (let x = 0; x < w; x++) {
            const i = (y * w + x) * 4;
            // strict: near-pure acid only, so antialiased edges of white type
            // against dark field can never be miscounted as acid.
            if (dist(i, acid) < 90 && data[i + 1] > 190 && data[i + 2] < 120) {
              acidPx.push([x, y]);
            }
          }
        }

        // cluster by proximity: glyphs of one word merge, separate roles do not
        const boxes: { x0: number; y0: number; x1: number; y1: number; px: number }[] = [];
        for (const [x, y] of acidPx) {
          let hit = null;
          for (const b of boxes) {
            if (
              x >= b.x0 - mergeGap &&
              x <= b.x1 + mergeGap &&
              y >= b.y0 - mergeGap &&
              y <= b.y1 + mergeGap
            ) {
              hit = b;
              break;
            }
          }
          if (hit) {
            hit.x0 = Math.min(hit.x0, x);
            hit.y0 = Math.min(hit.y0, y);
            hit.x1 = Math.max(hit.x1, x);
            hit.y1 = Math.max(hit.y1, y);
            hit.px++;
          } else {
            boxes.push({ x0: x, y0: y, x1: x, y1: y, px: 1 });
          }
        }
        // second pass: merge boxes that now overlap within the gap
        let merged = true;
        while (merged) {
          merged = false;
          outer: for (let a = 0; a < boxes.length; a++) {
            for (let b = a + 1; b < boxes.length; b++) {
              const A = boxes[a];
              const B = boxes[b];
              if (
                A.x0 - mergeGap <= B.x1 &&
                B.x0 - mergeGap <= A.x1 &&
                A.y0 - mergeGap <= B.y1 &&
                B.y0 - mergeGap <= A.y1
              ) {
                A.x0 = Math.min(A.x0, B.x0);
                A.y0 = Math.min(A.y0, B.y0);
                A.x1 = Math.max(A.x1, B.x1);
                A.y1 = Math.max(A.y1, B.y1);
                A.px += B.px;
                boxes.splice(b, 1);
                merged = true;
                break outer;
              }
            }
          }
        }

        // ── forbidden colours ──
        const forbiddenCounts = forbidden.map((f) => {
          let count = 0;
          for (let i = 0; i < data.length; i += 4) if (dist(i, f.rgb) < 60) count++;
          return { hex: f.hex, count };
        });

        return {
          width: w,
          height: h,
          fieldMismatch,
          edgeInk: { count: edgeInk, sample: edgeSample },
          acidClusters: boxes
            .filter((b) => b.px > 40) // ignore stray antialiasing specks
            .map((b) => ({ x: b.x0, y: b.y0, w: b.x1 - b.x0 + 1, h: b.y1 - b.y0 + 1, px: b.px }))
            .sort((a, b) => a.y - b.y),
          forbidden: forbiddenCounts,
        };
      },
      {
        dataUri,
        acid: hexToRgb(COLOR.acid),
        field: hexToRgb(COLOR.bg),
        forbidden: FORBIDDEN_COLORS.map((hex) => ({ hex, rgb: hexToRgb(hex) })),
        guard: FRAME.edgeGuard,
        mergeGap: 56,
        tol: 12,
      },
    );
  } finally {
    await browser.close();
  }
}

function contains(region: (typeof ACID_REGIONS)[number], c: { x: number; y: number; w: number; h: number }) {
  return (
    c.x >= region.x &&
    c.y >= region.y &&
    c.x + c.w <= region.x + region.w &&
    c.y + c.h <= region.y + region.h
  );
}

const failures: string[] = [];
const pass = (msg: string) => console.log(`  PASS  ${msg}`);
const fail = (msg: string) => {
  failures.push(msg);
  console.log(`  FAIL  ${msg}`);
};

const r = await analyse();
console.log(`\nstatic check — ${TARGET.replace(repoRoot + '/', '')}\n`);

// 1. dimensions
if (r.width === FRAME.width && r.height === FRAME.height)
  pass(`dimensions ${r.width}×${r.height}`);
else fail(`dimensions ${r.width}×${r.height}, expected ${FRAME.width}×${FRAME.height}`);

// 2. field
const inkRatio = r.fieldMismatch / (r.width * r.height);
pass(`field ${COLOR.bg}; ink covers ${(inkRatio * 100).toFixed(1)}% of the frame`);
if (inkRatio > 0.5) fail(`frame is ${(inkRatio * 100).toFixed(1)}% ink — negative space is gone`);

// 3. edge guard
if (r.edgeInk.count === 0) pass(`nothing within ${FRAME.edgeGuard}px of any edge`);
else
  fail(
    `${r.edgeInk.count} non-field px inside the ${FRAME.edgeGuard}px guard, ` +
      `e.g. ${r.edgeInk.sample.slice(0, 3).map(([x, y]) => `(${x},${y})`).join(' ')}`,
  );

// 4. acid budget
console.log(
  `  ....  acid clusters: ${r.acidClusters
    .map((c) => `[${c.x},${c.y} ${c.w}×${c.h} ${c.px}px]`)
    .join(' ')}`,
);
if (r.acidClusters.length === 2) pass('acid appears in exactly 2 places');
else fail(`acid appears in ${r.acidClusters.length} places, expected exactly 2`);

for (const c of r.acidClusters) {
  const region = ACID_REGIONS.find((reg) => contains(reg, c));
  if (region) pass(`acid cluster at (${c.x},${c.y}) is the permitted "${region.name}"`);
  else fail(`acid cluster at (${c.x},${c.y}) ${c.w}×${c.h} is outside every permitted region`);
}

// 5. forbidden colours
for (const f of r.forbidden) {
  if (f.count === 0) pass(`no ${f.hex}`);
  else fail(`${f.count} px of forbidden ${f.hex}`);
}

console.log('');
if (failures.length) {
  console.error(`FAILED — ${failures.length} problem(s)\n`);
  process.exit(1);
}
console.log('OK — frame is canon-clean\n');
