#!/usr/bin/env python3
"""Inject national births+deaths for the 9 countries whose Wikipedia tables the
auto-scraper couldn't parse (JPN/CHN/RUS/DEU/TUR/ARM/KAZ/KGZ/VNM), and fix
FRANCE to a single coherent scope (Metropolitan France, matching its deaths).
Data: _nso_deaths_manual.json (Wikipedia vital-stats, NSO-compiled).

For the 9: inject deaths (all years), and births for pre-2023 history
(curated sheet keeps 2023-2025). For FRA: inject BOTH births & deaths
2018-2025 at metropolitan scope (overriding the entiere sheet births, which
mismatched the metropole deaths)."""
import json, shutil
GLOBE='dhi_globe.html'; shutil.copy(GLOBE,GLOBE+'.bak_x')
WPP=json.load(open('_wpp_indicators_1960_2025.json'))
MAN={k:v for k,v in json.load(open('_nso_deaths_manual.json')).items() if not k.startswith('_')}
def wd(iso,y): v=WPP.get(iso,{}).get(str(y),{}).get('Deaths'); return v*1000 if v is not None else None
def wb(iso,y): return WPP.get(iso,{}).get(str(y),{}).get('Births')

h=open(GLOBE,encoding='utf-8').read()
i=h.find('const DATA='); s=i+len('const DATA=')
d=0;p=s
while p<len(h):
    c=h[p]
    if c=='{':d+=1
    elif c=='}':
        d-=1
        if d==0: e=p+1;break
    p+=1
DATA=json.loads(h[s:e])
DSRC=json.load(open('_deaths_sources.json'))

nd=nb=0
for iso,years in MAN.items():
    if iso not in DATA: continue
    m=DATA[iso]; yrs=m['yrs']; ny=m.setdefault('nso_yrs',{}); dy=m.setdefault('dre_yrs',{})
    dl=set(ny.get('deaths',[])); bl=set(ny.get('births',[]))
    fra=(iso=='FRA')
    for ys,(bv,dv) in years.items():
        yy=int(ys)
        if yy not in yrs: continue
        idx=yrs.index(yy)
        wD=wd(iso,yy)
        if dv and wD and 0.5*wD<=dv<=2*wD:
            m['ind']['deaths'][idx]=round(dv); dl.add(yy); nd+=1
        # births: France -> all years (metropole scope fix); others -> replace
        # wherever the current value differs >2% from the reported figure
        # (corrects WPP-modelled cells like Japan 2024), tag NSO either way.
        if bv:
            wB=wb(iso,yy); cur=m['ind']['births'][idx]
            if wB and 0.4*wB<=bv/1000<=2.2*wB:
                if fra or cur is None or abs(cur-bv/1000)/(bv/1000)>0.02:
                    m['ind']['births'][idx]=round(bv/1000,3); nb+=1
                bl.add(yy)
    ny['deaths']=sorted(dl); ny['births']=sorted(bl)
    DSRC[iso]=MAN.get('_slug',{}).get(iso,'Demographics_of_'+iso) if False else DSRC.get(iso,'wikipedia-vital-stats')

# recompute single-year natural change + retag (NSO if both national, DRE if mixed)
for iso,m in DATA.items():
    yrs=m['yrs']; ny=m.get('nso_yrs',{}); dy=m.get('dre_yrs',{})
    def isN(k,y): return y in (ny.get(k) or [])
    def isD(k,y): return y in (dy.get(k) or [])
    ncN=set(); ncD=set()
    for k,yy in enumerate(yrs):
        b=m['ind']['births'][k]; de=m['ind']['deaths'][k]
        if b is None or de is None: m['ind']['natch5'][k]=None; continue
        m['ind']['natch5'][k]=round(b-de/1000.0,3)
        bn=isN('births',yy) and not isD('births',yy); dn=isN('deaths',yy) and not isD('deaths',yy)
        if bn and dn: ncN.add(yy)
        elif isN('births',yy) or isN('deaths',yy): ncN.add(yy); ncD.add(yy)
    if ncN: ny['natch5']=sorted(ncN)
    elif 'natch5' in ny: del ny['natch5']
    if ncD: dy['natch5']=sorted(ncD)
    elif 'natch5' in dy: del dy['natch5']

h2=h[:s]+json.dumps(DATA,ensure_ascii=False,separators=(',',':'))+h[e:]
assert h2.count('const GLOBE=')==1 and h2.count('const DATA=')==1
open(GLOBE,'w',encoding='utf-8').write(h2)
json.dump(DSRC,open('_deaths_sources.json','w'),ensure_ascii=False)
print(f"injected {nd} deaths + {nb} births for the 9 + France")
for iso in ('JPN','CHN','RUS','DEU','FRA'):
    m=DATA[iso]; yy=m['yrs']
    for y in (2024,2025):
        if y not in yy: continue
        k=yy.index(y); b=m['ind']['births'][k]; de=m['ind']['deaths'][k]; nc=m['ind']['natch5'][k]
        dn='NSO' if y in (m.get('nso_yrs',{}).get('deaths') or []) else 'WPP'
        print(f"  {iso} {y}: births={b*1000:,.0f} deaths={de:,.0f}[{dn}] natch={nc:+,.0f}k")
