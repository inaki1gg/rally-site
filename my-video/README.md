# rally-rank-post

RALLY rank-post reel — 1080×1920, 9:16, silent, ~13s. A single paused GSAP
timeline registered on `window.__timelines`, deterministic and seek-safe
(no `Date.now`, no `Math.random`, no `repeat: -1`).

> **File name note:** the composition is `index.html`. HyperFrames hard-requires
> the single root composition to be `index.html` (`check`/`render` discover
> `index.html` only, and two root compositions fail lint), so `rally-rank-post`
> lives in `index.html`. Its identity is carried by the project name, the header
> comment in `index.html`, and the output names below.

## Beats

1. **The excuses (0–5.5s)** — four quoted white lines appear ~1.1s apart and
   stack, each holding as the next arrives (built top-anchored so nothing
   reflows), then all four clear together.
2. **The turn (5.5–7s)** — one brand-weight line lands alone: *"Tu rating no
   escucha excusas."*
3. **The proof (7–11s)** — the glass rank cell builds in: CLASIFICACIÓN header +
   CLUB pill, rows cascade top-to-bottom, ratings count up as they settle, and
   the acid YOU-row lights and lifts. No caption.
4. **The end card (11–13s)** — `RALLY.` (RALL white, `Y.` acid with a soft
   bloom), *"El rating verificado del pádel."*, `rallyrating.app/apply`.
   Dead-still hold, hard cut to black.

## Locked identity

Acid `#CCFF00` is the only color; everything else is near-black `#0D0D0D` and
white `#F2F2F0`. Montserrat Black 900 / Bold, always razor-sharp and rendered
above the glow. Glass cell with a luminous acid border, soft halo, real
Z-depth, idle float and a slow sheen sweep. No sparkle/star motif.

## Assets & determinism

- Fonts are vendored locally (`fonts/montserrat-latin-{400,700,900}-normal.woff2`)
  and GSAP is vendored (`vendor/gsap.min.js`) — the render environment has no CDN
  access, so both are loaded from disk for a deterministic, offline render.

## Commands

```bash
npm run check                        # lint + runtime + layout + motion + contrast
npm run render                       # MP4 via hyperframes (renders/<name>.mp4)
```

## Outputs

- `renders/rally-rank-post.mp4` — final render (30fps, h264).
- `renders/rank-v2-stills/` — stills at 2s, 4s, 5s, 6.5s, 9s, 12.5s.
