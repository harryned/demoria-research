#!/usr/bin/env python3
"""Site-level social share cards (1200x630) for the landing, the Birth &
Fertility Tracker and the bubbles animation — brand fonts + palette, matching
the per-country cards built by _build_share_cards.py. Writes public/og/*.png.

  python3 _build_og_cards.py
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1200, 630
NAVY = (12, 26, 51); PAGE = (10, 20, 38); CREAM = (244, 236, 211)
GOLD = (232, 184, 75); GOLDD = (181, 132, 32); INKMUT = (148, 156, 172)
FD = '_fonts'
OUT = 'public/og'
os.makedirs(OUT, exist_ok=True)


def manrope(size, weight=800):
    f = ImageFont.truetype(os.path.join(FD, 'Manrope.ttf'), size)
    f.set_variation_by_axes([weight]); return f


def mono(size, w='Bold'):
    return ImageFont.truetype(os.path.join(FD, f'JetBrainsMono-{w}.ttf'), size)


def spaced(d, xy, text, font, fill, tracking=6, anchor_mid=True):
    """Letter-spaced text (PIL has no tracking)."""
    widths = [d.textlength(c, font=font) for c in text]
    total = sum(widths) + tracking * (len(text) - 1)
    x = xy[0] - total / 2 if anchor_mid else xy[0]
    for c, w in zip(text, widths):
        d.text((x, xy[1]), c, font=font, fill=fill)
        x += w + tracking
    return total


def frame(d):
    d.rectangle([0, 0, W, 16], fill=CREAM)
    d.rectangle([0, 16, W, 19], fill=GOLDD)
    d.rectangle([0, H - 5, W, H], fill=GOLDD)


def sigil(d, cx, cy, s, col=GOLD, lw=7):
    """Brand triangle + hourglass."""
    a = (cx, cy - s); b = (cx + s * 0.94, cy + s * 0.78); c = (cx - s * 0.94, cy + s * 0.78)
    d.line([a, b, c, a], fill=col, width=lw, joint='curve')
    m = s * 0.42
    d.polygon([(cx - m * 0.85, cy - m * 0.45), (cx + m * 0.85, cy - m * 0.45), (cx, cy + m * 0.28)], fill=col)
    d.polygon([(cx, cy + m * 0.28), (cx + m * 0.85, cy + m * 1.05), (cx - m * 0.85, cy + m * 1.05)], fill=col)


# ---------- 1. landing ----------
img = Image.new('RGB', (W, H), PAGE); d = ImageDraw.Draw(img)
frame(d)
sigil(d, W / 2, 130, 52)
spaced(d, (W / 2, 208), 'DEMORIA RESEARCH', mono(21), (201, 166, 74), tracking=9)
t1 = manrope(72, 800)
d.text((W / 2, 300), 'The World’s Demographics', font=t1, fill=(247, 243, 232), anchor='mm')
d.text((W / 2, 384), 'Current, Honest, in One Place', font=manrope(58, 800), fill=GOLD, anchor='mm')
spaced(d, (W / 2, 462), '236 COUNTRIES & TERRITORIES · 1965–2100 · NSO + UN WPP 2024', mono(18), INKMUT, tracking=3)
spaced(d, (W / 2, 556), 'DEMORIARESEARCH.COM', mono(19), (201, 166, 74), tracking=7)
img.save(f'{OUT}/home.png'); print('wrote og/home.png')

# ---------- 2. births tracker (cream, tracker aesthetic) ----------
img = Image.new('RGB', (W, H), CREAM); d = ImageDraw.Draw(img)
d.rectangle([0, 0, 14, H], fill=(196, 34, 26))          # tracker band edge
d.rectangle([W - 0, 0, W, H], fill=CREAM)
d.rectangle([0, H - 5, W, H], fill=GOLDD)
# LIVE chip
d.rounded_rectangle([70, 62, 208, 108], 10, fill=(29, 125, 29))
d.ellipse([88, 77, 104, 93], fill=(244, 236, 211))
d.text((120, 85), 'LIVE', font=mono(26), fill=CREAM, anchor='lm')
d.text((70, 180), 'The Birth & Fertility', font=manrope(88, 800), fill=NAVY, anchor='lm')
d.text((70, 272), 'Tracker', font=manrope(88, 800), fill=(154, 113, 16), anchor='lm')
d.text((70, 372), 'Current-year births for every country on Earth,', font=manrope(37, 600), fill=(60, 70, 92), anchor='lm')
d.text((70, 420), 'refreshed as national offices publish.', font=manrope(37, 600), fill=(60, 70, 92), anchor='lm')
# provenance chips
cx = 70
for label, col in [('NSO', (29, 125, 29)), ('DRE', (181, 132, 32)), ('UN WPP', (110, 117, 128))]:
    w = 46 + len(label) * 17
    d.rounded_rectangle([cx, 480, cx + w, 522], 8, fill=col)
    d.text((cx + w / 2, 501), label, font=mono(22), fill=CREAM, anchor='mm')
    cx += w + 14
d.text((70, 572), 'demoriaresearch.com/births', font=mono(22), fill=(118, 124, 136), anchor='lm')
img.save(f'{OUT}/births.png'); print('wrote og/births.png')

# ---------- 3. bubbles ----------
img = Image.new('RGB', (W, H), PAGE); d = ImageDraw.Draw(img)
frame(d)
# bubble motif: gold cluster deflating into a green cluster
GOLDB = (232, 184, 75); GREENB = (82, 193, 122); BLUEB = (91, 155, 213); PINKB = (236, 111, 158); TEALB = (55, 194, 176)
for (x, y, r, c) in [(210, 300, 96, GOLDB), (330, 250, 52, GOLDB), (320, 372, 40, GOLDB), (415, 305, 26, GOLDB),
                     (560, 330, 30, BLUEB), (620, 270, 22, PINKB), (610, 380, 20, TEALB),
                     (790, 300, 88, GREENB), (900, 250, 48, GREENB), (895, 368, 38, GREENB), (975, 305, 24, GREENB)]:
    d.ellipse([x - r, y - r, x + r, y + r], fill=c)
d.text((210, 300), '1965', font=mono(30), fill=(10, 18, 34), anchor='mm')
d.text((790, 300), '2100', font=mono(30), fill=(10, 18, 34), anchor='mm')
# arrow between clusters
d.line([(455, 300), (520, 300)], fill=INKMUT, width=4)
d.polygon([(520, 292), (536, 300), (520, 308)], fill=INKMUT)
d.text((W / 2, 480), 'A Century of Births', font=manrope(76, 800), fill=(247, 243, 232), anchor='mm')
spaced(d, (W / 2, 540), 'EVERY COUNTRY, ANIMATED · 1965 → 2100 · PRESS PLAY', mono(19), (201, 166, 74), tracking=3)
img.save(f'{OUT}/bubbles.png'); print('wrote og/bubbles.png')
