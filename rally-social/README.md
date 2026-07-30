# rally-social

Node + TypeScript + Playwright harness for RALLY static social renders.

```bash
npm install          # playwright only; Chromium is already on the box
npm run build        # render, then static-check
```

Outputs land in `out/social/`.

## canon.ts

Single source of truth. Colours, typography, frame geometry, the acid budget,
and the rank fact all live there — templates read, never invent. Values are
lifted from the shipped product (`:root` and `.wordmark` in `index.html`, the
share-card surface in `profile.html`, the vendored Montserrat woff2 files),
so a render can't drift from the app.

`ROSTER.available` is `false`: there are no player names, ratings, or records
to draw on. Templates must redact. Inventing or placeholdering a name is a
hard failure, not a fallback — `rank-in-group.ts` throws if the flag ever
flips without the template being revisited.

## Rules the checker enforces

`src/check.ts` reads the exported PNG's pixels, not the source, so compliant-
looking markup can't fool it:

1. frame is exactly 1080×1920
2. field is `#0D0D0D`
3. no ink within 64px of any edge
4. acid `#CCFF00` forms **exactly two** clusters, each inside a region declared
   in `ACID_REGIONS` — the wordmark tail (identity) and the hero figure (the
   one fact). Everything else, including the standings surface, is white/grey.
5. no `#FF3B30` / `#FF4444` anywhere

## Posts

- `src/rank-in-group.ts` — 1080×1920. A global rank is meaningless; a rank
  inside the eight people you actually play is a fact.
