#!/usr/bin/env python3
"""Fill births for countries with NO nationally-reported figures using UN WPP 2024.
Uses DATA's own 2024->2025 births (both years carry identical DHI/override treatment,
so the year-on-year change is clean — unlike crossing into the PROJD projection blob,
which reverts overrides and invents jumps). Tagged so the page marks them as forecasts.
NSO countries (b26 or ba present) are left untouched and never get a wpp block."""
import json

GLOBE='dhi_globe.html'; DATA_PATH='public/births_data.json'
h=open(GLOBE,encoding='utf-8').read()
def blob(name):
    i=h.find(name); s=i+len(name); d=0;p=s
    while p<len(h):
        c=h[p]
        if c=='{': d+=1
        elif c=='}':
            d-=1
            if d==0: return json.loads(h[s:p+1])
        p+=1
DATA=blob('const DATA=')

bd=json.load(open(DATA_PATH,encoding='utf-8'))
filled=0; skipped_nso=0
for c in bd['countries']:
    if c.get('b26') is not None or c.get('ba'):       # has national data -> keep, no wpp
        c.pop('wpp',None); skipped_nso+=1; continue
    d=DATA.get(c['iso'])
    if not d or not d.get('ind',{}).get('births'):
        c.pop('wpp',None); continue
    yrs=d['yrs']
    if 2024 not in yrs or 2025 not in yrs: continue
    b24=round(d['ind']['births'][yrs.index(2024)]*1000)
    b25=round(d['ind']['births'][yrs.index(2025)]*1000)
    if b24<=0 or b25<=0: continue
    c['wpp']={'prev':b24,'cur':b25,'year':2025}       # UN WPP 2024 projection, 2024 -> 2025
    filled+=1

bd['wpp_note']='Countries without nationally-reported births show UN WPP 2024 medium-variant projections (forecasts, not national counts).'
json.dump(bd,open(DATA_PATH,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
print(f"WPP-filled: {filled} | NSO kept: {skipped_nso} | total: {len(bd['countries'])}")
