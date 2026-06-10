#!/usr/bin/env python3
"""Pre-render the site's crawlable static pages from the canonical data:

  public/country/<slug>/index.html   one per country/territory (GLOBE + births data
                                     baked into real HTML, per-page meta/OG/canonical)
  public/country/index.html          A-Z / by-continent directory
  public/sitemap.xml                 all URLs
  public/robots.txt                  + Sitemap pointer

Sources: GLOBE blob in dhi_globe.html (scores, rank, band, note, pillars, projections
— identical to what the SPA shows) and public/births_data.json (TFR series, births,
source tier, iso2 flags). Run after any data update, before deploy.
"""
import json, os, re, unicodedata, html, datetime

BASE='https://demoriaresearch.com'
GLOBE_HTML='dhi_globe.html'
BIRTHS='public/births_data.json'
OUT='public'
TODAY=datetime.date.today().isoformat()
def _nice(d):
    try: return datetime.date.fromisoformat(d).strftime('%-d %B %Y')
    except Exception: return d
METH_VERSION='2.0'
METH_PDF='/methodology/DHI-Methodology-v2.0.pdf'
CONTACT='harryned@gmail.com'

# ---------- load ----------
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
INGEST=_nice(BD.get('updated',TODAY))

# Friendly display names for pages/URLs: prefer the tracker's curated names over
# GLOBE's formal UN names ("Republic of Korea" -> "South Korea"), with a few
# spelled-out overrides so slugs read naturally and abbreviations don't leak in.
NAME_OVERRIDES={'PRK':'North Korea','COD':'Democratic Republic of the Congo',
 'LAO':'Laos','DOM':'Dominican Republic','ARE':'United Arab Emirates',
 'BIH':'Bosnia and Herzegovina','XKX':'Kosovo','PSE':'Palestine',
 'TZA':'Tanzania','FSM':'Micronesia','FLK':'Falkland Islands','MAF':'Saint Martin'}
def disp_name(iso):
    if iso in NAME_OVERRIDES: return NAME_OVERRIDES[iso]
    if iso in BC: return BC[iso]['name']
    return G[iso]['name']
for iso in G: G[iso]['name']=disp_name(iso)

def slugify(name):
    s=unicodedata.normalize('NFKD',name)
    s=''.join(ch for ch in s if not unicodedata.combining(ch))
    s=s.replace('&','and').replace("'",'').replace('’','')
    s=re.sub(r'[^A-Za-z0-9]+','-',s).strip('-').lower()
    return s
SLUG={iso:slugify(g['name']) for iso,g in G.items()}
assert len(set(SLUG.values()))==len(SLUG), "slug collision"

# ---- publish the slug map so every surface links to /country/<slug>/ ----
# 1) births_data.json: per-country slug for the tracker tiles
_changed=False
for c in BD['countries']:
    s=SLUG.get(c['iso'])
    if s and c.get('slug')!=s: c['slug']=s; _changed=True
