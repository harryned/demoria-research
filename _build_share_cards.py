#!/usr/bin/env python3
"""Generate a 1200x630 social share card (card.png) for every country page:
name, DHI score + band + rank, TFR (with 2026 estimate where live), current-year
births and source tier — the country's most important data, readable in a feed.
Run after _build_static_pages.py (uses the same slugs/data)."""
import json, os, re, unicodedata
from PIL import Image, ImageDraw, ImageFont

GLOBE_HTML='dhi_globe.html'; BIRTHS='public/births_data.json'; OUT='public/country'
W,Hc=1200,630
NAVY=(12,26,51); NAVY2=(10,20,38); CREAM=(244,236,211); GOLD=(232,184,75)
INK=(238,241,246); INK2=(190,196,210); INK3=(120,130,150)

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
def slugify(name):
    s=unicodedata.normalize('NFKD',name); s=''.join(ch for ch in s if not unicodedata.combining(ch))
    s=s.replace('&','and').replace("'",'').replace('’','')
    return re.sub(r'[^A-Za-z0-9]+','-',s).strip('-').lower()

AB='/System/Library/Fonts/Supplemental/Arial Bold.ttf'
AR='/System/Library/Fonts/Supplemental/Arial.ttf'
MEN='/System/Library/Fonts/Menlo.ttc'
F=lambda p,s,i=0: ImageFont.truetype(p,s,index=i)

def band_col(s):
    if s is None: return (127,138,158)
    return (46,125,50) if s>=80 else (154,113,16) if s>=65 else (207,85,18) if s>=50 else (196,34,26) if s>=35 else (143,19,16)
def tfr_col(v):
    if v is None: return (127,138,158)
    return (226,74,66) if v<1.0 else (235,110,52) if v<1.3 else (212,164,40) if v<1.6 else (160,170,190) if v<2.1 else (61,158,61)
CAT={'nso':('NSO · VERIFIED NATIONAL DATA',(29,125,29)),
     'dre':('DRE · DEMORIA RESEARCH ESTIMATION',(181,132,32)),
     'wpp':('UN WPP 2024 · PROJECTION',(86,96,122))}

def births_line(c):
    if c.get('b25') is not None and c.get('b26') is not None:
        chg=(c['b26']-c['b25'])/c['b25']*100
        return f"{chg:+.1f}% births YTD 2026  ·  {c['b26']:,} vs {c['b25']:,} ({c['mon']} mo)",chg
    if c.get('ba'):
        ba=c['ba']; chg=(ba['cur']-ba['prev'])/ba['prev']*100
        return f"{chg:+.1f}% births in {ba['year']}  ·  {ba['cur']:,} vs {ba['prev']:,}",chg
    if c.get('est'):
        e=c['est']; chg=(e['cur']-e['prev'])/e['prev']*100
        return f"~{e['cur']:,} births in {e['year']} (estimate, {chg:+.1f}%)",chg
    return "Current-year births awaiting release",None

def t2026e(c):
    t25=c.get('tfr',{}).get('2025')
    if t25 and c.get('b25') and c.get('b26'): return round(t25*(c['b26']/c['b25']),2)
    return None

def fit(draw,text,path,size,maxw,minsize=34):
    while size>minsize:
        f=F(path,size)
        if draw.textlength(text,font=f)<=maxw: return f
        size-=4
    return F(path,minsize)

def card(iso):
    g=G[iso]; c=BC.get(iso,{})
    name=disp(iso); slug=slugify(name)
    score=g.get('scores',{}).get('2025'); rank=g.get('rank'); cat=g.get('cat','')
    t25=c.get('tfr',{}).get('2025'); e26=t2026e(c); cur=e26 or t25
    bl,bchg=births_line(c)
    sc=c.get('src_cat','wpp'); catlab,catcol=CAT.get(sc,CAT['wpp'])

    im=Image.new('RGB',(W,Hc),NAVY2); d=ImageDraw.Draw(im)
    # subtle top band + gold rule
    d.rectangle([0,0,W,8],fill=GOLD)
    d.rectangle([0,8,W,140],fill=NAVY)
    d.text((64,46),"DEMORIA RESEARCH  ·  DEMOGRAPHIC HEALTH INDEX",font=F(MEN,26,1),fill=GOLD)
    # country name
    nf=fit(d,name,AB,92,W-128)
    d.text((60,160),name,font=nf,fill=INK)
    # score block (left)
    sx,sy=64,330
    d.text((sx,sy-44),"DHI SCORE 2025",font=F(MEN,22,0),fill=INK3)
    d.text((sx,sy),f"{score:.1f}",font=F(AB,124),fill=band_col(score))
    d.text((sx,sy+140),cat.upper(),font=F(MEN,24,1),fill=INK2)
    d.text((sx,sy+178),f"RANK #{rank} OF 236",font=F(MEN,24,0),fill=INK3)
    # TFR block (right)
    tx=640
    d.text((tx,sy-44),"TOTAL FERTILITY RATE",font=F(MEN,22,0),fill=INK3)
    if cur is not None:
        d.text((tx,sy),f"{cur:.2f}",font=F(AB,124),fill=tfr_col(cur))
        d.text((tx,sy+140),("2026 ESTIMATE" if e26 else "2025"),font=F(MEN,24,1),fill=INK2)
    # births line across the bottom card area
    by=sy+196
    bcol=INK2
    if bchg is not None: bcol=(61,158,61) if bchg>0 else (226,74,66) if bchg<0 else INK2
    d.text((tx,by),bl,font=fit(d,bl,AR,30,W-tx-56,minsize=22),fill=bcol)
    # source tier chip + footer
    chw=d.textlength(catlab,font=F(MEN,21,1))+36
    d.rounded_rectangle([60,556,60+chw,556+44],radius=9,fill=catcol)
    d.text((78,556+11),catlab,font=F(MEN,21,1),fill=(255,255,255))
    foot=f"demoriaresearch.com/country/{slug}"
    d.text((W-64-d.textlength(foot,font=F(MEN,22,0)),566),foot,font=F(MEN,22,0),fill=INK3)
    path=os.path.join(OUT,slug,'card.png')
    os.makedirs(os.path.dirname(path),exist_ok=True)
    im.save(path,optimize=True)
    return path

n=0; total=0
for iso in G:
    p=card(iso); n+=1; total+=os.path.getsize(p)
print(f"share cards: {n} written, avg {total//n//1024} KB, total {total//1024//1024} MB")
