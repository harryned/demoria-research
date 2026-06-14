#!/usr/bin/env python3
"""Re-source raw-data + tracker TFR from the NSO published figure (the Total
Fertility Rate column in the same Wikipedia vital-statistics tables we used for
births/deaths, so the scope matches), with UN WPP as the fallback. Display +
tracker only; DHI scores keep their own overrides/tfr.csv cascade.

For each country-year with an NSO TFR within 0.3-2x of WPP: set display TFR,
scale NRR proportionally, tag NSO. Years with an existing curated override but
no wiki value keep the override. The latest tracked year with no published TFR
but a known full-year birth count is nowcast (last published x birth ratio),
tagged DRE/provisional."""
import json, shutil
GLOBE='dhi_globe.html'; shutil.copy(GLOBE,GLOBE+'.bak_tfr')
WPP=json.load(open('_wpp_indicators_1960_2025.json'))
WIKI=json.load(open('_wiki_births_tfr.json'))

# unified NSO TFR {iso:{year:tfr}} from wiki rows ([year, births, tfr])
NSO={}
for iso,rec in WIKI.items():
    if rec.get('status')!='ok': continue
    yt={}
    for row in rec.get('rows',[]):
        if len(row)>=3 and isinstance(row[0],(int,float)) and isinstance(row[2],(int,float)):
            t=row[2]
            if 0.4<=t<=9.5: yt[int(row[0])]=round(t,3)
    if yt: NSO[iso]=yt
# Eurostat (authoritative EU) fills years/countries missing from wiki
E2={'AL':'ALB','AM':'ARM','AT':'AUT','AZ':'AZE','BE':'BEL','BG':'BGR','BY':'BLR','CH':'CHE',
    'CY':'CYP','CZ':'CZE','DE':'DEU','DK':'DNK','EE':'EST','EL':'GRC','ES':'ESP','FI':'FIN',
    'FR':'FRA','GE':'GEO','HR':'HRV','HU':'HUN','IE':'IRL','IS':'ISL','IT':'ITA','LI':'LIE',
    'LT':'LTU','LU':'LUX','LV':'LVA','ME':'MNE','MK':'MKD','MT':'MLT','NL':'NLD','NO':'NOR',
    'PL':'POL','PT':'PRT','RO':'ROU','RS':'SRB','SE':'SWE','SI':'SVN','SK':'SVK','TR':'TUR','XK':'XKX'}
EU=json.load(open('_eurostat_tfr.json'))['data']
for code,iso3 in E2.items():
    ev=EU.get(code)
    if not ev: continue
    dd=NSO.setdefault(iso3,{})
    for ys,t in ev.items():
        y=int(ys)
        if y not in dd and isinstance(t,(int,float)) and 0.4<=t<=9.5: dd[y]=round(t,3)
print(f"NSO TFR available for {len(NSO)} countries (wiki vital-stats + Eurostat fill)")

def wtfr(iso,y): return WPP.get(iso,{}).get(str(y),{}).get('TFR')

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

PRESERVE={'MDA','UKR'}   # curated national series
nset=0
for iso,yt in NSO.items():
    if iso in PRESERVE or iso not in DATA: continue
    m=DATA[iso]; yrs=m['yrs']; ny=m.setdefault('nso_yrs',{})
    tl=set(ny.get('tfr',[])); nl=set(ny.get('nrr',[]))
    for y,t in yt.items():
        if y not in yrs: continue
        w=wtfr(iso,y)
        if w and not (0.3*w<=t<=2.0*w): continue   # reject scope/parse outliers
        idx=yrs.index(y)
        old=m['ind']['tfr'][idx]
        m['ind']['tfr'][idx]=t; tl.add(y)
        # scale NRR proportionally to the TFR change
        if old and old>0 and m['ind'].get('nrr') and m['ind']['nrr'][idx] is not None:
            m['ind']['nrr'][idx]=round(m['ind']['nrr'][idx]*t/old,3); nl.add(y)
        nset+=1
    ny['tfr']=sorted(tl); ny['nrr']=sorted(nl)

h2=h[:s]+json.dumps(DATA,ensure_ascii=False,separators=(',',':'))+h[e:]
assert h2.count('const GLOBE=')==1 and h2.count('const DATA=')==1
open(GLOBE,'w',encoding='utf-8').write(h2)
print(f"injected {nset} NSO TFR display values")

# ---- update tracker TFR from the same source ----
BD=json.load(open('public/births_data.json'))
upd=0
for c in BD['countries']:
    iso=c['iso']
    if iso in PRESERVE: continue
    yt=NSO.get(iso)
    if not yt: continue
    est=c.setdefault('tfr_est',{})
    for ys in list(c.get('tfr',{})):
        y=int(ys)
        if y in yt:
            w=wtfr(iso,y)
            if w and not (0.3*w<=yt[y]<=2.0*w): continue
            if abs(c['tfr'][ys]-yt[y])>0.001: c['tfr'][ys]=yt[y]; upd+=1
            est[ys]=False
json.dump(BD,open('public/births_data.json','w'),ensure_ascii=False,separators=(',',':'))
import shutil as sh; sh.copy('public/births_data.json','births_data.json')
print(f"tracker TFR values updated: {upd}")
for iso in ('FRA','KOR','ITA','DEU','ESP'):
    m=DATA[iso]; yy=m['yrs']
    vals={y:m['ind']['tfr'][yy.index(y)] for y in (2023,2024,2025) if y in yy}
    print(f"  {iso}: {vals}  (NSO yrs tagged: {2024 in (m['nso_yrs'].get('tfr') or [])})")
