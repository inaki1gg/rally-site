#!/usr/bin/env python3
"""Render the RALLY heartbeat reel: 8s of ECG, then two title cards.

Everything is deterministic — the heartbeat audio is synthesised, the trace is
drawn from a PQRST model, and the title cards come from headless Chromium so
the type matches the site exactly. Audio and picture share one beat clock, so
every thump lands on an R spike.
"""
import os, subprocess, sys
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
CHROME = os.environ.get("CHROME", "/opt/pw-browsers/chromium-1194/chrome-linux/chrome")

W, H = 1080, 1920
FPS = 30
SR = 44100

BPM = 60.0
BEAT = 60.0 / BPM          # seconds between beats
FIRST_BEAT = 0.5           # let the trace run in before the first spike

ACT1 = 8.0                 # heartbeat
ACT2 = 2.0                 # September 2026
ACT3 = 2.0                 # RALLY.
TOTAL = ACT1 + ACT2 + ACT3

INK = (13, 13, 13)
LIME = (204, 255, 0)

SWEEP = 360.0              # px/sec, so 3 beats span the screen
CURSOR_X = int(W * 0.84)
BASE_Y = int(H * 0.5)
AMP = 330.0                # px for an R of 1.0

BEATS = [FIRST_BEAT + i * BEAT for i in range(int((TOTAL - FIRST_BEAT) / BEAT) + 1)]
BEATS = [b for b in BEATS if b < TOTAL]


# ---------------------------------------------------------------- waveform

def _gauss(x, mu, sigma, amp):
    return amp * np.exp(-((x - mu) ** 2) / (2.0 * sigma ** 2))


def ecg(t):
    """PQRST amplitude at absolute time t. R peaks land exactly on each beat."""
    t = np.asarray(t, dtype=np.float64)
    q = np.full_like(t, np.nan)
    # phase relative to the nearest beat, in [-BEAT/2, BEAT/2)
    rel = (t - FIRST_BEAT) / BEAT
    q = (rel + 0.5) % 1.0 - 0.5
    y = (
        _gauss(q, -0.100, 0.022, 0.13)    # P
        - _gauss(q, -0.025, 0.007, 0.10)  # Q
        + _gauss(q, 0.000, 0.012, 1.00)   # R
        - _gauss(q, 0.028, 0.011, 0.28)   # S
        + _gauss(q, 0.180, 0.045, 0.28)   # T
    )
    return np.where(t < 0, 0.0, y)


def bloom_curve(t):
    """Lime flash that peaks on each R spike and decays fast."""
    v = 0.0
    for b in BEATS:
        d = t - b
        if -0.05 < d < 0.9:
            v += np.exp(-max(d, 0.0) / 0.16) * (1.0 if d >= 0 else (d + 0.05) / 0.05)
    return min(v, 1.0)


# ---------------------------------------------------------------- audio

def thump(n, f0, f1, decay, amp):
    """One low sine sweep with a fast attack — the body of a heart sound."""
    t = np.arange(n) / SR
    freq = f0 + (f1 - f0) * (t / t[-1])
    phase = 2 * np.pi * np.cumsum(freq) / SR
    env = np.exp(-t / decay)
    attack = np.minimum(t / 0.004, 1.0)
    return amp * env * attack * np.sin(phase)


def build_audio(path):
    total = int(TOTAL * SR)
    buf = np.zeros(total + SR, dtype=np.float64)
    n1, n2 = int(0.30 * SR), int(0.24 * SR)
    lub = thump(n1, 68.0, 38.0, 0.055, 1.00)
    dub = thump(n2, 60.0, 34.0, 0.045, 0.62)
    for b in BEATS:
        i = int(b * SR)
        buf[i:i + n1] += lub
        j = int((b + 0.32) * SR)
        buf[j:j + n2] += dub
    buf = buf[:total]
    peak = np.max(np.abs(buf))
    if peak:
        buf = buf / peak * 0.89
    # trim any click at the very end
    tail = int(0.05 * SR)
    buf[-tail:] *= np.linspace(1.0, 0.0, tail)
    pcm = (buf * 32767).astype("<i2")
    stereo = np.repeat(pcm[:, None], 2, axis=1)

    import wave
    with wave.open(path, "wb") as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes(stereo.tobytes())
    return path


