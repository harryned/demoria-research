#!/usr/bin/env python3
"""Per-country social share cards (1200x630 card.png) in the Birth & Fertility
Tracker's cream-tile aesthetic — a tracker card, larger and with more data:
big TFR (banded colour), births panel with YoY change, full TFR strip
2010-2026e, DHI score/band/rank footer, source-tier chip. Real brand fonts
(Manrope variable + JetBrains Mono from _fonts/). Run after data updates.
Note: og:image must be a raster (platforms don't render SVG), hence PNG."""
import json, os, re, unicodedata
from PIL import Image, ImageDraw, ImageFont

GLOBE_HTML='dhi_globe.html'; BIRTHS='public/births_data.json'; OUT='public/country'
W,Hc=1200,630

# ---- palette (tracker tile on cream) ----
NAVY=(12,26,51); PAGE=(10,20,38); CREAM=(244,236,211)
PANEL=(233,224,199)          # .c-births tint on cream
CELL=(237,229,205)
GOLDD=(181,132,32)           # #b58420 dark gold
MUT=(118,124,136)            # rgba(12,26,51,.5) on cream
MUT2=(96,104,120)
PREV=(110,117,128)
GREEN=(29,125,29); RED=(192,57,43)

def est_color(v):
    if v is None: return (42,53,80)
    return (184,29,20) if v<1.0 else (189,84,15) if v<1.3 else (154,113,16) if v<1.6 else (42,53,80) if v<2.1 else (29,125,29)
def band_strip(v):  # .c-band edge colour
    if v is None: return (136,136,136)
    return (196,34,26) if v<1.0 else (207,85,18) if v<1.3 else (184,135,15) if v<1.6 else (127,138,158) if v<2.1 else (29,138,29)
def dhi_col(s):
    if s is None: return MUT
    return (30,125,50) if s>=80 else (154,113,16) if s>=65 else (207,85,18) if s>=50 else (196,34,26) if s>=35 else (143,19,16)

# ---- fonts ----
FD='_fonts'
def manrope(size,weight=800):
    f=ImageFont.truetype(os.path.join(FD,'Manrope.ttf'),size)
    f.set_variation_by_axes([weight]); return f
def mono(size,w='Bold'):
    return ImageFont.truetype(os.path.join(FD,f'JetBrainsMono-{w}.ttf'),size)

# ---- data ----
h=open(GLOBE_HTML,encoding='utf-8').read()
def blob(name):
    i=h.find(name); s=i+len(name); d=0;p=s
    while p<len(h):
        c=h[p]
        if c=='{': d+=1
        elif c=='}':
            d-=1
            if d==0: return json.loads(h[s:p+1])
        p+=1
G={v['iso']:v for v in blob('const GLOBE=').values() if isinstance(v,dict) and v.get('iso')}
BD=json.load(open(BIRTHS,encoding='utf-8'))
BC={c['iso']:c for c in BD['countries']}
NAME_OVERRIDES={'PRK':'North Korea','COD':'Democratic Republic of the Congo',
 'LAO':'Laos','DOM':'Dominican Republic','ARE':'United Arab Emirates',
 'BIH':'Bosnia and Herzegovina','XKX':'Kosovo','PSE':'Palestine',
 'TZA':'Tanzania','FSM':'Micronesia','FLK':'Falkland Islands','MAF':'Saint Martin'}
def disp(iso):
    if iso in NAME_OVERRIDES: return NAME_OVERRIDES[iso]
    return BC[iso]['name'] if iso in BC else G[iso]['name']
def slugify(n):
    s=unicodedata.normalize('NFKD',n); s=''.join(ch for ch in s if not unicodedata.combining(ch))
    s=s.replace('&','and').replace("'",'').replace('’','')
    return re.sub(r'[^A-Za-z0-9]+','-',s).strip('-').lower()
def t2026e(c):
    t25=c.get('tfr',{}).get('2025')
    if t25 and c.get('b25') and c.get('b26'): return round(t25*(c['b26']/c['b25']),2)
    return None
