"""RALLY x web-teaser carousel compositor.

Runs in the Higgsfield sandbox at /home/user with:
  - the rally-site repo cloned at /home/user/rally-site (this file's repo)
  - g0.png  : hero hand generation (1760x2352)
  - ge.png  : net-catches-phone edit  (2720x1536)
  - uploads.json (optional): {filename: presigned_put_url}

Produces a seamless 5400x1350 panorama sliced into five 1080x1350 slides:
  s1 hand+cord | s2 cord | s3 cord->net | s4 net holds phone | s5 CTA
"""
import json, os, subprocess, sys, hashlib, urllib.request
from PIL import Image, ImageChops, ImageFilter

GEN_BASE = 'https://d8j0ntlcm91z4.cloudfront.net/user_3FwcSFk4XJLeeaMb70sVr46BWA5'
INPUTS = {
    'g0.png': f'{GEN_BASE}/hf_20260812_161318_a8567112-c400-4d9c-886d-695f5ddcfc8b.png',
    'ge.png': f'{GEN_BASE}/hf_20260812_163905_42cc0b1a-bc86-4806-b8c8-b4a119441739.png',
}
for name, url in INPUTS.items():
    p = f'/home/user/{name}'
    if not os.path.exists(p) or os.path.getsize(p) == 0:
        urllib.request.urlretrieve(url, p)

W, H = 1080, 1350
PAN_W = 5 * W
CORD_Y = 630           # global cord centerline, tuned to g0's natural exit height
BG = (5, 5, 5)
ROOT = '/home/user'
REPO = f'{ROOT}/rally-site/social/spiderman-teaser'


def brightest_row(im, x0, x1, y0=350, y1=950, thresh=60):
    """Return (y_center, thickness) of the bright cord inside column band."""
    g = im.convert('L')
    px = g.load()
    best_v, best_y = 0, None
    rows = []
    for y in range(y0, min(y1, g.height)):
        s = 0
        for x in range(x0, min(x1, g.width)):
            s += px[x, y]
        rows.append((s, y))
        if s > best_v:
            best_v, best_y = s, y
    if best_y is None:
        return None, 0
    n = max(1, x1 - x0)
    th = sum(1 for s, y in rows if s / n > thresh and abs(y - best_y) < 90)
    return best_y, th


def add_grain(im, sigma):
    if sigma <= 0:
        return im
    noise = Image.effect_noise(im.size, sigma).convert('RGB')
    return ImageChops.add(im, noise, scale=1.0, offset=-128)


def feather_paste(dst, src, pos, feather=40, edges=('left', 'right')):
    """Paste src onto dst with horizontal alpha ramps on chosen edges."""
    mask = Image.new('L', src.size, 255)
    mp = mask.load()
    w, h = src.size
    for i in range(min(feather, w)):
        a = int(255 * i / feather)
        for y in range(h):
            if 'left' in edges:
                mp[i, y] = min(mp[i, y], a)
            if 'right' in edges:
                mp[w - 1 - i, y] = min(mp[w - 1 - i, y], a)
    dst.paste(src, pos, mask)


report = {}

# ---------------------------------------------------------------- S1: hand
g0 = Image.open(f'{ROOT}/g0.png').convert('RGB')
s = W / g0.width
g0 = g0.resize((W, round(g0.height * s)), Image.LANCZOS)
y_meas, th1 = brightest_row(g0, W - 60, W - 8)
top = max(0, min(g0.height - H, y_meas - CORD_Y))
s1 = g0.crop((0, top, W, top + H))
report['s1_cord_exit'] = brightest_row(s1, W - 60, W - 8)

# ------------------------------------------------------- ge: net + phone
ge = Image.open(f'{ROOT}/ge.png').convert('RGB')
gs = 2400 / ge.width
geh = round(ge.height * gs)
ge_s = ge.resize((2400, geh), Image.LANCZOS)
gey, th2 = brightest_row(ge_s, 235, 250, 400, 900)
shift = gey - CORD_Y            # >0 means move image up
report['ge_cord_at240'] = (gey, th2)
report['ge_shift_up'] = shift

pan = Image.new('RGB', (PAN_W, H), BG)
# black+grain base for synthetic regions, matched to ge shadow noise
patch = ge_s.crop((100, geh - 160, 700, geh - 40)).convert('L')
hist_px = list(patch.getdata())
mean = sum(hist_px) / len(hist_px)
var = sum((p - mean) ** 2 for p in hist_px) / len(hist_px)
sigma = max(4.0, min(11.0, var ** 0.5 * 1.15))
report['grain_sigma'] = round(sigma, 2)

