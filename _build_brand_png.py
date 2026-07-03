#!/usr/bin/env python3
"""Demoria brand marks, v2 — refined solid-gold sigil (stepped double pyramid,
arch, hourglass) built as vector SVG, rendered to PNG via macOS QuickLook
(WebKit), finished with PIL. Writes public/brand/:

  demoria-sigil.svg                    master vector (transparent)
  demoria-sigil-transparent-1024.png
  demoria-profile-navy-1024.png        <- primary avatar
  demoria-profile-cream-1024.png
  demoria-lockup-navy-1024.png         sigil + wordmark

  python3 _build_brand_png.py
"""
import os, subprocess
from PIL import Image, ImageDraw, ImageFont

OUT = 'public/brand'; os.makedirs(OUT, exist_ok=True)
GOLD = (232, 184, 75, 255); GOLDD = (201, 166, 74, 255)


def mark(fill_ref, stroke):
    bars = []
    widths = [70, 110, 150, 190, 230, 270, 310]
    for i, w in enumerate(widths):
        y = 250 + i * 62
        bars.append(f'<rect x="{430-w}" y="{y}" width="{w}" height="52" rx="7" fill="{fill_ref}" stroke="{stroke}" stroke-width="2.5"/>')
        bars.append(f'<rect x="570" y="{y}" width="{w}" height="52" rx="7" fill="{fill_ref}" stroke="{stroke}" stroke-width="2.5"/>')
    # arch: stroke outer edge lands exactly on the inner top corners (430/570, y250)
    arch = ('<path d="M 442 250 A 58 58 0 0 1 558 250" fill="none" '
            f'stroke="{fill_ref}" stroke-width="24" stroke-linecap="butt"/>')
    hg = ('<path d="M 450 336 H 550 L 506 476 V 484 L 550 624 H 450 L 494 484 V 476 Z" '
          f'fill="{fill_ref}" stroke="{stroke}" stroke-width="2.5" stroke-linejoin="round"/>')
    return '\n'.join(bars) + '\n' + arch + '\n' + hg


GOLD_GRAD = '''<linearGradient id="au" x1="0" y1="170" x2="0" y2="700" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#f2d78e"/><stop offset="0.5" stop-color="#e2af41"/><stop offset="1" stop-color="#b5851e"/>
</linearGradient>'''
NAVY_BG = '''<radialGradient id="bg" cx="0.5" cy="0.42" r="0.85">
<stop offset="0" stop-color="#152a52"/><stop offset="1" stop-color="#0a1428"/></radialGradient>'''
NAVY_GRAD = '''<linearGradient id="nv" x1="0" y1="170" x2="0" y2="700" gradientUnits="userSpaceOnUse">
<stop offset="0" stop-color="#1d3560"/><stop offset="1" stop-color="#0a1a38"/></linearGradient>'''


def svg(inner, defs=''):
    return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1000 1000"><defs>{defs}</defs>{inner}</svg>'


mk = mark('url(#au)', '#8a6516')
mkn = mark('url(#nv)', '#0a1428')
open(f'{OUT}/demoria-sigil.svg', 'w').write(svg(f'<g transform="translate(0,45)">{mk}</g>', GOLD_GRAD))
open(f'{OUT}/_navy.svg', 'w').write(svg(f'<rect width="1000" height="1000" fill="url(#bg)"/><g transform="translate(0,45)">{mk}</g>', GOLD_GRAD + NAVY_BG))
open(f'{OUT}/_cream.svg', 'w').write(svg(f'<rect width="1000" height="1000" fill="#f4ecd3"/><g transform="translate(0,45)">{mkn}</g>', NAVY_GRAD))
# lockup base: mark raised + smaller, room for wordmark
open(f'{OUT}/_lockup.svg', 'w').write(svg(
    f'<rect width="1000" height="1000" fill="url(#bg)"/><g transform="translate(150,-25) scale(0.7)">{mk}</g>',
    GOLD_GRAD + NAVY_BG))


def ql(name):
    subprocess.run(['qlmanage', '-t', '-s', '2048', '-o', OUT, f'{OUT}/{name}.svg'],
                   capture_output=True, check=True)
    return Image.open(f'{OUT}/{name}.svg.png').convert('RGBA')


def save(img, name, px=1024):
    img.resize((px, px), Image.LANCZOS).save(f'{OUT}/{name}')
    print('wrote', f'{OUT}/{name}')


# transparent: QuickLook flattens alpha, so un-blend from black + white renders
open(f'{OUT}/_onwhite.svg', 'w').write(svg(f'<rect width="1000" height="1000" fill="#ffffff"/><g transform="translate(0,45)">{mk}</g>', GOLD_GRAD))
open(f'{OUT}/_onblack.svg', 'w').write(svg(f'<rect width="1000" height="1000" fill="#000000"/><g transform="translate(0,45)">{mk}</g>', GOLD_GRAD))
import numpy as np
W_ = np.asarray(ql('_onwhite'), dtype=np.float64)[:, :, :3]
B_ = np.asarray(ql('_onblack'), dtype=np.float64)[:, :, :3]
alpha = 1.0 - (W_ - B_).mean(axis=2) / 255.0
alpha = np.clip(alpha, 0, 1)
with np.errstate(divide='ignore', invalid='ignore'):
    rgb = np.where(alpha[..., None] > 1e-4, B_ / np.maximum(alpha[..., None], 1e-4), 0)
rgba = np.dstack([np.clip(rgb, 0, 255), alpha * 255]).astype('uint8')
save(Image.fromarray(rgba, 'RGBA'), 'demoria-sigil-transparent-1024.png')
save(ql('_navy'), 'demoria-profile-navy-1024.png')
save(ql('_cream'), 'demoria-profile-cream-1024.png')

lock = ql('_lockup').resize((1024, 1024), Image.LANCZOS)
d = ImageDraw.Draw(lock)


def spaced(d, y, text, font, fill, tr):
    widths = [d.textlength(c, font=font) for c in text]
    x = (1024 - (sum(widths) + tr * (len(text) - 1))) / 2
    for c, w in zip(text, widths):
        d.text((x, y), c, font=font, fill=fill)
        x += w + tr


spaced(d, 730, 'DEMORIA', ImageFont.truetype('_fonts/JetBrainsMono-Bold.ttf', 72), GOLD, 12)
spaced(d, 830, 'RESEARCH', ImageFont.truetype('_fonts/JetBrainsMono-Bold.ttf', 32), GOLDD, 18)
lock.save(f'{OUT}/demoria-lockup-navy-1024.png')
print('wrote', f'{OUT}/demoria-lockup-navy-1024.png')

for t in ['_navy', '_cream', '_lockup', '_onwhite', '_onblack']:
    for ext in ['.svg', '.svg.png']:
        p = f'{OUT}/{t}{ext}'
        if os.path.exists(p):
            os.remove(p)
p=f'{OUT}/demoria-sigil.svg.png'
if os.path.exists(p): os.remove(p)
print('cleaned temp files')
