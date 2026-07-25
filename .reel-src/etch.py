#!/usr/bin/env python3
"""Deterministically etch the RALLY 'R.' mark into a real terrain photo as
mown/cleared land-art. Produces a CLEAN master and an ETCHED master that the
renderer cross-fades between (imperceptible -> clear).

Usage: etch.py MASTER.png ICON.png OUT_CLEAN.png OUT_ETCH.png
Anchor + size tuned via env: EX,EY (center frac), EH (glyph height frac), SLOPE.
"""
import sys, os, numpy as np
from PIL import Image, ImageFilter

master, icon, out_clean, out_etch = sys.argv[1:5]
EX = float(os.environ.get('EX', '0.44'))
EY = float(os.environ.get('EY', '0.63'))
EH = float(os.environ.get('EH', '0.135'))   # glyph height as frac of frame H
SQUASH = float(os.environ.get('SQUASH', '0.86'))  # vertical foreshorten on slope

M = Image.open(master).convert('RGB')
W, H = M.size
base = np.asarray(M).astype(np.float32)

# ---- extract R mask + period mask from the brand icon ----
ic = Image.open(icon).convert('RGBA')
ia = np.asarray(ic).astype(np.float32)
r, g, b = ia[..., 0], ia[..., 1], ia[..., 2]
Rm = ((r > 175) & (g > 175) & (b > 175)).astype(np.float32)          # white R
Pm = ((g > 170) & (b < 130) & (r > 130) & (b < g - 40)).astype(np.float32)  # acid dot
glyph = np.clip(Rm + Pm, 0, 1)
ys, xs = np.where(glyph > 0.5)
y0, y1, x0, x1 = ys.min(), ys.max(), xs.min(), xs.max()
Rm = Rm[y0:y1 + 1, x0:x1 + 1]
Pm = Pm[y0:y1 + 1, x0:x1 + 1]
gh0, gw0 = Rm.shape

# ---- target size on the terrain ----
eh = EH * H
ratio = gw0 / gh0
ew = eh * ratio
eh_s = eh * SQUASH                      # squash vertically for slope perspective
def place(mask):
    m = Image.fromarray((mask * 255).astype(np.uint8))
    m = m.resize((int(round(ew)), int(round(eh_s))), Image.LANCZOS)
    canvas = Image.new('L', (W, H), 0)
    cx, cy = int(EX * W), int(EY * H)
    canvas.paste(m, (cx - m.width // 2, cy - m.height // 2))
    return np.asarray(canvas).astype(np.float32) / 255.0

Rf = place(Rm)
Pf = place(Pm)

# feather (soft hand-cut edges) — radius scaled to glyph size
fr = max(1.5, eh * 0.010)
Rf = np.asarray(Image.fromarray((Rf * 255).astype(np.uint8)).filter(
    ImageFilter.GaussianBlur(fr))).astype(np.float32) / 255.0
Pf = np.asarray(Image.fromarray((Pf * 255).astype(np.uint8)).filter(
    ImageFilter.GaussianBlur(fr * 0.8))).astype(np.float32) / 255.0
Pf *= (1 - Rf)  # dot never overlaps the R strokes

out = base.copy()

# ---- R strokes: cleared/mown -> lighter tan-khaki, keeps real texture ----
lum = (0.299 * base[..., 0] + 0.587 * base[..., 1] + 0.114 * base[..., 2])
cleared = np.empty_like(base)
cleared[..., 0] = np.clip(base[..., 0] * 1.12 + 30, 0, 255)
cleared[..., 1] = np.clip(base[..., 1] * 1.02 + 20, 0, 255)
cleared[..., 2] = np.clip(base[..., 2] * 0.90 + 6, 0, 255)
# desaturate cleared 28% toward its own luminance (dead-grass, not vivid)
cl_l = (0.299 * cleared[..., 0] + 0.587 * cleared[..., 1] + 0.114 * cleared[..., 2])
for c in range(3):
    cleared[..., c] = cleared[..., c] * 0.72 + cl_l * 0.28
a = (Rf * 0.92)[..., None]
out = out * (1 - a) + cleared * a

# cut-edge shadow: darker rim on the down-right side for depth
sh = np.asarray(Image.fromarray((Rf * 255).astype(np.uint8)).filter(
    ImageFilter.GaussianBlur(fr * 1.5))).astype(np.float32) / 255.0
shift = max(1, int(eh * 0.012))
sh_off = np.zeros_like(sh); sh_off[shift:, shift:] = sh[:-shift, :-shift]
rim = np.clip(sh_off - Rf, 0, 1) * (1 - Rf)
out *= (1 - (rim * 0.28)[..., None])

# ---- period: clearly the acid-green dot, but muted + textured ----
acid = np.array([150.0, 195.0, 40.0])            # muted from #CCFF00, less neon
tex = np.clip(lum / max(1.0, lum.mean()), 0.55, 1.35)[..., None]
green = acid[None, None, :] * (0.55 + 0.45 * tex)  # texture modulates brightness
green = np.clip(green, 0, 255)
ap = (Pf * 0.9)[..., None]
out = out * (1 - ap) + green * ap
# subtle dark rim around the dot so it reads as a distinct mown circle
psh = np.asarray(Image.fromarray((Pf * 255).astype(np.uint8)).filter(
    ImageFilter.GaussianBlur(fr))).astype(np.float32) / 255.0
prim = np.clip(psh - Pf, 0, 1)
out *= (1 - (prim * 0.20)[..., None])

Image.fromarray(np.clip(base, 0, 255).astype(np.uint8)).save(out_clean)
Image.fromarray(np.clip(out, 0, 255).astype(np.uint8)).save(out_etch)
print("ETCHED", W, H, "glyph_px", int(ew), int(eh_s), "at", int(EX*W), int(EY*H))
