# RALLY — "Brand New Game" seamless swipe carousel

A 5-slide Instagram teaser in the style of the seamless "web across the swipe"
reveal format: a gloved hand releases a white cord on slide 1, the cord
travels across the black slides, frays into a net, and the net catches a
phone running the RALLY home screen. Slide 5 is the CTA.

All five slides are exact 1080×1350 cuts of one continuous 5400×1350
panorama, so the cord lines up edge-to-edge on every swipe.

## Slides

| # | Content | Final JPEG (1080×1350) |
|---|---------|------------------------|
| 1 | Suit-glove hand shooting the cord from its palm, lockup, SWIPE | https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/c4558940-033d-459f-92a2-fbaec1e9b83a.jpg |
| 2 | Taut cord across black | https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/db975ab6-31b8-4eb2-adb7-1f628fa27b6e.jpg |
| 3 | Cord frays into net | https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/f641c4f1-5ba5-44f9-90ec-7c6b3026c518.jpg |
| 4 | Net catches the phone (RALLY home) | https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/96d4007b-4148-4cee-98d2-5f69e363d1f3.jpg |
| 5 | BRAND NEW GAME. + Founding 100 CTA | https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/ee7fb76c-7189-4c65-a6de-d40388515334.jpg |

Full panorama (5400×1350):
https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/eb851e4f-45fa-4eb7-b583-2b0a979eaa03.jpg

Contact sheet:
https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/530d702e-3814-476e-b682-cd5c424358dd.jpg

![carousel preview](./carousel_preview.jpg)

## Caption (Spanish-primary, brand voice)

> Un juego nuevo. Founding 100 · Madrid — solicita acceso en la bio.
> A brand new game. Founding 100 · Madrid — apply via the link in bio.

Alt (net wordplay):

> Todo lo que cae en la red queda registrado.
> Whatever lands in the net gets recorded.

No emojis. Post order: slides 1→5, 4:5 portrait.

## Hashtags + discovery

Instagram capped hashtags at **5 per post** (announced Dec 2025), and Mosseri
has repeatedly said tags don't drive reach — they label the post so it can be
matched to searches. Put all five in the caption, not the first comment: it is
unpublished whether comment tags count against the cap, so don't split them.

```
#padel #padelmadrid #padelespaña #padeleros #rallyrating
```

Verify each in-app before posting (search it; if it returns nothing or a
warning, it's restricted). Swap pool for later posts so the set isn't
identical every time: `#padelamateur`, `#ligaspadelmadrid`, `#nivelpadel`,
`#torneopadel`, `#padelclub`.

Avoid: `#worldpadeltour` (tour absorbed into Premier Padel, tag is a relic),
the generic filler every hashtag tool outputs (`#padeltime`, `#padelmania`,
`#instapadel`, `#padeladdict`), `#paddle` (collides with paddleboarding and
pickleball), and `#tenis`/`#tennis` (wrong sport — miscategorises the post).

Accents: Instagram does NOT merge `#padel` and `#pádel` — they are separate
tags. Use the unaccented `#padel` as the tag (matches what people type and
carries the international volume), but always write `pádel` **with the tilde
in caption prose** — a Madrid reader reads a missing tilde as a badly
localised foreign app, which is the opposite of the brand position.

Higher-leverage than any of the above:
- Keyword-rich Spanish first line carrying pádel + Madrid + nivel/rating.
- Manual alt text on all 5 slides, in Spanish (Advanced Settings → alt text
  per image). Instagram's auto-generated alt text is vague junk; this is free
  indexed text almost nobody writes.
- Madrid location tag — separate from hashtags, doesn't count against the 5.
- Optimise for sends: sends-per-reach is the heaviest signal for reaching
  non-followers, which is the whole game for a launch account.

## Pipeline (reproducible)

- `phone_src.html` — the RALLY home screen + device chassis (Montserrat,
  #CCFF00 on #0D0D0D, canonical demo data: 1,370 / +14 / 46 matches / 72% /
  #2 CLUB / VERIFIED). Rendered at 3× with headless Chromium.
- `screen_layer.png` — screen-only cutout used to restore pixel-perfect UI
  after the net edit.
- `../ferry/canvas_in.jpg` — 16:9 canvas with the phone pre-placed; input for
  the image edit that adds the net (Seedream 5 Pro, `is_inpaint`).
- Slide 1 hand and the net edit were generated with Seedream 5 Pro; the
  slide-2 cord is tiled from slide 1's own cord strip with a progressive
  thickness ramp so texture and position match at every seam.
- `overlay_s1.html` / `overlay_s5.html` (+ pre-rendered PNGs) — typography
  overlays: lockup, SWIPE, and the BRAND NEW GAME. CTA slide.
- `build_slides.py` — the compositor: aligns the cord centerline (y=630) at
  all seams by scanning brightest rows, re-pastes the screen with
  acid-pixel-centroid refinement, matches film grain, slices the panorama,
  and uploads the outputs.

Seam QA (brightest-row y / thickness, left vs right of each cut):
seam 1|2: 617/12 vs 616/13 · seam 2|3: 616/45 vs 617/46.

Slide QA: slide 2 carries 0.05% bright pixels outside the cord band (the
strip picker rejected candidate windows scoring up to 57% — those clipped
the fingertips and used to tile ghost shapes across the slide). Slide 5's
type sits 242px from the left edge and 236px from the right.

Slide 1 uses the suit-glove hand generation (`aa438821…`) refined by an
inpaint pass (`e0843e59…`) that removes the cord left of the hand and makes
it emanate from the palm, keeping the right half of the cord pixel-identical
so the slide 1|2 seam is untouched. The cord centerline auto-tunes to the
hand's natural cord height (y=616).
