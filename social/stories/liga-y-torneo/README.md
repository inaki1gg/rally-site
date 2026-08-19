# Story set — Liga y Torneo

Seven-frame Instagram story sequence, 1080×1920, explaining how RALLY leagues
and tournaments run. The set hangs on one line from the spec — **the draw is a
sort, not a shuffle** — because that's the claim that ends the "why am I in B"
argument, and it's the only one a competitor can't copy without also being
deterministic.

Structure: open on the argument, answer it, then teach league, then tournament,
then close.

| # | File | Copy |
|---|---|---|
| 1 | `out/01-por-que-grupo-b.png` | ¿Por qué estoy en el **grupo B**? — "La pregunta de cada temporada." |
| 2 | `out/02-no-es-un-sorteo.png` | No es un sorteo. **Es un orden.** — "Mismos jugadores. Mismos ratings. Mismo cuadro. Siempre." |
| 3 | `out/03-liga.png` | LIGA · Cinco semanas. Una noche por semana. + la escalera del Grupo B |
| 4 | `out/04-tu-grupo.png` | Ves tu grupo y tu movimiento. — "Nadie ve «8º de 8»." |
| 5 | `out/05-torneo.png` | TORNEO · Un día. + cuadro con cabezas de serie repartidas |
| 6 | `out/06-lo-que-ves.png` | Tu sitio. Tu distancia. — "Todo partido cuenta para el rating." |
| 7 | `out/07-nos-vemos-en-septiembre.png` | Liga y torneo **cargando...** + "Nos vemos en Septiembre" |

`out/07b-nos-vemos-sin-sticker.png` is frame 7 with the sticker removed — use it
if you want a real, tappable IG link sticker on top. The sticker in frame 7 is
baked into the pixels.

## Caption

    No es un sorteo. Es un orden.
    The draw is a sort, not a shuffle.

## Screenshots

Both come from the Drive album `App Pics`, cropped to the card so no phone
chrome or empty-state scaffolding comes along:

- Frame 4 — the group standings table from `Cups / Competition is empty`.
- Frame 6 — the expanded "You" row from `Groups / Screenshot 2026-08-05 at
  22.22.55.png`: rank 3, rating 1305, `3RD OF 4`, with `55 TO CLIMB` above and
  `65 CUSHION` below. A live screen with real data.

Two things to know about them:

- **Frame 6 is cropped tight on purpose.** The full screen it comes from is
  titled `TEST GROUP A` and lists `Apple Test` and `Apple test 2` as opponents.
  The crop takes only the "You" row and its two gap rails, so no test-account
  name reaches the story. If you want a frame showing the whole table, capture
  one with real players first.
- **Frame 4 is still an empty state** — the table carries the product's own
  `EXAMPLE` label, and it is visible. No populated bracket exists in Drive.
- **The app UI is in English, the story copy is Spanish.** Normal for the launch
  phase, but frames 4 and 6 are where the seam shows.

Also worth reconciling: the Cups screen says **TEN WEEKS / NINETY MATCHES**,
while the league spec says **five weeks**. The frames avoid pairing a screenshot
with a week count so the story never contradicts itself, but the app copy and
the spec disagree.

## Rebuilding

Frames are HTML in `src/`, rendered with headless Chromium. Fonts are the same
Montserrat woff2 files the site ships, copied in so rendering needs no network.

    ./build.sh
