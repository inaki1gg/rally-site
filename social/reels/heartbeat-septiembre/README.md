# Reel — heartbeat → September 2026 → RALLY.

12 seconds, 1080×1920, 30fps, H.264 + AAC. Three acts, hard cuts, one
unbroken heartbeat running underneath all of them.

| Act | Time | What's on screen |
|---|---|---|
| 1 | 0.0 – 8.0s | ECG trace sweeping right, 8 beats |
| 2 | 8.0 – 10.0s | September 2026 |
| 3 | 10.0 – 12.0s | RALLY. |

Output: `out/rally-heartbeat.mp4`

## How it's built

Nothing is stock or AI-generated — audio and picture are both synthesised, so
they share a single beat clock and stay locked.

- **Heartbeat audio** is built from scratch in `build.py`: each beat is a
  lub-dub pair of low sine sweeps (68→38 Hz for S1, 60→34 Hz for S2, 0.32s
  apart) with a 4ms attack and exponential decay. 60 BPM, beats at 0.5s
  through 11.5s — 12 in total, 8 of them during act 1.
- **The ECG trace** is a PQRST model (P, Q, R, S and T as gaussians) drawn as a
  strip chart scrolling at 360 px/s, so three beats span the screen. The R peak
  is placed exactly on each beat, which means every visual spike lands on the
  audible thump. Sampled at 3 points per pixel so the spike never falls between
  columns.
- **Title cards** are HTML in `src/`, rendered by headless Chromium, so the
  type is the same Montserrat the site and the story set use.
- **The lime bloom** pulses on every beat and is composited per frame, which is
  why the cards in `src/` are pure black — the glow is not baked into them.

The title cards hold still on purpose. Only the background bloom breathes, so
the frames read as cold and deliberate rather than animated.

## Rebuilding

    ./build.sh

Needs `numpy`, `Pillow` and `imageio-ffmpeg` (the wrapper installs them if
missing). Chromium is taken from `$CHROME`.

## Notes

- "September 2026" is in English, as directed. `src/reel-septiembre.html` is a
  one-line change if it should read "Septiembre 2026".
- The beat is steady at 60 BPM. It does not accelerate into the cut.
