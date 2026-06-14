#!/usr/bin/env python3
"""Full-NSO upgrade: inject national DEATHS (and pre-2023 national births) from
the Wikipedia vital-statistics scrape (_nso_births_deaths.json), so
births/deaths/natural-change are national, not UN WPP.

Rules:
  * deaths 2005-2025: scrape value where sane (0.5x-2x WPP) -> NSO + source
  * births <=2022: scrape value where sane (the curated sheet already covers
    2023-2025, kept as-is)
  * natural change recomputed single-year from displayed columns; tagged NSO
    when both births & deaths are national, DRE when national meets UN.
Skips Moldova & Ukraine (curated national series already in place).
Idempotent; rerun after re-scraping."""
import json, shutil
GLOBE='dhi_globe.html'; shutil.copy(GLOBE,GLOBE+'.bak_deaths')
WPP=json.load(open('_wpp_indicators_1960_2025.json'))
SCR=json.load(open('_nso_births_deaths.json'))
PRESERVE={'MDA','UKR'}
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

DSRC={}; nd=nb=0; countries=0
for iso,rec in SCR.items():
    if iso in PRESERVE or iso not in DATA: continue
    if rec.get('status')!='ok' or not rec.get('rows'): continue
    m=DATA[iso]; yrs=m['yrs']; ny=m.setdefault('nso_yrs',{}); dy=m.setdefault('dre_yrs',{})
    dl=set(ny.get('deaths',[])); bl=set(ny.get('births',[]))
    touched=False
    for row in rec['rows']:
        try: yy=int(row[0]); bv=row[1]; dv=row[2]
        except: continue
        if yy not in yrs or yy<2005: continue
        idx=yrs.index(yy)
        # deaths
        wD=wd(iso,yy)
        if isinstance(dv,(int,float)) and dv>0 and wD and 0.5*wD<=dv<=2*wD:
            m['ind']['deaths'][idx]=round(dv); dl.add(yy); nd+=1; touched=True
        # births: history only (<=2022); curated sheet keeps 2023-2025
        if yy<=2022 and isinstance(bv,(int,float)) and bv>0:
            wB=wb(iso,yy)
            if wB and 0.5*wB<=bv/1000<=2*wB:
                m['ind']['births'][idx]=round(bv/1000,3); bl.add(yy); nb+=1
    if touched:
        ny['deaths']=sorted(dl); ny['births']=sorted(bl); countries+=1
        DSRC[iso]=rec.get('slug','')

# recompute single-year natural change + retag everywhere
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
print(f"injected {nd} national deaths + {nb} historical births across {countries} countries")
for iso in ('FRA','USA','KOR','ITA','ESP'):
    m=DATA[iso]; yy=m['yrs']
    for y in (2023,2024):
        k=yy.index(y); b=m['ind']['births'][k]; de=m['ind']['deaths'][k]; nc=m['ind']['natch5'][k]
        dnso=y in (m.get('nso_yrs',{}).get('deaths') or [])
        print(f"  {iso} {y}: births={b*1000:,.0f} deaths={de:,.0f}[{'NSO' if dnso else 'WPP'}] natch={nc:+.1f}k")