# ---------------------------------------------------------------- picture

def render_card(name, out_png):
    subprocess.run([
        CHROME, "--headless", "--no-sandbox", "--disable-gpu", "--hide-scrollbars",
        "--allow-file-access-from-files", "--force-device-scale-factor=1",
        f"--window-size={W},{H}", f"--screenshot={out_png}",
        f"file://{HERE}/src/{name}.html",
    ], check=True, capture_output=True)
    return np.asarray(Image.open(out_png).convert("RGB")).astype(np.float64)


def radial_mask():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float64)
    d = np.sqrt(((xx - W / 2) / (W * 0.95)) ** 2 + ((yy - H / 2) / (H * 0.62)) ** 2)
    return np.clip(1.0 - d, 0.0, 1.0) ** 2.2


def trace_frame(t, mask):
    """One frame of the ECG strip chart."""
    base = np.zeros((H, W, 3), dtype=np.float64)
    base[:] = INK
    glow = bloom_curve(t) * 0.30
    base += mask[..., None] * np.array(LIME, dtype=np.float64) * glow
    img = Image.fromarray(np.clip(base, 0, 255).astype(np.uint8))

    # sample the waveform once per third of a pixel so the R spike never
    # falls between columns
    xs = np.arange(0, CURSOR_X + 1, 1 / 3.0)
    ts = t - (CURSOR_X - xs) / SWEEP
    ys = BASE_Y - ecg(ts) * AMP
    pts = list(zip(xs.tolist(), ys.tolist()))

    layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    d.line([(CURSOR_X, BASE_Y), (W, BASE_Y)], fill=(*LIME, 26), width=3)
    for width, alpha in ((24, 30), (13, 70), (5, 255)):
        d.line(pts, fill=(*LIME, alpha), width=width, joint="curve")

    y_now = BASE_Y - float(ecg(np.array([t]))[0]) * AMP
    for r, alpha in ((34, 40), (18, 90), (8, 255)):
        d.ellipse([CURSOR_X - r, y_now - r, CURSOR_X + r, y_now + r], fill=(*LIME, alpha))

    img = Image.alpha_composite(img.convert("RGBA"), layer).convert("RGB")
    return np.asarray(img).astype(np.float64)


def card_frame(card, t, mask):
    glow = bloom_curve(t) * 0.16
    out = card + mask[..., None] * np.array(LIME, dtype=np.float64) * glow
    return out


def main():
    os.makedirs(f"{HERE}/out", exist_ok=True)
    wav = build_audio(f"{HERE}/out/heartbeat.wav")

    sept = render_card("reel-septiembre", f"{HERE}/out/_card-september.png")
    rally = render_card("reel-rally", f"{HERE}/out/_card-rally.png")
    mask = radial_mask()

    import imageio_ffmpeg
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    mp4 = f"{HERE}/out/rally-heartbeat.mp4"

    n_frames = int(round(TOTAL * FPS))
    proc = subprocess.Popen([
        ff, "-y", "-hide_banner", "-loglevel", "error",
        "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
        "-i", wav,
        "-c:v", "libx264", "-preset", "slow", "-crf", "17",
        "-profile:v", "high", "-pix_fmt", "yuv420p", "-r", str(FPS),
        "-c:a", "aac", "-b:a", "192k", "-ar", str(SR),
        "-movflags", "+faststart", "-shortest", mp4,
    ], stdin=subprocess.PIPE)

    for i in range(n_frames):
        t = i / FPS
        if t < ACT1:
            f = trace_frame(t, mask)
        elif t < ACT1 + ACT2:
            f = card_frame(sept, t, mask)
        else:
            f = card_frame(rally, t, mask)
        proc.stdin.write(np.clip(f, 0, 255).astype(np.uint8).tobytes())
        if i % 60 == 0:
            print(f"  frame {i}/{n_frames}", flush=True)

    proc.stdin.close()
    if proc.wait() != 0:
        sys.exit("ffmpeg failed")

    os.remove(f"{HERE}/out/_card-september.png")
    os.remove(f"{HERE}/out/_card-rally.png")
    print(f"Wrote {mp4}")


if __name__ == "__main__":
    main()
