#!/usr/bin/env python3
"""RALLY reel renderer (aspect-general).
Push-in (etch fades imperceptible->clear) -> cut to black -> R. morphs to
RALLY. wordmark -> tagline + URL.

Usage: render.py CLEAN ETCH FONT_BOLD FONT_MED OUTDIR [MODE]
Env: OW,OH output size; WCX,WCY wide-crop center frac; S1 tight scale;
     EX,EY glyph anchor frac (match etch.py); FAST=1 -> bilinear.
"""
import sys, os, math, numpy as np
from PIL import Image, ImageFilter, ImageDraw, ImageFont

CLEAN, ETCH, FBOLD, FMED, OUTDIR = sys.argv[1:6]
MODE = sys.argv[6] if len(sys.argv) > 6 else 'full'
os.makedirs(OUTDIR, exist_ok=True)

OW = int(os.environ.get('OW', '1920'))
OH = int(os.environ.get('OH', '1080'))
FPS = 25
RESAMPLE = Image.LANCZOS if os.environ.get('FAST') != '1' else Image.BILINEAR
ACID = (204, 255, 0)
HOOK = os.environ.get('HOOK', '')  # on-screen scroll-stopper over the opening

clean = Image.open(CLEAN).convert('RGB')
etch = Image.open(ETCH).convert('RGB')
Wm, Hm = clean.size

# ---- geometry: largest AR-crop of the master, centered where we want ----
AR = OW / OH
MAR = Wm / Hm
if AR >= MAR:                      # output wider than master -> full width
    WW = float(Wm); WH = Wm / AR
else:                              # output taller than master -> full height
    WH = float(Hm); WW = Hm * AR
WCX = float(os.environ.get('WCX', '0.5')) * Wm
WCY = float(os.environ.get('WCY', '0.5')) * Hm
S1 = float(os.environ.get('S1', '0.255'))
EX = float(os.environ.get('EX', '0.44'))
EY = float(os.environ.get('EY', '0.63'))
gx, gy = EX * Wm, EY * Hm

def smooth(x):
    x = max(0.0, min(1.0, x))
    return x * x * x * (x * (x * 6 - 15) + 10)

def sample(progress, jphase):
    zp = smooth(progress)
    s = S1 ** zp                    # 1.0 (wide) -> S1 (tight)
    cw = WW * s; ch = WH * s
    cx = WCX + (gx - WCX) * zp
    cy = WCY + (gy - WCY) * zp
    j = cw * 0.010
    cx += math.sin(jphase * 1.7 + 0.4) * j + math.sin(jphase * 0.6) * j * 0.5
    cy += math.cos(jphase * 1.3) * j * 0.8 + math.sin(jphase * 0.9 + 1.1) * j * 0.4
    x0 = cx - cw / 2.0; y0 = cy - ch / 2.0
    x0 = min(max(0.0, x0), Wm - cw)
    y0 = min(max(0.0, y0), Hm - ch)
    a = smooth((zp - 0.06) / 0.66)
    box = (x0, y0, x0 + cw, y0 + ch)
    c = clean.resize((OW, OH), RESAMPLE, box=box)
    if a < 0.004:
        return np.asarray(c).astype(np.float32)
    e = etch.resize((OW, OH), RESAMPLE, box=box)
    return np.asarray(c).astype(np.float32) * (1 - a) + np.asarray(e).astype(np.float32) * a

# vignette + grain
yy, xx = np.mgrid[0:OH, 0:OW].astype(np.float32)
vig = 1.0 - 0.28 * (((xx / OW - 0.5) ** 2) * 1.4 + ((yy / OH - 0.5) ** 2) * 2.2)
vig = np.clip(vig, 0.6, 1.0)[..., None]
rng = np.random.default_rng(7)

def finish(arr, grain=2.4):
    arr = arr * vig + rng.standard_normal((OH, OW, 1)).astype(np.float32) * grain
    return np.clip(arr, 0, 255).astype(np.uint8)

