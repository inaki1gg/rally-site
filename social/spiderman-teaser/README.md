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
| 1 | Gloved hand + cord, lockup, SWIPE | https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/9c8084b0-4977-44b5-98ec-1b9e31281d0d.jpg |
| 2 | Taut cord across black | https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/d9565561-2df2-4418-b3fb-2fb02831acb9.jpg |
| 3 | Cord frays into net | https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/f641c4f1-5ba5-44f9-90ec-7c6b3026c518.jpg |
| 4 | Net catches the phone (RALLY home) | https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/96d4007b-4148-4cee-98d2-5f69e363d1f3.jpg |
| 5 | BRAND NEW GAME. + Founding 100 CTA | https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/f710b332-18c7-45f1-a36b-395c2bad02be.jpg |

Full panorama (5400×1350):
https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/ea7897d4-dc68-44a8-b225-1bfcac0850aa.jpg

Contact sheet:
https://d2ol7oe51mr4n9.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5/cef67101-4a1d-4a87-8604-b3eff1fa6311.jpg

![carousel preview](./carousel_preview.jpg)

## Caption (Spanish-primary, brand voice)

> Un juego nuevo. Founding 100 · Madrid — solicita acceso en la bio.
> A brand new game. Founding 100 · Madrid — apply via the link in bio.

Alt (net wordplay):

> Todo lo que cae en la red queda registrado.
> Whatever lands in the net gets recorded.

No hashtags, no emojis. Post order: slides 1→5, 4:5 portrait.

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
seam 1|2: 629/8 vs 629/9 · seam 2|3: 629/42 vs 630/45.