base_black = add_grain(Image.new('RGB', (PAN_W, H), BG), sigma)
pan.paste(base_black, (0, 0))

# place ge crop [240..2400] into panorama [2160..4320]
ge_layer = Image.new('RGB', (2400, H + 200), BG)
ge_layer.paste(ge_s, (0, -shift))
ge_crop = ge_layer.crop((240, 0, 2400, H))
pan.paste(ge_crop, (2160, 0))
report['s3_cord_entry'] = brightest_row(pan.crop((2160, 0, 2260, H)), 0, 60)

# ------------------------------------------------- screen re-paste + refine
def acid_centroid(im, box):
    r = im.crop(box).convert('RGB')
    px = r.load()
    xs = ys = n = 0
    for y in range(0, r.height, 2):
        for x in range(0, r.width, 2):
            pr, pg, pb = px[x, y]
            if pg > 170 and pr > 120 and pb < 110 and pg - pb > 90:
                xs += x; ys += y; n += 1
    return (xs / n, ys / n, n) if n else None

scr = Image.open(f'{REPO}/screen_layer.png').convert('RGBA')
scr = scr.resize(ge.size, Image.LANCZOS)                      # canvas -> ge native
scr = scr.resize((2400, geh), Image.LANCZOS)                  # ge native -> scaled
scr_layer = Image.new('RGBA', (2400, H + 200), (0, 0, 0, 0))
scr_layer.paste(scr, (0, -shift), scr)
scr_crop = scr_layer.crop((240, 0, 2400, H))                  # aligns with ge_crop

phone_box = (3500, 100, 4320, 1250)                           # panorama coords
c_pan = acid_centroid(pan, phone_box)
tmp = Image.new('RGB', (PAN_W, H), (0, 0, 0))
tmp.paste(scr_crop, (2160, 0), scr_crop)
c_scr = acid_centroid(tmp, phone_box)
dx = dy = 0
if c_pan and c_scr and c_scr[2] > 50:
    dx, dy = round(c_pan[0] - c_scr[0]), round(c_pan[1] - c_scr[1])
    dx = max(-14, min(14, dx)); dy = max(-14, min(14, dy))
report['screen_refine_dxdy'] = (dx, dy)
pan.paste(scr_crop, (2160 + dx, 0 + dy), scr_crop)

# --------------------------------------------------------- S2: cord tiling
strip_x0, strip_x1 = 720, 1056
band = 240
strip = s1.crop((strip_x0, CORD_Y - band, strip_x1, CORD_Y + band))
th_left = max(6, report['s1_cord_exit'][1])
th_right = max(th_left, report['s3_cord_entry'][1] if report['s3_cord_entry'][0] else th_left)
grow = min(6.0, th_right / th_left)
report['cord_grow'] = round(grow, 2)

