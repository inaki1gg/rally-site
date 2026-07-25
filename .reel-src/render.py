#!/usr/bin/env python3
"""RALLY reel renderer.
Push-in (etch fades imperceptible->clear) -> cut to black -> R. morphs to
RALLY. wordmark -> tagline + URL.

Usage: render.py CLEAN ETCH FONT_BOLD FONT_MED OUTDIR [MODE]
MODE: 'sample' renders a handful of key frames for quick review; else full reel.
Emits frames fXXXXX.jpg into OUTDIR and prints NFRAMES + FPS.
"""
import sys, os, math, numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont

CLEAN, ETCH, FBOLD, FMED, OUTDIR = sys.argv[1:6]
MODE = sys.argv[6] if len(sys.argv) > 6 else 'full'
os.makedirs(OUTDIR, exist_ok=True)

OW, OH = 1920, 1080
FPS = 25
ACID = (204, 255, 0)

clean = Image.open(CLEAN).convert('RGB')
etch = Image.open(ETCH).convert('RGB')
Wm, Hm = clean.size
clean_a = np.asarray(clean).astype(np.float32)
etch_a = np.asarray(etch).astype(np.float32)

# ---- geometry: 16:9 stage inside the 4:3 master ----
STAGE_H = Wm * 9.0 / 16.0
Y_TOP = (Hm - STAGE_H) / 2.0
# etch anchor (must match etch.py EX,EY)
EX, EY = 0.44, 0.63
gx, gy = EX * Wm, EY * Hm
# wide crop = full stage; tight crop width fraction of master width
S0, S1 = 1.0, 0.255

def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * x * (x * (x * 6 - 15) + 10)

def sample(progress, jphase):
    """Return an OWxOH RGB float array of the pushed-in, etch-blended frame."""
    zp = smooth(progress)
    s = S0 * (S1 / S0) ** zp
    cw = Wm * s
    ch = cw * 9.0 / 16.0
    # center lerp: wide-stage-center -> glyph center
    wcx, wcy = Wm / 2.0, Y_TOP + STAGE_H / 2.0
    cx = wcx + (gx - wcx) * zp
    cy = wcy + (gy - wcy) * zp
    # handheld micro-jitter (scaled with current crop so it feels constant)
    j = cw * 0.010
    cx += math.sin(jphase * 1.7 + 0.4) * j + math.sin(jphase * 0.6) * j * 0.5
    cy += math.cos(jphase * 1.3) * j * 0.8 + math.sin(jphase * 0.9 + 1.1) * j * 0.4
    x0 = cx - cw / 2.0; y0 = cy - ch / 2.0
    # clamp crop box inside the master
    x0 = min(max(0.0, x0), Wm - cw)
    y0 = min(max(0.0, y0), Hm - ch)
    # etch visibility ramp: ~0 at wide -> full before tight (imperceptible->clear)
    a = smooth((zp - 0.06) / 0.66)
    box = (x0, y0, x0 + cw, y0 + ch)
    c = clean.resize((OW, OH), Image.LANCZOS, box=box)
    if a < 0.004:
        out = np.asarray(c).astype(np.float32)
    else:
        e = etch.resize((OW, OH), Image.LANCZOS, box=box)
        out = np.asarray(c).astype(np.float32) * (1 - a) + np.asarray(e).astype(np.float32) * a
    return out

# vignette + grain applied at output res
yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
vig = 1.0 - 0.28 * (((xx / OW - 0.5) ** 2) * 1.4 + ((yy / OH - 0.5) ** 2) * 2.2)
vig = np.clip(vig, 0.6, 1.0)[..., None]
rng = np.random.default_rng(7)

def finish(arr, grain=2.4):
    arr = arr * vig
    arr = arr + rng.standard_normal((OH, OW, 1)).astype(np.float32) * grain
    return np.clip(arr, 0, 255).astype(np.uint8)

# ---- text helpers ----
def load(fp, sz):
    return ImageFont.truetype(fp, sz)

def text_w(draw, s, font, tracking=0):
    w = 0
    for ch in s:
        w += draw.textbbox((0, 0), ch, font=font)[2] + tracking
    return w - (tracking if s else 0)

def draw_tracked(draw, x, y, s, font, fill, tracking=0):
    for ch in s:
        draw.text((x, y), ch, font=font, fill=fill)
        x += draw.textbbox((0, 0), ch, font=font)[2] + tracking

def wordmark_layer(scale=1.0, alpha=1.0, y_center=None):
    """RALLY. wordmark on transparent layer. Returns RGBA np array."""
    img = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fs = int(150 * scale)
    f = load(FBOLD, fs)
    tr = int(fs * 0.06)
    word = "RALLY"
    ww = text_w(d, word, f, tr)
    dot_f = load(FBOLD, fs)
    dot_w = d.textbbox((0, 0), ".", font=dot_f)[2]
    total = ww + int(fs * 0.10) + dot_w
    x = (OW - total) / 2.0
    yc = OH * 0.45 if y_center is None else y_center
    asc, desc = f.getmetrics()
    y = yc - (asc) / 2.0
    draw_tracked(d, x, y, word, f, (255, 255, 255, 255), tr)
    dx = x + ww + int(fs * 0.10)
    d.text((dx, y), ".", font=dot_f, fill=(ACID[0], ACID[1], ACID[2], 255))
    arr = np.asarray(img).astype(np.float32)
    arr[..., 3] *= alpha
    return arr

