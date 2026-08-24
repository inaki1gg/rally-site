import base64, sys, subprocess, os
from PIL import Image

SP   = os.path.dirname(os.path.abspath(__file__))
PU   = base64.b64encode(open(os.path.join(SP,"pu_mark_white_3x.png"),"rb").read()).decode()
FONT = "file:///home/user/rally-site/fonts/montserrat-latin-variable.woff2"
CHROME = "/opt/pw-browsers/chromium-1194/chrome-linux/chrome"

# --- RALLY icon geometry, measured off the official rally-icon artwork -------
# Montserrat 700 "R":  cap = .700*fs   inkw = .6225*fs   lsb = .0825*fs
#                      inktop = .1575*fs
# Official icon ratios (relative to cap height C):
#   dot diameter .158C   gap R-ink to dot .21C   dot bottom = R baseline
CAPfs, INKW, LSB, TOP = 0.700, 0.6225, 0.0825, 0.1575
DOT, GAP = 0.158, 0.210
R_W = INKW/CAPfs + GAP + DOT          # mark width in cap units = 1.257

PU_AR = 489/374.0                     # padel united mark aspect

BASE = """
@font-face{{font-family:'Montserrat';font-style:normal;font-weight:300 900;
  src:url('{font}') format('woff2');}}
*{{margin:0;padding:0;box-sizing:border-box;}}
html,body{{background:#0D0D0D;}}
body{{width:{W}px;height:{H}px;font-family:'Montserrat',sans-serif;
  -webkit-font-smoothing:antialiased;overflow:hidden;}}

.rally{{position:relative;display:block;height:var(--c);
  width:calc(var(--c) * %.4f);}}
.rally .glyph{{position:absolute;font-weight:700;line-height:1;color:#FFFFFF;
  font-size:calc(var(--c) / %.4f);
  left:calc(var(--c) * %.4f);top:calc(var(--c) * %.4f);}}
.rally .dot{{position:absolute;right:0;bottom:0;border-radius:50%%;
  background:#CCFF00;
  width:calc(var(--c) * %.4f);height:calc(var(--c) * %.4f);}}

.pu{{display:block;height:calc(var(--c) * var(--pu));
  width:calc(var(--c) * var(--pu) * %.4f);}}
.pu img{{display:block;width:100%%;height:100%%;}}

.row{{display:flex;align-items:center;justify-content:center;}}
.x{{font-weight:400;color:#CCFF00;line-height:1;font-size:calc(var(--c) * .50);}}
""" % (R_W, CAPfs, -LSB/CAPfs, -TOP/CAPfs, DOT, DOT, PU_AR)


def row(c, gap, pu=1.0):
    return ('<div class="row" style="--c:%dpx;--pu:%s">'
            '<span class="rally"><span class="glyph">R</span>'
            '<span class="dot"></span></span>'
            '<span style="width:%dpx"></span>'
            '<span class="x">&#215;</span>'
            '<span style="width:%dpx"></span>'
            '<span class="pu"><img src="data:image/png;base64,%s"></span>'
            '</div>' % (c, pu, gap, gap, PU))


def page(W, H, css, body):
    return ("<!doctype html><html><head><meta charset='utf-8'><style>"
            + BASE.format(font=FONT, W=W, H=H) + css
            + "</style></head><body>" + body + "</body></html>")


# ------------------------------------------------------------------ variants
def v_mark(W, H):
    """Marks only. Survives WhatsApp's circular crop."""
    css = ".stage{width:100%;height:100%;display:flex;align-items:center;justify-content:center;}"
    return page(W, H, css, '<div class="stage">%s</div>' % row(225, 74, 1.14))


def v_post(W, H):
    css = """
    .stage{width:100%;height:100%;display:flex;flex-direction:column;
      align-items:center;justify-content:center;}
    .kicker{font-weight:700;font-size:18px;letter-spacing:.36em;color:#CCFF00;
      text-transform:uppercase;margin-bottom:104px;text-indent:.36em;}
    .names{font-weight:700;font-size:30px;letter-spacing:.20em;color:#FFFFFF;
      text-transform:uppercase;margin-top:112px;text-indent:.20em;}
    .names .sep{color:#CCFF00;font-weight:300;}
    .rule{width:120px;height:1px;background:#262626;margin:32px 0 24px;}
    .place{font-weight:400;font-size:16px;letter-spacing:.28em;color:#6B6B6B;
      text-transform:uppercase;text-indent:.28em;}
    """
    body = ('<div class="stage">'
            '<div class="kicker">Official Partner</div>'
            + row(186, 68, 1.14) +
            '<div class="names">Rally <span class="sep">&#215;</span> Padel United</div>'
            '<div class="rule"></div>'
            '<div class="place">Cresskill, New Jersey</div>'
            '</div>')
    return page(W, H, css, body)


def v_lockup(W, H):
    """Horizontal lockup on a transparent field, for overlays and decks."""
    css = ("html,body{background:transparent;}"
           ".stage{width:100%;height:100%;display:flex;"
           "align-items:center;justify-content:center;}")
    return page(W, H, css, '<div class="stage">%s</div>' % row(200, 66, 1.14))


VARIANTS = {"mark": v_mark, "post": v_post, "lockup": v_lockup}

name = sys.argv[1]
W, H = (1800, 560) if name == "lockup" else (1080, 1080)
hp  = os.path.join(SP, "_%s.html" % name)
raw = os.path.join(SP, "_%s@2x.png" % name)
out = os.path.join(SP, "%s.png" % name)
open(hp, "w").write(VARIANTS[name](W, H))
cmd = [CHROME, "--headless", "--disable-gpu", "--no-sandbox", "--hide-scrollbars",
       "--force-device-scale-factor=2", "--window-size=%d,%d" % (W, H),
       "--screenshot=" + raw, "file://" + hp]
if name == "lockup":
    cmd.insert(1, "--default-background-color=00000000")
subprocess.run(cmd, capture_output=True)
im = Image.open(raw)
mode = "RGBA" if name == "lockup" else "RGB"
im.convert(mode).resize((W, H), Image.LANCZOS).save(out)
print("wrote", out)
