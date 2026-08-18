# Story set — "Cosas que suben de rating ahora mismo"

Five-frame Instagram story sequence, 1080×1920. RALLY's take on the
snob.madrid "cosas que están hot ahora mismo" format: same five-beat structure
(hook → two judged items → product payoff → loading card + link sticker), but
the joke runs on RALLY's own tier scale (Beg. / Int. / Adv. / Elite) instead of
borrowed "hot", so the punchline is the product's vocabulary.

## Frames

| # | File | Copy |
|---|---|---|
| 1 | `out/01-cosas-que-suben.png` | Cosas que suben **de rating** ahora mismo: |
| 2 | `out/02-madrid-en-agosto.png` | ¿Madrid en agosto? → Rating **BEG.** — "Cero partidos." |
| 3 | `out/03-group-chat.png` | ¿Tu group chat organizando septiembre? → Rating **ADV.** — "Mucho mensaje. Cero reservas." |
| 4 | `out/04-pero-nada-como-esto.png` | Pero nada como esto: → the app |
| 5 | `out/05-nos-vemos-en-septiembre.png` | Tu rating **cargando...** + "Nos vemos en Septiembre" |

`out/05b-nos-vemos-sin-sticker.png` is frame 5 with the sticker removed. Use
that one if you want to drop a real, tappable IG link sticker on top at publish
time — the sticker in frame 5 is baked into the pixels and won't be clickable.

## Caption

    Madrid vuelve en septiembre. Tu rating también.
    Madrid comes back in September. So does your rating.

## Screenshot

Frame 4 uses **Homescreen Fully Unlocked** from the Drive album `App Pics /
Homescreen` — the rating card at 1,320, #1 · Spain. It's the shot that plays the
role the Hot Honey bottle plays in the original: the product, held up. Its
mockup background was flood-filled out (`src/phone.png`) so the device sits on
RALLY black instead of importing a light rectangle.

Runner-up was `Groups / Rivalry-moment` (the 4–2 head-to-head). Stronger for a
group-chat beat, but frame 4 needs to land the rating itself.

## Rebuilding

Frames are HTML in `src/`, rendered with headless Chromium. Fonts are the same
Montserrat woff2 files the site ships, copied in so rendering needs no network.

    ./build.sh
