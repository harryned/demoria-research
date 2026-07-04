#!/usr/bin/env python3
"""Demoria brand marks, v3 — the site's exact line-art sigil (outlined stepped
double pyramid, arch, hourglass — tiles NOT filled), rendered at 4096x4096 via
macOS QuickLook (WebKit) from vector SVG. Writes public/brand/:

  demoria-sigil.svg                     master vector (transparent, gold strokes)
  demoria-sigil-transparent-4096.png    true alpha (un-blended)
  demoria-profile-navy-4096.png         <- primary avatar
  demoria-profile-cream-4096.png        navy strokes on cream
  demoria-lockup-navy-4096.png          sigil + wordmark

  python3 _build_brand_png.py
"""
import os, subprocess
import numpy as np
from PIL import Image, ImageDraw, ImageFont

OUT = 'public/brand'; os.makedirs(OUT, exist_ok=True)
PX = 4096
GOLD_HEX = '#e8b84b'; NAVY_HEX = '#0c1a33'
GOLD = (232, 184, 75, 255); GOLDD = (201, 166, 74, 255)

# ---- the site's exact sigil geometry (viewBox 600x500, stroked, no fills) ----
SIGIL_INNER = '''<g stroke="{c}" stroke-width="{sw}" fill="none">
<rect x="200" y="100" width="50" height="38"/><rect x="178" y="138" width="72" height="38"/>
<rect x="156" y="176" width="94" height="38"/><rect x="134" y="214" width="116" height="38"/>
<rect x="112" y="252" width="138" height="38"/><rect x="90" y="290" width="160" height="38"/>
<rect x="68" y="328" width="182" height="38"/><rect x="46" y="366" width="204" height="38"/>
<rect x="350" y="100" width="50" height="38"/><rect x="350" y="138" width="72" height="38"/>
<rect x="350" y="176" width="94" height="38"/><rect x="350" y="214" width="116" height="38"/>
<rect x="350" y="252" width="138" height="38"/><rect x="350" y="290" width="160" height="38"/>
<rect x="350" y="328" width="182" height="38"/><rect x="350" y="366" width="204" height="38"/>
<path d="M 250 100 A 50 50 0 0 1 350 100"/></g>
<g stroke="{c}" stroke-width="{sw}" fill="none" stroke-linejoin="miter">
<path d="M 270 160 L 330 160 L 300 250 Z"/><path d="M 270 350 L 330 350 L 300 250 Z"/></g>'''

# art bounds in viewBox units: x 46..554 (w 508), y 50..404 (h 354)
AW, AH, AX, AY = 508, 354, 46, 50


def sigil_group(colour, scale_frac, sw=4.5, canvas=1000):
    s = canvas * scale_frac / AW
    tx = (canvas - AW * s) / 2 - AX * s
    ty = (canvas - AH * s) / 2 - AY * s
    inner = SIGIL_INNER.format(c=colour, sw=sw)
    return f'<g transform="translate({tx:.1f},{ty:.1f}) scale({s:.4f})">{inner}</g>'


def svg(inner, bg=None):
    b = f'<rect width="1000" height="1000" fill="{bg}"/>' if bg else ''
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000">{b}{inner}</svg>'


def ql(name, px=PX):
    subprocess.run(['qlmanage', '-t', '-s', str(px), '-o', OUT, f'{OUT}/{name}.svg'],
                   capture_output=True, check=True)
    img = Image.open(f'{OUT}/{name}.svg.png').convert('RGBA')
    if img.size != (px, px):
        img = img.resize((px, px), Image.LANCZOS)
    return img


def save(img, name):
    img.save(f'{OUT}/{name}')
    print('wrote', f'{OUT}/{name}', img.size)


# master vector (transparent, gold line-art)
open(f'{OUT}/demoria-sigil.svg', 'w').write(svg(sigil_group(GOLD_HEX, 0.72)))

# profile squares — mark inset for circular avatar crops
open(f'{OUT}/_navy.svg', 'w').write(svg(sigil_group(GOLD_HEX, 0.60), bg=NAVY_HEX))
open(f'{OUT}/_cream.svg', 'w').write(svg(sigil_group(NAVY_HEX, 0.60), bg='#f4ecd3'))
save(ql('_navy'), 'demoria-profile-navy-4096.png')
save(ql('_cream'), 'demoria-profile-cream-4096.png')

# transparent with true alpha: un-blend black/white renders
open(f'{OUT}/_onwhite.svg', 'w').write(svg(sigil_group(GOLD_HEX, 0.72), bg='#ffffff'))
open(f'{OUT}/_onblack.svg', 'w').write(svg(sigil_group(GOLD_HEX, 0.72), bg='#000000'))
W_ = np.asarray(ql('_onwhite'), dtype=np.float64)[:, :, :3]
B_ = np.asarray(ql('_onblack'), dtype=np.float64)[:, :, :3]
alpha = np.clip(1.0 - (W_ - B_).mean(axis=2) / 255.0, 0, 1)
rgb = np.where(alpha[..., None] > 1e-4, B_ / np.maximum(alpha[..., None], 1e-4), 0)
save(Image.fromarray(np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype('uint8'), 'RGBA'),
     'demoria-sigil-transparent-4096.png')

# lockup: mark upper, wordmark beneath
open(f'{OUT}/_lockup.svg', 'w').write(
    svg(f'<g transform="translate(0,-120)">{sigil_group(GOLD_HEX, 0.52)}</g>', bg=NAVY_HEX))
lock = ql('_lockup')
d = ImageDraw.Draw(lock)


def spaced(y, text, font, fill, tr):
    widths = [d.textlength(c, font=font) for c in text]
    x = (PX - (sum(widths) + tr * (len(text) - 1))) / 2
    for c, w in zip(text, widths):
        d.text((x, y), c, font=font, fill=fill)
        x += w + tr


spaced(2870, 'DEMORIA', ImageFont.truetype('_fonts/JetBrainsMono-Bold.ttf', 300), GOLD, 52)
spaced(3290, 'RESEARCH', ImageFont.truetype('_fonts/JetBrainsMono-Bold.ttf', 132), GOLDD, 76)
save(lock, 'demoria-lockup-navy-4096.png')

# tidy temp files + the old 1024 set
for t in ['_navy', '_cream', '_lockup', '_onwhite', '_onblack']:
    for ext in ['.svg', '.svg.png']:
        p = f'{OUT}/{t}{ext}'
        if os.path.exists(p):
            os.remove(p)
p = f'{OUT}/demoria-sigil.svg.png'
if os.path.exists(p):
    os.remove(p)
for old in ['demoria-sigil-transparent-1024.png', 'demoria-profile-navy-1024.png',
            'demoria-profile-cream-1024.png', 'demoria-lockup-navy-1024.png']:
    p = f'{OUT}/{old}'
    if os.path.exists(p):
        os.remove(p)
print('done')