CHIP={'nso':('NSO · VERIFIED NATIONAL DATA',(29,125,29),(255,255,255)),
      'dre':('DRE · DEMORIA RESEARCH ESTIMATION',(181,132,32),(255,255,255)),
      'wpp':('UN WPP 2024 · PROJECTION',(214,205,180),(86,96,122))}

def fit(draw,text,mk,size,maxw,minsize=30):
    while size>minsize:
        f=mk(size)
        if draw.textlength(text,font=f)<=maxw: return f
        size-=4
    return mk(minsize)

def card(iso):
    g=G[iso]; c=BC.get(iso,{})
    name=disp(iso); slug=slugify(name)
    score=g.get('scores',{}).get('2025'); rank=g.get('rank'); cat=(g.get('cat') or '').upper()
    tfr=c.get('tfr',{}); t25=tfr.get('2025'); e26=t2026e(c); cur=e26 or t25
    sc=c.get('src_cat','wpp')

    im=Image.new('RGB',(W,Hc),PAGE); d=ImageDraw.Draw(im)
    # cream tile with the tracker's coloured left band
    d.rounded_rectangle([18,18,W-18,Hc-18],radius=26,fill=CREAM)
    d.rounded_rectangle([18,18,46,Hc-18],radius=13,fill=band_strip(cur))
    d.rectangle([36,18,46,Hc-18],fill=band_strip(cur))
    X=84  # content left edge

    # header: eyebrow + source chip
    d.text((X,52),"DEMORIA RESEARCH · BIRTH & FERTILITY TRACKER",font=mono(21,'Bold'),fill=GOLDD)
    lab,bg,fg=CHIP.get(sc,CHIP['wpp'])
    cf=mono(19,'Bold'); cw=d.textlength(lab,font=cf)+34
    d.rounded_rectangle([W-64-cw,40,W-64,40+42],radius=8,fill=bg)
    d.text((W-64-cw+17,40+11),lab,font=cf,fill=fg)

    # country name
    nf=fit(d,name,lambda s:manrope(s,800),84,W-X-360)
    d.text((X,92),name,font=nf,fill=NAVY)

    # ---- left: big TFR ----
    ly=232
    d.text((X,ly),("ESTIMATED 2026 TFR" if e26 else "LATEST TFR · 2025"),font=mono(22,'Bold'),fill=MUT)
    if cur is not None:
        d.text((X-6,ly+30),f"{cur:.2f}",font=mono(150,'ExtraBold'),fill=est_color(cur))

    # ---- right: births panel ----
    px,py,pw,ph=560,250,556,190
    d.rounded_rectangle([px,py,px+pw,py+ph],radius=16,fill=PANEL)
    pad=26
    if c.get('b25') is not None and c.get('b26') is not None:
        head={'nso':'NSO','dre':'DRE','wpp':'UN WPP'}[sc]+f" · FIRST {c['mon']} MONTHS"
        chg=(c['b26']-c['b25'])/c['b25']*100
        y0,y1,v0,v1='2025','2026',f"{c['b25']:,}",f"{c['b26']:,}"
    elif c.get('ba'):
        ba=c['ba']; head={'nso':'NSO','dre':'DRE','wpp':'UN WPP'}[sc]+f" · {ba['year']} FULL YEAR"
        chg=(ba['cur']-ba['prev'])/ba['prev']*100
        y0,y1,v0,v1=str(ba['year']-1),str(ba['year']),f"{ba['prev']:,}",f"{ba['cur']:,}"
    elif c.get('est'):
        e=c['est']; head="UN WPP 2024 · PROJECTED" if sc=='wpp' else "DEMORIA RESEARCH ESTIMATE"
        chg=(e['cur']-e['prev'])/e['prev']*100
        y0,y1,v0,v1=str(e['year']-1),str(e['year']),f"~{e['prev']:,}",f"~{e['cur']:,}"
    else:
        head="BIRTHS 2026"; chg=None; y0=y1=v0=v1=None
    d.text((px+pad,py+22),head,font=mono(20,'Bold'),fill=MUT2)
    if chg is not None:
        cs=("▲ " if chg>0 else "▼ " if chg<0 else "")+f"{chg:+.1f}%"
        ccol=GREEN if chg>0 else RED if chg<0 else MUT2
        cf2=mono(30,'ExtraBold')
        d.text((px+pw-pad-d.textlength(cs,font=cf2),py+16),cs,font=cf2,fill=ccol)
    if v0:
        vf=mono(46,'Bold'); yf=mono(19,'Bold')
        col0=px+pad; col1=px+pw//2+34
        d.text((col0,py+74),y0,font=yf,fill=MUT)
        f0=fit(d,v0,lambda s:mono(s,'Bold'),46,pw//2-pad-44,minsize=28)
        d.text((col0,py+100),v0,font=f0,fill=PREV)
        ay=py+112
        d.text((px+pw//2-8,ay),"→",font=mono(34,'Bold'),fill=MUT)
        d.text((col1,py+74),y1,font=yf,fill=MUT)
        f1=fit(d,v1,lambda s:mono(s,'Bold'),46,pw//2-pad-44,minsize=28)
        d.text((col1,py+100),v1,font=f1,fill=NAVY)
    else:
        d.text((px+pad,py+95),"awaiting release",font=mono(30,'Regular'),fill=MUT)

    # ---- TFR strip: 2010 / 2015 / 2020 / 2024 / 2025 / 2026e ----
    d.text((X,462),"TFR · CHILDREN PER WOMAN",font=mono(19,'Bold'),fill=MUT)
    years=[('2010',tfr.get('2010'),False),('2015',tfr.get('2015'),False),('2020',tfr.get('2020'),False),
           ('2024',tfr.get('2024'),False),('2025',t25,False),('2026e',e26,True)]
    cy=492; cw2=164; chh=74; gap=14
    for i,(yl,v,is_e) in enumerate(years):
        cx=X+i*(cw2+gap)
        if is_e and v is not None:
            d.rounded_rectangle([cx,cy,cx+cw2,cy+chh],radius=12,outline=GOLDD,width=3)
        else:
            d.rounded_rectangle([cx,cy,cx+cw2,cy+chh],radius=12,fill=CELL)
        d.text((cx+16,cy+10),yl,font=mono(17,'Bold'),fill=MUT)
        if v is not None:
            d.text((cx+16,cy+30),f"{v:.2f}",font=mono(34,'ExtraBold'),fill=(est_color(v) if (is_e or yl=='2025') else NAVY))
        else:
            d.text((cx+16,cy+32),"—",font=mono(30,'Regular'),fill=MUT)

    # ---- footer: DHI line + URL ----
    fy=Hc-44
    seg1="DHI "; seg2=f"{score:.1f}"; seg3=f" · {cat} · RANK #{rank} OF 236"
    f1=mono(19,'Bold')
    x=X
    d.text((x,fy),seg1,font=f1,fill=MUT); x+=d.textlength(seg1,font=f1)
    d.text((x,fy),seg2,font=f1,fill=dhi_col(score)); x+=d.textlength(seg2,font=f1)
    d.text((x,fy),seg3,font=f1,fill=MUT)
    url=f"demoriaresearch.com/country/{slug}"
    uf=mono(19,'Regular')
    d.text((W-64-d.textlength(url,font=uf),fy),url,font=uf,fill=MUT)

    path=os.path.join(OUT,slug,'card.png')
    os.makedirs(os.path.dirname(path),exist_ok=True)
    im.save(path,optimize=True)
    return os.path.getsize(path)

sizes=[card(iso) for iso in G]
print(f"share cards: {len(sizes)} written, avg {sum(sizes)//len(sizes)//1024} KB, total {sum(sizes)//1024//1024} MB")
