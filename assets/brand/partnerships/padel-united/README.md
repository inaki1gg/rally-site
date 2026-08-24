# RALLY × Padel United Sports Club

Co-brand lockup for the Padel United partnership.
Padel United Sports Club — 160 Broadway, Cresskill, NJ.

## Files

| File | Size | Use |
|---|---|---|
| `rally-x-padel-united-icon-1080.png` | 1080×1080 | WhatsApp group photo, avatars. Marks only — survives a circular crop and stays legible down to ~48px. |
| `rally-x-padel-united-announcement-1080.png` | 1080×1080 | Instagram post. Adds wordmarks, partner line, location. |
| `rally-x-padel-united-lockup-transparent.png` | 1800×560 | Horizontal lockup on transparent field, for decks and overlays. |
| `padel-united-mark-white.png` | 489×374 | Padel United mark, white on transparent. Working file (see Provenance). |
| `build-lockup.py` | — | Regenerates all three renders. |

## Brand rules applied

Per RALLY Brand System V1:

- **Field** `#0D0D0D` — the ground, the only background colour.
- **Acid** `#CCFF00` — the single accent, rationed. Used only twice per
  composition: the period of the R. mark, and the `×` joining the two marks.
- **White** `#FFFFFF` — primary type and both marks.
- **Muted** `#6B6B6B` — metadata line only.
- **Montserrat Bold (700)** throughout.

The R. mark is rebuilt to the proportions measured off the official
`rally-icon` artwork, not re-typeset by eye:

```
cap height          C
R ink width         0.889 C   (Montserrat 700, not 900)
dot diameter        0.158 C
gap R-ink to dot    0.210 C
dot baseline        aligned to R baseline
```

Note the icon mark uses Montserrat **700**, not 900 — the 900 "R" is ~8%
wider and does not match the official artwork.

## Regenerating

```
python3 build-lockup.py mark      # square icon tile
python3 build-lockup.py post      # announcement
python3 build-lockup.py lockup    # transparent horizontal
```

Renders through headless Chromium at 2× and downsamples, so the type stays
crisp. Needs the self-hosted Montserrat at `/fonts/` in this repo.

## Provenance of the Padel United mark

`padel-united-mark-white.png` was extracted from Padel United's own public
profile artwork by masking their orange field to transparency — their mark,
their own white-on-dark treatment, unaltered in shape. It is good enough for
these renders, but it is a raster trace, not artwork from source.

**Before anything goes to print or to a large format, ask Eric or Justin for
the real vector file.**
