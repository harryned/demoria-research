#!/usr/bin/env python3
"""Brand PNGs: the Demoria sigil (stepped double pyramid + arch + hourglass),
redrawn from the site's exact SVG geometry at high resolution. Writes
public/brand/*.png — profile-picture squares (navy, cream, transparent) and a
lockup with the wordmark.

  python3 _build_brand_png.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

NAVY = (12, 26, 51, 255); CREAM = (244, 236, 211, 255); GOLD = (232, 184, 75, 255)
OUT = 'public/brand'; os.makedirs(OUT, exist_ok=True)
SS = 4  # supersampling

# --- exact geometry from the site's SVG (viewBox 600x500) ---
RECTS = [(200,100,50,38),(178,138,72,38),(156,176,94,38),(134,214,116,38),
         (112,252,138,38),(90,290,160,38),(68,328,182,38),(46,366,204,38),
         (350,100,50,38),(350,138,72,38),(350,176,94,38),(350,214,116,38),
         (350,252,138,38),(350,290,160,38),(350,328,182,38),(350,366,204,38)]
TRIS = [[(270,160),(330,160),(300,250)],[(270,350),(330,350),(300,250)]]
ARCH = (250, 50, 350, 150)          # bbox of the r=50 circle centred (300,100)
SW = 4.5
BX0, BY0, BX1, BY1 = 46, 50, 554, 404   # artwork bounds


def draw_sigil(canvas_px, colour, scale_frac=0.72, dy_frac=0.0):
    """Render the sigil centred on a transparent canvas of canvas_px squared."""
    px = canvas_px * SS
    img = Image.new('RGBA', (px, px), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    art_w, art_h = BX1 - BX0, BY1 - BY0
    s = px * scale_frac / max(art_w, art_h)
    ox = (px - art_w * s) / 2 - BX0 * s
    oy = (px - art_h * s) / 2 - BY0 * s + dy_frac * px
    w = max(2, round(SW * s))
    X = lambda x: x * s + ox
    Y = lambda y: y * s + oy
    for (x, y, ww, hh) in RECTS:
        d.rectangle([X(x), Y(y), X(x + ww), Y(y + hh)], outline=colour, width=w)
    d.arc([X(ARCH[0]), Y(ARCH[1]), X(ARCH[2]), Y(ARCH[3])], 180, 360, fill=colour, width=w)
    for t in TRIS:
        pts = [(X(a), Y(b)) for a, b in t]
        d.line(pts + [pts[0], pts[1]], fill=colour, width=w, joint='curve')
    return img


def save(img, name, px=1024):
    img = img.resize((px, px), Image.LANCZOS)
    img.save(f'{OUT}/{name}')
    print('wrote', f'{OUT}/{name}')


# 1. transparent gold sigil
sig = draw_sigil(1024, GOLD)
save(sig, 'demoria-sigil-transparent-1024.png')

# 2. navy square (primary profile pic) — sigil sized for circular crops
bg = Image.new('RGBA', (1024 * SS, 1024 * SS), NAVY)
bg.alpha_composite(draw_sigil(1024, GOLD, scale_frac=0.62))
save(bg, 'demoria-profile-navy-1024.png')

# 3. cream square (light variant), navy sigil
bg = Image.new('RGBA', (1024 * SS, 1024 * SS), CREAM)
bg.alpha_composite(draw_sigil(1024, NAVY, scale_frac=0.62))
save(bg, 'demoria-profile-cream-1024.png')

# 4. lockup: sigil + wordmark on navy
bg = Image.new('RGBA', (1024 * SS, 1024 * SS), NAVY)
bg.alpha_composite(draw_sigil(1024, GOLD, scale_frac=0.52, dy_frac=-0.10))
small = bg.resize((1024, 1024), Image.LANCZOS)
d = ImageDraw.Draw(small)
f = ImageFont.truetype('_fonts/JetBrainsMono-Bold.ttf', 64)
text = 'DEMORIA'
tr = 10  # tracking px
widths = [d.textlength(c, font=f) for c in text]
total = sum(widths) + tr * (len(text) - 1)
x = (1024 - total) / 2
for c, wch in zip(text, widths):
    d.text((x, 745), c, font=f, fill=GOLD)
    x += wch + tr
f2 = ImageFont.truetype('_fonts/JetBrainsMono-Bold.ttf', 30)
text2 = 'RESEARCH'
widths = [d.textlength(c, font=f2) for c in text2]
total = sum(widths) + 16 * (len(text2) - 1)
x = (1024 - total) / 2
for c, wch in zip(text2, widths):
    d.text((x, 835), c, font=f2, fill=(201, 166, 74, 255))
    x += wch + 16
small.save(f'{OUT}/demoria-lockup-navy-1024.png')
print('wrote', f'{OUT}/demoria-lockup-navy-1024.png')
