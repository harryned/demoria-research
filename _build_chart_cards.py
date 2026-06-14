#!/usr/bin/env python3
"""Pre-render the /charts/ figures as 1200x630 og:image PNGs (brand fonts via
_fonts/), so chart links unfurl on X / LinkedIn. Mirrors the on-page SVG charts.
Re-run after the chart data changes."""
import json, os, math
from PIL import Image, ImageDraw

FD='_fonts'
from PIL import ImageFont
def manrope(size,weight=800):
    f=ImageFont.truetype(os.path.join(FD,'Manrope.ttf'),size); f.set_variation_by_axes([weight]); return f
def mono(size,w='Regular'):
    return ImageFont.truetype(os.path.join(FD,f'JetBrainsMono-{w}.ttf'),size)

CREAM=(252,244,221); INK=(12,26,51); MUT=(12,26,51,140)
GOLD=(181,132,32); TEAL=(29,158,117); CORAL=(221,111,62); CORALD=(153,60,29)
W,Hh=1200,630
TFR=json.load(open('public/charts_tfr_shift.json'))
ONS=sorted([o for o in json.load(open('public/charts_onset.json')) if o.get('onset')],key=lambda x:x['onset'])

def base(title,sub):
    im=Image.new('RGB',(W,Hh),CREAM); d=ImageDraw.Draw(im,'RGBA')
    d.rectangle([0,0,W,8],fill=GOLD)
    d.text((56,40),title,font=manrope(44,800),fill=INK)
    d.text((58,104),sub,font=mono(20,'Regular'),fill=(90,97,114))
    d.text((56,Hh-30),'demoriaresearch.com   ·   Source: UN WPP 2024 + national statistical offices   ·   CC BY',font=mono(17,'Regular'),fill=(120,126,140))
    return im,d

def jit(iso):
    h=0
    for c in iso: h=(h*31+ord(c))&0xffff
    return (h%1000)/1000*2-1

def dot(d,cx,cy,r,fill,outline):
    d.ellipse([cx-r,cy-r,cx+r,cy+r],fill=fill+(190,),outline=outline+(150,))

# ---------- Chart 1: TFR strip ----------
def chart1():
    im,d=base('The world fell below replacement','Total fertility rate · every country & territory · 1965 vs 2025')
    mL,mR,mT,mB=70,40,170,124
    x0,x1,y0,y1=mL,W-mR,Hh-mB,mT; TMAX=8.6
    yS=lambda t:y0+(y1-y0)*(t/TMAX)
    for t in (0,2,4,6,8):
        y=yS(t); d.line([x0,y,x1,y],fill=(12,26,51,28),width=1)
        d.text((x0-14,y-9),str(t),font=mono(17),fill=(120,126,140),anchor='la')
    d.text((x0-14,yS(8)-30),'TFR',font=mono(16),fill=(120,126,140))
    yr=yS(2.1);
    for xx in range(int(x0),int(x1),14): d.line([xx,yr,xx+7,yr],fill=CORAL,width=2)
    d.text((x1,yr-22),'Replacement — 2.1 children',font=mono(17,'Bold'),fill=CORALD,anchor='ra')
    groups=[('a',int((x0+(x0+x1)/2)/2)+40,'1965'),('b',int(((x0+x1)/2+x1)/2)-10,'2025')]
    bw=(x1-x0)/2*0.74
    for k,cx,lab in groups:
        below=0
        for r in TFR:
            v=r[k]; px=cx+jit(r['iso'])*bw/2; py=yS(v); lo=v<2.1
            if lo: below+=1
            dot(d,px,py,5.2,CORAL if lo else TEAL,CORALD if lo else (15,110,86))
        d.text((cx,y0+18),lab,font=manrope(30,800),fill=INK,anchor='ma')
        d.text((cx,y0+56),f'{below} of {len(TFR)} below',font=mono(18),fill=(90,97,114),anchor='ma')
    lx,ly=x0+4,mT-34
    dot(d,lx+7,ly,6,TEAL,(15,110,86)); d.text((lx+22,ly-9),'at or above replacement',font=mono(17),fill=(90,97,114))
    dot(d,lx+285,ly,6,CORAL,CORALD); d.text((lx+300,ly-9),'below replacement',font=mono(17),fill=(90,97,114))
    im.save('public/charts/fertility-1965-2025.png'); return below

# ---------- Chart 2: natural-decline onset ----------
def chart2():
    im,d=base('When the dying started',f"Year each country's deaths first overtook its births · {len(ONS)} and counting")
    mL,mR,mT,mB=66,24,150,84
    x0,x1,y0,y1=mL,W-mR,Hh-mB,mT; Y0,Y1=1965,2026
    xS=lambda y:x0+(x1-x0)*((y-Y0)/(Y1-Y0))
    CMAX=math.ceil((len(ONS)+4)/10)*10; cS=lambda c:y0+(y1-y0)*(c/CMAX)
    for c in range(0,CMAX+1,20):
        y=cS(c); d.line([x0,y,x1,y],fill=(12,26,51,28),width=1)
        d.text((x0-12,y-9),str(c),font=mono(17),fill=(120,126,140),anchor='la')
    for yy in (1970,1980,1990,2000,2010,2020):
        d.text((xS(yy),y0+12),str(yy),font=mono(17),fill=(120,126,140),anchor='ma')
        d.line([xS(yy),y0,xS(yy),y0+7],fill=(12,26,51,80),width=1)
    # cumulative step
    pts=[(xS(Y0),cS(0))]; cum=0
    for r in ONS:
        x=xS(r['onset']); pts.append((x,cS(cum))); cum+=1; pts.append((x,cS(cum)))
    pts.append((xS(2025),cS(cum)))
    d.polygon(pts+[(xS(2025),cS(0))],fill=(181,132,32,26))
    d.line(pts,fill=GOLD,width=3,joint='curve')
    # rug sized by pop
    for r in ONS:
        x=xS(r['onset']); rr=max(2.5,min(15,math.sqrt(r.get('pop',1) or 1)*1.25))
        dot(d,x,y0-6,rr,CORAL,CORALD)
    cumAt=lambda y:sum(1 for r in ONS if r['onset']<=y)
    for yy,nm,dr in [(1972,'Germany',1),(1992,'Russia',1),(2005,'Japan',1),(2015,'Spain',1),(2022,'China',-1)]:
        x=xS(yy); y=cS(cumAt(yy)); d.ellipse([x-5,y-5,x+5,y+5],fill=INK)
        a='la' if dr>0 else 'ra'; ox=10 if dr>0 else -10
        d.text((x+ox,y+(-22 if dr>0 else -38)),nm,font=manrope(19,800),fill=INK,anchor=a)
        d.text((x+ox,y+(0 if dr>0 else -16)),str(yy),font=mono(15),fill=(90,97,114),anchor=a)
    d.text((x0+38,y1+18),f'{len(ONS)} countries',font=manrope(34,800),fill=INK)
    d.text((x0+40,y1+62),'now in natural decline',font=mono(18),fill=(90,97,114))
    im.save('public/charts/natural-decline.png')

b=chart1(); chart2()
print(f"wrote og PNGs — fertility (2025 below={b}), natural-decline ({len(ONS)})")