def logo_R_layer(scale, alpha, cx_frac=0.5, cy_frac=0.45):
    """Big 'R.' mark centered (the icon resolving on black)."""
    img = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    fs = int(360 * scale)
    f = load(FBOLD, fs)
    rw = d.textbbox((0, 0), "R", font=f)[2]
    dot_w = d.textbbox((0, 0), ".", font=f)[2]
    gap = int(fs * 0.05)
    total = rw + gap + dot_w
    asc, desc = f.getmetrics()
    x = OW * cx_frac - total / 2.0
    y = OH * cy_frac - asc / 2.0
    d.text((x, y), "R", font=f, fill=(255, 255, 255, 255))
    d.text((x + rw + gap, y), ".", font=f, fill=(ACID[0], ACID[1], ACID[2], 255))
    arr = np.asarray(img).astype(np.float32)
    arr[..., 3] *= alpha
    return arr

def over(base, layer):
    a = (layer[..., 3] / 255.0)[..., None]
    return base * (1 - a) + layer[..., :3] * a

# tagline + URL fonts
def endcard_text(base, tag_a, url_a):
    img = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    ft = load(FMED, 46)
    tag = "Know your game."
    tw = text_w(d, tag, ft, 2)
    draw_tracked(d, (OW - tw) / 2, OH * 0.605, tag, ft, (235, 235, 235, int(255 * tag_a)), 2)
    fu = load(FBOLD, 40)
    url = "rallyrating.com/apply"
    uw = text_w(d, url, fu, 3)
    draw_tracked(d, (OW - uw) / 2, OH * 0.70, url, fu, (ACID[0], ACID[1], ACID[2], int(255 * url_a)), 3)
    arr = np.asarray(img).astype(np.float32)
    return over(base, arr)

# ---- timeline ----
PUSH = 170
HOLD = 12
DISS = 26      # terrain -> black + etched R resolves to clean R.
BUILD = 18     # R. -> RALLY. wordmark
TAGIN = 14
URLIN = 12
ENDHOLD = 34
TOTAL = PUSH + HOLD + DISS + BUILD + TAGIN + URLIN + ENDHOLD

def render_index(i):
    if i < PUSH:
        p = i / (PUSH - 1)
        return finish(sample(p, i * 0.13))
    i2 = i - PUSH
    if i2 < HOLD:
        return finish(sample(1.0, (PUSH + i2) * 0.13), grain=2.4)
    i3 = i2 - HOLD
    # tight etched frame held as the base for the dissolve
    tight = sample(1.0, (PUSH + HOLD) * 0.13)
    if i3 < DISS:
        t = smooth(i3 / (DISS - 1))
        base = tight * (1 - t)                      # terrain fades to black
        base = np.clip(base, 0, 255)
        # clean R. resolves in, centered (where the etched glyph sat = frame center)
        base = over(base, logo_R_layer(1.0, t))
        return finish(base, grain=1.4 * (1 - t) + 0.5)
    i4 = i3 - DISS
    if i4 < BUILD:
        t = smooth(i4 / (BUILD - 1))
        base = np.zeros((OH, OW, 3), np.float32)
        # big R. cross-dissolves into RALLY. wordmark; R fades fast, word a bit later
        rscale = 1.0 - 0.58 * t
        base = over(base, logo_R_layer(rscale, (1 - t) ** 1.7))
        base = over(base, wordmark_layer(scale=0.80 + 0.20 * t, alpha=t ** 0.8))
        return finish(base, grain=0.5)
    # final: wordmark solid, tagline then URL fade in, hold
    base = np.zeros((OH, OW, 3), np.float32)
    base = over(base, wordmark_layer(1.0, 1.0))
    i5 = i4 - BUILD
    tag_a = smooth(i5 / (TAGIN - 1)) if i5 < TAGIN else 1.0
    url_a = 0.0
    if i5 >= TAGIN:
        url_a = smooth((i5 - TAGIN) / (URLIN - 1)) if i5 - TAGIN < URLIN else 1.0
    base = endcard_text(base, tag_a, url_a)
    return finish(base, grain=0.5)

if MODE == 'sample':
    idxs = [0, int(PUSH*0.45), int(PUSH*0.8), PUSH+HOLD+DISS//2,
            PUSH+HOLD+DISS+BUILD//2, PUSH+HOLD+DISS+BUILD+TAGIN+URLIN+10]
    for n, i in enumerate(idxs):
        Image.fromarray(render_index(i)).save(f"{OUTDIR}/s{n}_{i:05d}.jpg", quality=90)
    print("SAMPLES", idxs, "TOTAL", TOTAL, "FPS", FPS)
else:
    for i in range(TOTAL):
        Image.fromarray(render_index(i)).save(f"{OUTDIR}/f{i:05d}.jpg", quality=92)
    print("NFRAMES", TOTAL, "FPS", FPS)