# ---- text (width-aware) ----
_md = ImageDraw.Draw(Image.new('RGB', (8, 8)))

def tracked_w(s, font, tr):
    return sum(_md.textbbox((0, 0), ch, font=font)[2] + tr for ch in s) - (tr if s else 0)

def draw_tracked(d, x, y, s, font, fill, tr):
    for ch in s:
        d.text((x, y), ch, font=font, fill=fill)
        x += _md.textbbox((0, 0), ch, font=font)[2] + tr

def fit_fs(text, target_w, trfrac, path, base=200):
    f = ImageFont.truetype(path, base)
    w = tracked_w(text, f, base * trfrac)
    return max(8, int(base * target_w / max(1.0, w)))

def over(base, layer):
    a = (layer[..., 3] / 255.0)[..., None]
    return base * (1 - a) + layer[..., :3] * a

def wordmark_layer(scale=1.0, alpha=1.0):
    fs = int(fit_fs("RALLY.", 0.72 * OW, 0.06, FBOLD) * scale)
    f = ImageFont.truetype(FBOLD, fs)
    tr = int(fs * 0.06)
    img = Image.new('RGBA', (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    ww = tracked_w("RALLY", f, tr)
    gap = int(fs * 0.10)
    dot_w = _md.textbbox((0, 0), ".", font=f)[2]
    x = (OW - (ww + gap + dot_w)) / 2.0
    asc = f.getmetrics()[0]
    y = OH * 0.45 - asc / 2.0
    draw_tracked(d, x, y, "RALLY", f, (255, 255, 255, 255), tr)
    d.text((x + ww + gap, y), ".", font=f, fill=(*ACID, 255))
    arr = np.asarray(img).astype(np.float32); arr[..., 3] *= alpha
    return arr

def logo_R_layer(scale, alpha, cy_frac=0.45):
    # size by cap height so it matches the pushed-in glyph scale
    base = 400
    fb = ImageFont.truetype(FBOLD, base)
    bb = _md.textbbox((0, 0), "R", font=fb)
    rh = bb[3] - bb[1]
    fs = max(8, int(base * (0.30 * OH) / rh * scale))
    f = ImageFont.truetype(FBOLD, fs)
    img = Image.new('RGBA', (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    rw = _md.textbbox((0, 0), "R", font=f)[2]
    gap = int(fs * 0.05)
    dot_w = _md.textbbox((0, 0), ".", font=f)[2]
    x = OW * 0.5 - (rw + gap + dot_w) / 2.0
    asc = f.getmetrics()[0]
    y = OH * cy_frac - asc / 2.0
    d.text((x, y), "R", font=f, fill=(255, 255, 255, 255))
    d.text((x + rw + gap, y), ".", font=f, fill=(*ACID, 255))
    arr = np.asarray(img).astype(np.float32); arr[..., 3] *= alpha
    return arr

def hook_alpha(i):
    # fade in ~0.3s, hold, fade out before the R resolves (~frame 72)
    if i < 8 or i > 74:
        return 0.0
    if i < 22:
        return smooth((i - 8) / 14.0)
    if i <= 52:
        return 1.0
    return 1.0 - smooth((i - 52) / 22.0)

def hook_layer(alpha):
    fs = int(fit_fs(HOOK.upper(), 0.66 * OW, 0.13, FBOLD))
    fs = min(fs, int(0.045 * OH))          # keep it restrained, not a banner
    f = ImageFont.truetype(FBOLD, fs)
    tr = int(fs * 0.13)
    text = HOOK.upper()
    w = tracked_w(text, f, tr)
    x = (OW - w) / 2.0
    y = 0.11 * OH
    sh = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
    draw_tracked(ImageDraw.Draw(sh), x + 2, y + 3, text, f, (0, 0, 0, 210), tr)
    sh = sh.filter(ImageFilter.GaussianBlur(6))
    tx = Image.new('RGBA', (OW, OH), (0, 0, 0, 0))
    draw_tracked(ImageDraw.Draw(tx), x, y, text, f, (255, 255, 255, 255), tr)
    comp = Image.alpha_composite(sh, tx)
    arr = np.asarray(comp).astype(np.float32); arr[..., 3] *= alpha
    return arr

def endcard_text(base, tag_a, url_a):
    img = Image.new('RGBA', (OW, OH), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    tfs = fit_fs("Know your game.", 0.44 * OW, 0.04, FMED)
    ft = ImageFont.truetype(FMED, tfs); ttr = int(tfs * 0.04)
    tw = tracked_w("Know your game.", ft, ttr)
    draw_tracked(d, (OW - tw) / 2, OH * 0.605, "Know your game.", ft, (235, 235, 235, int(255 * tag_a)), ttr)
    ufs = fit_fs("rallyrating.app/apply", 0.46 * OW, 0.05, FBOLD)
    fu = ImageFont.truetype(FBOLD, ufs); utr = int(ufs * 0.05)
    uw = tracked_w("rallyrating.app/apply", fu, utr)
    draw_tracked(d, (OW - uw) / 2, OH * 0.70, "rallyrating.app/apply", fu, (*ACID, int(255 * url_a)), utr)
    return over(base, np.asarray(img).astype(np.float32))

# ---- timeline ----
PUSH, HOLD, DISS, BUILD, TAGIN, URLIN, ENDHOLD = 170, 12, 26, 18, 14, 12, 34
TOTAL = PUSH + HOLD + DISS + BUILD + TAGIN + URLIN + ENDHOLD

def render_index(i):
    if i < PUSH:
        arr = sample(i / (PUSH - 1), i * 0.13)
        if HOOK:
            a = hook_alpha(i)
            if a > 0.004:
                arr = over(arr, hook_layer(a))
        return finish(arr)
    i2 = i - PUSH
    if i2 < HOLD:
        return finish(sample(1.0, (PUSH + i2) * 0.13))
    i3 = i2 - HOLD
    tight = sample(1.0, (PUSH + HOLD) * 0.13)
    if i3 < DISS:
        t = smooth(i3 / (DISS - 1))
        base = np.clip(tight * (1 - t), 0, 255)
        base = over(base, logo_R_layer(1.0, t))
        return finish(base, grain=1.4 * (1 - t) + 0.5)
    i4 = i3 - DISS
    if i4 < BUILD:
        t = smooth(i4 / (BUILD - 1))
        base = np.zeros((OH, OW, 3), np.float32)
        base = over(base, logo_R_layer(1.0 - 0.58 * t, (1 - t) ** 1.7))
        base = over(base, wordmark_layer(0.80 + 0.20 * t, t ** 0.8))
        return finish(base, grain=0.5)
    base = np.zeros((OH, OW, 3), np.float32)
    base = over(base, wordmark_layer(1.0, 1.0))
    i5 = i4 - BUILD
    tag_a = smooth(i5 / (TAGIN - 1)) if i5 < TAGIN else 1.0
    url_a = 0.0 if i5 < TAGIN else (smooth((i5 - TAGIN) / (URLIN - 1)) if i5 - TAGIN < URLIN else 1.0)
    return finish(endcard_text(base, tag_a, url_a), grain=0.5)

if MODE == 'sample':
    idxs = [0, int(PUSH * 0.5), int(PUSH * 0.82), PUSH + HOLD + DISS // 2,
            PUSH + HOLD + DISS + BUILD // 2, TOTAL - 8]
    for n, i in enumerate(idxs):
        Image.fromarray(render_index(i)).save(f"{OUTDIR}/s{n}_{i:05d}.jpg", quality=90)
    print("SAMPLES", idxs, "TOTAL", TOTAL)
else:
    for i in range(TOTAL):
        Image.fromarray(render_index(i)).save(f"{OUTDIR}/f{i:05d}.jpg", quality=92)
    print("NFRAMES", TOTAL, "FPS", FPS)