if _changed:
    json.dump(BD,open(BIRTHS,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    print("slugs written into births_data.json")
# 2) dhi_globe.html: splice CSLUG between markers for the SPA's profile/map links
_smap=json.dumps(SLUG,ensure_ascii=False,separators=(',',':'))
_h2,_n=re.subn(r'/\*__CSLUG__\*/.*?/\*__/CSLUG__\*/',
               lambda m:'/*__CSLUG__*/'+_smap+'/*__/CSLUG__*/', h, count=1, flags=re.S)
if _n==1:
    open(GLOBE_HTML,'w',encoding='utf-8').write(_h2)
    print("CSLUG map spliced into dhi_globe.html")
else:
    print("WARN: CSLUG markers not found in dhi_globe.html")

def esc(s): return html.escape(str(s),quote=True)
def band_col(s):
    if s is None: return '#7f8a9e'
    return '#1e7d32' if s>=80 else '#9a7110' if s>=65 else '#cf5512' if s>=50 else '#c4221a' if s>=35 else '#8f1310'
def tfr_col(v):
    if v is None: return '#7f8a9e'
    return '#c4221a' if v<1.0 else '#cf5512' if v<1.3 else '#b8870f' if v<1.6 else '#7f8a9e' if v<2.1 else '#1d8a1d'
CAT={'nso':('NSO','Verified — national statistical office','#1d7d1d'),
     'dre':('DRE','Demoria Research Estimation — synthesised from national & official sources','#b58420'),
     'wpp':('UN WPP','UN WPP 2024 medium-variant projection (forecast)','#56607a')}

def births_block(c):
    """(headline, sub, is_estimate) for the births section."""
    if c.get('b25') is not None and c.get('b26') is not None:
        chg=(c['b26']-c['b25'])/c['b25']*100
        return (f"{c['b26']:,} births in the first {c['mon']} months of 2026",
                f"vs {c['b25']:,} in the same months of 2025 ({chg:+.1f}%)",False)
    if c.get('ba'):
        ba=c['ba']; chg=(ba['cur']-ba['prev'])/ba['prev']*100
        return (f"{ba['cur']:,} births in {ba['year']} (full year)",
                f"vs {ba['prev']:,} in {ba['year']-1} ({chg:+.1f}%)",False)
    if c.get('est'):
        e=c['est']; chg=(e['cur']-e['prev'])/e['prev']*100
        return (f"~{e['cur']:,} births in {e['year']} (estimate)",
                f"vs ~{e['prev']:,} in {e['year']-1} ({chg:+.1f}%)",True)
    return ("Current-year births awaiting release",None,True)

def t2026e(c):
    t25=c.get('tfr',{}).get('2025')
    if t25 and c.get('b25') and c.get('b26'):
        return round(t25*(c['b26']/c['b25']),2)
    return None

CSS="""
:root{--navy:#0c1a33;--navy2:#0a1426;--gold:#e8b84b;--goldd:#b58420;--cream:#f4ecd3;--mut:rgba(12,26,51,.55);--mut2:rgba(12,26,51,.42);--line:rgba(12,26,51,.1)}
*{box-sizing:border-box;margin:0;padding:0}
body{background:var(--navy2);color:var(--navy);font-family:'Manrope',sans-serif;font-size:15px;line-height:1.55}
a{color:var(--goldd)}
.topbar{background:var(--cream);height:50px;display:flex;align-items:center;padding:0 22px;gap:13px;border-bottom:2px solid rgba(12,26,51,.12)}
.topbar a{font-size:.68rem;font-weight:700;letter-spacing:.14em;text-transform:uppercase;color:var(--navy);text-decoration:none}
.topbar .t{font-size:.95rem;font-weight:700;color:var(--navy)}
.wrap{max-width:940px;margin:32px auto 56px;padding:44px 54px 42px 62px;background:var(--cream);border-radius:24px;position:relative;overflow:hidden;box-shadow:0 18px 60px rgba(0,0,0,.45)}
.wrap::before{content:"";position:absolute;left:0;top:0;bottom:0;width:14px;background:var(--band,#7f8a9e)}
@media(max-width:980px){.wrap{margin:0;border-radius:0;padding:34px 22px 36px 30px}}
.crumb{font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:.16em;text-transform:uppercase;color:var(--goldd);margin-bottom:14px}
.crumb a{color:inherit;text-decoration:none}
h1{font-size:clamp(1.9rem,4vw,2.7rem);font-weight:800;letter-spacing:-.01em;color:var(--navy);display:flex;align-items:center;gap:14px;flex-wrap:wrap}
h1 img{height:30px;border-radius:3px;box-shadow:0 1px 4px rgba(12,26,51,.35)}
.sub{color:var(--mut);margin:4px 0 24px;font-size:.92rem}
.score-row{display:flex;gap:14px;flex-wrap:wrap;margin:18px 0 8px}
.card{background:rgba(12,26,51,.05);border:1px solid rgba(12,26,51,.07);border-radius:14px;padding:16px 18px;flex:1;min-width:180px}
.card .k{font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;color:var(--mut2);margin-bottom:6px}
.card .v{font-family:'JetBrains Mono',monospace;font-size:1.7rem;font-weight:800;line-height:1;color:var(--navy)}
.card .s{font-size:.78rem;color:var(--mut);margin-top:6px}
.lede{background:var(--navy);color:var(--cream);border-radius:14px;padding:18px 20px;margin:18px 0;font-size:1.02rem;line-height:1.6}
h2{font-size:1.05rem;font-weight:800;margin:30px 0 10px;letter-spacing:.01em;color:var(--navy)}
table{border-collapse:collapse;width:100%;font-size:.9rem}
th{font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.1em;text-transform:uppercase;color:var(--mut2);text-align:right;padding:7px 10px;border-bottom:1px solid rgba(12,26,51,.2)}
td{text-align:right;padding:8px 10px;border-bottom:1px solid var(--line);font-variant-numeric:tabular-nums;font-family:'JetBrains Mono',monospace;font-weight:700;color:var(--navy)}
th:first-child,td:first-child{text-align:left}
.pill{display:inline-block;font-family:'JetBrains Mono',monospace;font-size:.62rem;font-weight:700;padding:3px 8px;border-radius:5px;color:#fff;vertical-align:2px}
.bar{height:9px;background:rgba(12,26,51,.1);border-radius:5px;overflow:hidden;margin-top:5px}
.bar i{display:block;height:100%;border-radius:5px;background:var(--goldd)}
.pgrid{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.cta{display:flex;gap:12px;flex-wrap:wrap;margin:30px 0 8px}
.cta a{display:inline-block;background:var(--gold);color:var(--navy);font-weight:800;text-decoration:none;padding:12px 20px;border-radius:9px;font-size:.92rem;border:1px solid var(--goldd);box-shadow:0 2px 10px rgba(181,132,32,.25)}
.cta a.ghost{background:transparent;border:1px solid rgba(12,26,51,.4);color:var(--navy);box-shadow:none}
.near a{color:rgba(12,26,51,.78);text-decoration:none;border-bottom:1px dotted rgba(12,26,51,.4)}
.near a:hover{color:var(--goldd)}
.cite{margin:30px 0 0;padding:16px 18px;background:rgba(12,26,51,.05);border:1px solid rgba(12,26,51,.1);border-radius:12px}.cite .ck{font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.12em;text-transform:uppercase;color:var(--mut2);margin-bottom:8px;display:flex;align-items:center;justify-content:space-between}.cite .cv{font-size:.84rem;color:rgba(12,26,51,.85);line-height:1.55;font-family:'JetBrains Mono',monospace}.cite button{background:var(--navy);color:var(--cream);border:none;border-radius:6px;padding:5px 11px;font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.08em;cursor:pointer}.cite button:hover{background:#1a2c52}.foot{margin-top:42px;padding-top:18px;border-top:1px solid rgba(12,26,51,.14);font-size:.8rem;color:var(--mut)}
.foot a{color:rgba(12,26,51,.78)}
"""

HEAD="""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{url}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="Demoria Research">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{url}">
<meta property="og:image" content="{ogimg}">
<meta name="twitter:card" content="{twcard}">
<link rel="icon" href="/favicon-32.png">
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=JetBrains+Mono:wght@400;600;700&display=swap" rel="stylesheet">
<style>{css}</style>
{ld}
</head>
<body>
<div class="topbar"><a href="/">&lsaquo; Demoria Research</a><span style="width:1px;height:20px;background:rgba(12,26,51,.18)"></span><span class="t">{topbar}</span></div>
<div class="wrap"{wrapstyle}>
"""
FOOT=f"""<div class="foot">Data: UN World Population Prospects 2024, national statistical offices, and Demoria Research estimations. See the <a href="/methodology/">methodology</a> (<a href="{METH_PDF}">PDF v{METH_VERSION}</a>), the <a href="/dhi/">interactive index</a> and the <a href="/births/">Birth &amp; Fertility Tracker</a>.<br>Free to reuse with attribution for journalism, research and education — see the <a href="/licence/">data licence</a>. Commercial licensing by enquiry. &copy; Demoria Research.</div>
</div></body></html>"""

def cite_box(title,url):
    cit=f"Demoria Research ({TODAY[:4]}). {title}. Demographic Health Index v{METH_VERSION}. {url} (accessed {_nice(TODAY)})."
    return (f'<div class="cite"><div class="ck"><span>Cite this</span>'
            f'<button onclick="navigator.clipboard&&navigator.clipboard.writeText(this.parentNode.parentNode.querySelector(\'.cv\').textContent).then(()=>{{this.textContent=\'Copied\';setTimeout(()=>this.textContent=\'Copy\',1400)}})">Copy</button></div>'
            f'<div class="cv">{esc(cit)}</div></div>')

# rank-ordered list for neighbours + directory
ranked=sorted(G.values(), key=lambda g:g.get('rank') or 999)

def country_page(iso):
    g=G[iso]; c=BC.get(iso,{})
    name=g['name']; slug=SLUG[iso]; url=f"{BASE}/country/{slug}/"
    score=g.get('scores',{}).get('2025'); rank=g.get('rank'); cat=g.get('cat','')
    note=(g.get('note') or '').strip()
    tfr=c.get('tfr',{}); t25=tfr.get('2025'); e26=t2026e(c)
    iso2=(c.get('iso2') or '').lower()
    flag=f'<img src="https://flagcdn.com/w80/{iso2}.png" alt="Flag of {esc(name)}" width="40" height="27">' if iso2 else ''
    sc=c.get('src_cat','wpp'); cl,cdesc,ccol=CAT.get(sc,CAT['wpp'])
    bh,bs,best=births_block(c)
    # description for meta: note if present else assembled
    desc=note if note else f"{name}: DHI score {score}, rank {rank} of 236, TFR {t25}. Demographic Health Index profile with fertility, births and projections."
    desc=re.sub(r'\s+',' ',desc)[:300]
    cur_tfr=e26 or t25
    title=f"{name} — DHI {score:.1f}, TFR {f'{cur_tfr:.2f}' if cur_tfr is not None else 'n/a'} | Demoria Research"
    # pillars
    pil=(g.get('pillars') or {}).get('2025')
    PNAMES=['Fertility','Age structure','Renewal','Migration']
    pil_html=''
    if pil:
        cells=''.join(f'<div class="card"><div class="k">{n}</div><div class="v" style="font-size:1.25rem">{v:.1f}</div><div class="bar"><i style="width:{max(2,min(100,v))}%"></i></div></div>' for n,v in zip(PNAMES,pil))
        pil_html=f'<h2>Pillars (2025)</h2><div class="pgrid">{cells}</div>'
    # tfr table
    yrs=['2010','2015','2020','2023','2024','2025']
    row_y=''.join(f'<th>{y}</th>' for y in yrs)+('<th>2026e</th>' if e26 else '')
    row_v=''.join(f'<td style="color:{tfr_col(tfr.get(y))};font-weight:700">{tfr.get(y):.2f}</td>' if tfr.get(y) is not None else '<td>–</td>' for y in yrs)+(f'<td style="color:{tfr_col(e26)};font-weight:700;font-style:italic">{e26:.2f}</td>' if e26 else '')
    # projections
    proj=g.get('proj') or {}
    p35=(proj.get('2035') or {}).get('med'); p50=(proj.get('2050') or {}).get('med')
    proj_html=''
    if p35 is not None and p50 is not None:
        proj_html=(f'<h2>DHI outlook (medium variant)</h2><div class="score-row">'
                   f'<div class="card"><div class="k">2035 projected</div><div class="v" style="color:{band_col(p35)}">{p35:.1f}</div></div>'
                   f'<div class="card"><div class="k">2050 projected</div><div class="v" style="color:{band_col(p50)}">{p50:.1f}</div></div></div>')
    # neighbours by rank
    near=''
    if rank:
        idx=[i for i,x in enumerate(ranked) if x['iso']==iso]
        if idx:
            i0=idx[0]; win=[x for x in ranked[max(0,i0-2):i0+3] if x['iso']!=iso]
            near='<h2>Adjacent in the ranking</h2><p class="near">'+' &nbsp;·&nbsp; '.join(
                f'#{x.get("rank")} <a href="/country/{SLUG[x["iso"]]}/">{esc(x["name"])}</a>' for x in win)+'</p>'
    ld=json.dumps({"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
        {"@type":"ListItem","position":1,"name":"Demoria Research","item":BASE+"/"},
        {"@type":"ListItem","position":2,"name":"Countries","item":BASE+"/country/"},
        {"@type":"ListItem","position":3,"name":name,"item":url}]},ensure_ascii=False)
    body=f"""<div class="crumb"><a href="/country/" style="color:inherit;text-decoration:none">Countries</a> · {esc(g.get('cont',''))} · {esc(g.get('reg',''))}</div>
<h1>{flag}{esc(name)}</h1>
<div class="sub">Demographic Health Index profile · data through 2025 · last NSO ingest: {INGEST}</div>
<div class="score-row">
 <div class="card"><div class="k">DHI score 2025</div><div class="v" style="color:{band_col(score)}">{score:.1f}</div><div class="s">{esc(cat)}</div></div>
 <div class="card"><div class="k">Rank</div><div class="v">#{rank}</div><div class="s">of 236 countries &amp; territories</div></div>
 <div class="card"><div class="k">Total fertility rate</div><div class="v" style="color:{tfr_col(e26 or t25)}">{(e26 or t25):.2f}</div><div class="s">{'2026 estimate' if e26 else '2025'} · children per woman</div></div>
</div>
{'<div class="lede">'+esc(note)+'</div>' if note else ''}
<h2>Total fertility rate</h2>
<table><thead><tr>{row_y}</tr></thead><tbody><tr>{row_v}</tr></tbody></table>
<h2>Births <span class="pill" style="background:{ccol}" title="{esc(cdesc)}">{cl}</span></h2>
<p style="font-size:1.05rem;font-weight:700">{esc(bh)}</p>
{'<p style="color:var(--ink2)">'+esc(bs)+'</p>' if bs else ''}
<p style="color:var(--ink3);font-size:.8rem;margin-top:6px">{esc(cdesc)}</p>
{pil_html}
{proj_html}
{near}
<div class="cta">
 <a href="/dhi/#country={iso}">Open the interactive profile</a>
 <a class="ghost" href="/births/">Birth &amp; Fertility Tracker</a>
</div>
{cite_box(f"{name} — Demographic Health Index profile", url)}"""
    page=HEAD.format(title=esc(title),desc=esc(desc),url=url,base=BASE,css=CSS,topbar=esc(name),
                     wrapstyle=f' style="--band:{tfr_col(e26 or t25)}"',
                     ogimg=f"{url}card.png",twcard="summary_large_image",
                     ld=f'<script type="application/ld+json">{ld}</script>')+body+FOOT
    d=os.path.join(OUT,'country',slug); os.makedirs(d,exist_ok=True)
    open(os.path.join(d,'index.html'),'w',encoding='utf-8').write(page)
    return url

# ---------- generate all country pages ----------
urls=[country_page(iso) for iso in G]

# ---------- directory ----------
by_cont={}
for g in ranked: by_cont.setdefault(g.get('cont','Other'),[]).append(g)
secs=''
for cont in ['Asia','Europe','Africa','Americas','Oceania','Other']:
    lst=by_cont.get(cont)
    if not lst: continue
    rows=''.join(f'<tr><td><a href="/country/{SLUG[g["iso"]]}/" style="color:var(--ink);text-decoration:none">{esc(g["name"])}</a></td>'
                 f'<td>#{g.get("rank")}</td><td style="color:{band_col(g.get("scores",{}).get("2025"))};font-weight:700">{g.get("scores",{}).get("2025"):.1f}</td>'
                 f'<td>{esc(g.get("cat",""))}</td></tr>' for g in sorted(lst,key=lambda x:x['name']))
    secs+=f'<h2>{cont}</h2><table><thead><tr><th>Country</th><th>Rank</th><th>DHI 2025</th><th>Band</th></tr></thead><tbody>{rows}</tbody></table>'
dir_page=HEAD.format(title="All 236 country profiles — Demographic Health Index | Demoria Research",
    wrapstyle='',
    ogimg=f"{BASE}/favicon-512.png",twcard="summary",
    desc="Demographic Health Index profiles for all 236 countries and territories: score, rank, fertility, births and projections.",
    url=f"{BASE}/country/",base=BASE,css=CSS,topbar="Countries",ld='')+ \
    '<div class="crumb">Demoria Research · Country profiles</div><h1>Every country &amp; territory</h1>'+ \
    '<div class="sub">DHI 2025 scores and ranks · last NSO ingest: '+INGEST+'; click through for full profiles with fertility and births.</div>'+secs+cite_box('The Demographic Health Index','https://demoriaresearch.com/')+FOOT
open(os.path.join(OUT,'country','index.html'),'w',encoding='utf-8').write(dir_page)

# ---------- methodology (static extract of the SPA essay) ----------
def extract_essay():
    i=h.find('id="view-about"'); j=h.find('id="view-', i+20)
    seg=h[i:j]
    s=seg.find('<div class="essay">'); seg=seg[s:]
    k=seg.rfind('</div>'); seg=seg[:k+6]
    seg=re.sub(r'<script[\s\S]*?</script>','',seg)
    seg=re.sub(r'<svg[\s\S]*?</svg>','',seg)
    seg=re.sub(r'<canvas[\s\S]*?</canvas>','',seg)
    seg=re.sub(r'<button[\s\S]*?</button>','',seg)
    seg=re.sub(r'<(img|input)[^>]*>','',seg)
    def clean_tag(m):
        tag=m.group(1).lower(); attrs=m.group(2)
        if tag=='a':
            href=re.search(r'href="([^"]*)"',attrs)
            return f'<a href="{href.group(1)}">' if href else '<a>'
        return f'<{tag}>'
    seg=re.sub(r'<([a-zA-Z0-9]+)((?:\s+[^<>]*?)?)>',clean_tag,seg)
    return seg

ESSAY_CSS=CSS+"""
.wrap{max-width:760px}
h1{display:block;font-size:clamp(1.9rem,4vw,2.5rem);line-height:1.15;margin:6px 0 14px}
h1 em,h2 em{color:var(--goldd);font-style:normal}
h2{font-size:1.35rem;margin:36px 0 12px}
p{margin:0 0 14px;color:rgba(12,26,51,.82);font-size:1.0rem;line-height:1.7}
p b{color:var(--navy)}
div{margin-bottom:6px}
span{font-family:'JetBrains Mono',monospace;font-size:.66rem;letter-spacing:.14em;text-transform:uppercase;color:var(--goldd);margin-right:10px}
"""
meth_url=f"{BASE}/methodology/"
meth=HEAD.format(title="Methodology — the Demographic Health Index | Demoria Research",
    wrapstyle='',
    ogimg=f"{BASE}/favicon-512.png",twcard="summary",
    desc="How the Demographic Health Index is built: fertility, age structure, momentum and migration combined into a single score for 236 countries and territories, 1965 to 2100.",
    url=meth_url,base=BASE,css=ESSAY_CSS,topbar="Methodology",ld='')+ \
    '<div class="sub" style="font-family:JetBrains Mono,monospace">Version '+METH_VERSION+' · June 2026 · <a href="'+METH_PDF+'">Download as PDF</a> · DOI: pending (Zenodo)</div>'+ \
    extract_essay()+ \
    '<div class="cta"><a href="'+METH_PDF+'">Methodology PDF v'+METH_VERSION+'</a><a class="ghost" href="/dhi/">Open the interactive index</a><a class="ghost" href="/births/">Birth &amp; Fertility Tracker</a><a class="ghost" href="/licence/">Data licence</a></div>'+ \
    cite_box('The Demographic Health Index: methodology (v'+METH_VERSION+')','https://demoriaresearch.com/methodology/')+FOOT
os.makedirs(os.path.join(OUT,'methodology'),exist_ok=True)
open(os.path.join(OUT,'methodology','index.html'),'w',encoding='utf-8').write(meth)

# ---------- data licence ----------
LIC_BODY=f"""<div class="crumb">Demoria Research · Data licence</div>
<h1>Data licence</h1>
<div class="sub">Version 1.0 · applies to the Demographic Health Index and the Birth &amp; Fertility Tracker · last NSO ingest: {INGEST}</div>
<h2>Free with attribution</h2>
<p style="margin-bottom:12px">DHI scores, rankings, projections, Demoria Research Estimations (DRE) and the assembled births dataset are free to reuse, quote, chart and republish for <b>journalism, academic research, education and other non-commercial purposes</b>, provided each use is attributed to <b>&ldquo;Demoria Research (demoriaresearch.com)&rdquo;</b> with a link where the medium allows.</p>
<h2>Commercial use</h2>
<p style="margin-bottom:12px">Use inside commercial products, paid reports, dashboards or redistributed datasets requires a commercial licence. Enquiries: <a href="mailto:{CONTACT}">{CONTACT}</a>.</p>
<h2>Underlying sources</h2>
<p style="margin-bottom:12px">Figures tagged <b>NSO</b> originate from the named national statistical office and remain subject to that office&rsquo;s terms. UN World Population Prospects 2024 inputs are &copy; United Nations, licensed CC BY 3.0 IGO. Demoria Research&rsquo;s scores, estimations and the assembled dataset are &copy; Demoria Research.</p>
<h2>No warranty</h2>
<p>Data is provided as-is; estimates are clearly tagged (DRE, UN WPP) and revised as official figures are published. Cite the access date.</p>"""
lic=HEAD.format(title="Data licence — Demoria Research",
    wrapstyle='', ogimg=f"{BASE}/favicon-512.png",twcard="summary",
    desc="Reuse terms for the Demographic Health Index and Birth & Fertility Tracker: free with attribution for journalism, research and education; commercial licensing by enquiry.",
    url=f"{BASE}/licence/",base=BASE,css=CSS,topbar="Data licence",ld='')+LIC_BODY+FOOT
os.makedirs(os.path.join(OUT,'licence'),exist_ok=True)
open(os.path.join(OUT,'licence','index.html'),'w',encoding='utf-8').write(lic)

# ---------- sitemap + robots ----------
statics=[f"{BASE}/",f"{BASE}/dhi/",f"{BASE}/births/",f"{BASE}/methodology/",f"{BASE}/country/",f"{BASE}/licence/"]
sm=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for u in statics+sorted(urls):
    sm.append(f'<url><loc>{u}</loc><lastmod>{TODAY}</lastmod></url>')
sm.append('</urlset>')
open(os.path.join(OUT,'sitemap.xml'),'w').write('\n'.join(sm))
open(os.path.join(OUT,'robots.txt'),'w').write(f"User-agent: *\nAllow: /\nSitemap: {BASE}/sitemap.xml\n")

print(f"country pages: {len(urls)} | directory + sitemap ({len(statics)+len(urls)} urls) + robots.txt written")