x = W - 60                      # start overlapping S1's right edge
i = 0
while x < 2 * W + 40:
    t = min(1.0, max(0.0, (x - W) / W))
    scale = 1.0 + (grow - 1.0) * t
    tile = strip.transpose(Image.FLIP_LEFT_RIGHT) if i % 2 else strip
    tw = round(tile.width)
    thh = round(tile.height * scale)
    tile = tile.resize((tw, thh), Image.LANCZOS)
    feather_paste(pan, tile, (x, CORD_Y - thh // 2), feather=48)
    x += tw - 64
    i += 1

# paste S1 on top (its own right edge feathers into the tiles)
feather_paste(pan, s1, (0, 0), feather=0, edges=())
# re-blend one strip across the S1|S2 boundary to hide the hard edge
bridge = strip.copy()
feather_paste(pan, bridge, (W - bridge.width // 2, CORD_Y - bridge.height // 2), feather=60)

# --------------------------------------------------------------- overlays
render_py = f'''
from playwright.sync_api import sync_playwright
with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={{'width': 1080, 'height': 1350}})
    for name in ['overlay_s1', 'overlay_s5']:
        page.goto('file://{REPO}/' + name + '.html')
        page.wait_for_timeout(400)
        page.locator('#stage').screenshot(
            path='{ROOT}/' + name + '.png',
            omit_background=(name == 'overlay_s1'))
    browser.close()
print('overlays ok')
'''
open(f'{ROOT}/render_overlays.py', 'w').write(render_py)
r = subprocess.run([sys.executable, f'{ROOT}/render_overlays.py'],
                   capture_output=True, text=True, cwd=ROOT)
if r.returncode != 0:
    npm_root = subprocess.run(['npm', 'root', '-g'], capture_output=True, text=True).stdout.strip()
    render_js = f'''
let pw; try {{ pw = require('playwright'); }} catch (e) {{ pw = require('playwright-core'); }}
(async () => {{
  const browser = await pw.chromium.launch();
  const page = await browser.newPage({{ viewport: {{ width: 1080, height: 1350 }} }});
  for (const name of ['overlay_s1', 'overlay_s5']) {{
    await page.goto('file://{REPO}/' + name + '.html');
    await page.waitForTimeout(400);
    await page.locator('#stage').screenshot({{
      path: '{ROOT}/' + name + '.png',
      omitBackground: name === 'overlay_s1',
    }});
  }}
  await browser.close();
  console.log('overlays ok');
}})().catch(e => {{ console.error('OVERLAY_FAIL', e.message); process.exit(1); }});
'''
    open(f'{ROOT}/render_overlays.js', 'w').write(render_js)
    env = dict(os.environ, NODE_PATH=npm_root)
    r = subprocess.run(['node', f'{ROOT}/render_overlays.js'],
                       capture_output=True, text=True, cwd=ROOT, env=env)
report['overlays'] = (r.returncode, r.stdout.strip()[-120:], r.stderr.strip()[-200:])

if os.path.exists(f'{ROOT}/overlay_s1.png'):
    ov1 = Image.open(f'{ROOT}/overlay_s1.png').convert('RGBA')
    pan.paste(ov1, (0, 0), ov1)
if os.path.exists(f'{ROOT}/overlay_s5.png'):
    ov5 = add_grain(Image.open(f'{ROOT}/overlay_s5.png').convert('RGB'), sigma * 0.7)
    feather_paste(pan, ov5, (4 * W - 90, 0), feather=200, edges=('left',))
    tail = add_grain(Image.new('RGB', (90, H), BG), sigma * 0.7)
    pan.paste(tail, (PAN_W - 90, 0))

# ------------------------------------------------------------ seam metrics
for name, sx in [('seam12', W), ('seam23', 2 * W), ('seam34', 3 * W), ('seam45', 4 * W)]:
    l = brightest_row(pan, sx - 40, sx - 4)
    rr = brightest_row(pan, sx + 4, sx + 40)
    report[name] = {'L': l, 'R': rr}

# ------------------------------------------------------------------ export
out = f'{ROOT}/out'
os.makedirs(out, exist_ok=True)
files = []
for k in range(5):
    slide = pan.crop((k * W, 0, (k + 1) * W, H))
    p = f'{out}/s{k+1}.jpg'
    slide.save(p, quality=92)
    files.append(p)
pan.save(f'{out}/panorama.jpg', quality=88)
files.append(f'{out}/panorama.jpg')

thumbs = [Image.open(f'{out}/s{k+1}.jpg').resize((260, 325), Image.LANCZOS) for k in range(5)]
contact = Image.new('RGB', (260 * 5 + 24, 325 + 8), (24, 24, 24))
for k, t in enumerate(thumbs):
    contact.paste(t, (4 + k * 264, 4))
contact.save(f'{out}/contact.jpg', quality=70)
files.append(f'{out}/contact.jpg')

for p in files:
    b = open(p, 'rb').read()
    report[os.path.basename(p)] = {'bytes': len(b), 'md5': hashlib.md5(b).hexdigest()[:10]}

# ------------------------------------------------------------------ upload
up_path = f'{ROOT}/uploads.json'
if os.path.exists(up_path):
    ups = json.load(open(up_path))
    codes = {}
    for p in files:
        n = os.path.basename(p)
        if n in ups:
            r = subprocess.run(['curl', '-s', '-o', '/dev/null', '-w', '%{http_code}',
                                '-X', 'PUT', '-H', 'Content-Type: image/jpeg',
                                '--upload-file', p, ups[n]], capture_output=True, text=True)
            codes[n] = r.stdout.strip()
    report['upload_codes'] = codes

print(json.dumps(report))
