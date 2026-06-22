#!/usr/bin/env python3
"""Demographic 'cliff' engine — convert births + age structure into the
forward cohort metrics a buyer budgets around. Birth-cohort cliffs run on the
NSO births series (observed, near-certain) + WPP forecast births for future
birth-years; structural cliffs (workers, 80+) run on the age pyramid.
Output: public/cliffs_data.json."""
import json
h=open('dhi_globe.html',encoding='utf-8').read()
def blob(name,end):
    i=h.find(name); s=i+len(name); return json.loads(h[s:h.find(end,s)])
DATA=blob('const DATA=',';const FCAGE=')
G={v['iso']:v for v in blob('const GLOBE=',';const HCX=').values() if isinstance(v,dict) and v.get('iso')}
FC=json.load(open('_wpp_forecast_cache.json'))
AP=json.load(open('public/age_pyramid.json'))

def births_series(iso):
    """absolute births by year: NSO 1965-2025 (blob, in K) + WPP forecast 2026-2100 (K)."""
    out={}
    d=DATA.get(iso)
    if d:
        for i,y in enumerate(d['yrs']):
            b=d['ind']['births'][i]
            if b is not None: out[y]=b*1000
    for ys,rec in FC.get(iso,{}).items():
        y=int(ys)
        if y>2025 and isinstance(rec,dict) and rec.get('Births') is not None:
            out[y]=rec['Births']*1000
    return out

def pyr_cohort(iso,lo_band,hi_band):
    """sum m+f over 5-yr age bands [lo_band..hi_band] -> {year: persons}. bands: 0=0-4,...,16=80-84,20=100+. values in thousands."""
    e=AP.get(iso)
    if not e: return {}
    out={}
    for i,y in enumerate(e['y']):
        tot=0
        for b in range(lo_band,hi_band+1):
            if b<len(e['m'][i]): tot+=(e['m'][i][b]+e['f'][i][b])
        out[y]=tot*1000
    return out

def cohort_from_births(B,a1,a2,Ys,Ye):
    """cohort aged [a1,a2] in year Y = sum of births in (Y-a2..Y-a1). near-certain while Y-a1<=2025."""
    out={}
    for Y in range(Ys,Ye+1):
        bys=[Y-a for a in range(a1,a2+1)]
        vals=[B[by] for by in bys if by in B]
        if len(vals)==len(bys): out[Y]=sum(vals)
    return out

def metric(series, certain_to=None):
    if not series: return None
    yrs=sorted(series)
    horizon=[y for y in yrs if (certain_to is None or y<=certain_to)] or yrs
    # peak & end both within the certain horizon, so growing countries don't
    # show a false 'decline' against a peak that lies beyond the locked-in window
    pk=max(horizon,key=lambda y:series[y]); pkv=series[pk]
    end=max(horizon); endv=series[end]
    pct=round((endv-pkv)/pkv*100,1) if pkv else None
    return {'series':{str(y):round(series[y]) for y in yrs},
            'peak':[pk,round(pkv)],'end':[end,round(endv)],'pct':pct,
            'certainTo':certain_to}

out={}
for iso,d in DATA.items():
    B=births_series(iso)
    if not B: continue
    name=d['name']; pop=G.get(iso,{}).get('pop',0) or 0
    # certainty horizon for an age-a cohort = 2025 + a (last observed birth-year is 2025)
    cliffs={}
    # Start every window in 1965 (earliest observed birth-year / pyramid year) so the
    # chart shows the TRUE historical peak, not a false one pinned to the window start.
    # cohort_from_births auto-clamps to the first fully-computable year for each age band
    # (5yo->1970, 18yo->1983, 18-25->1990, 28-35->2000), which is as far back as the
    # 1965 births floor allows.
    # baby economy — annual births
    cliffs['baby']=metric({y:B[y] for y in B if 1965<=y<=2050}, certain_to=2025)
    # kindergarten — 5-year-olds
    cliffs['kindergarten']=metric(cohort_from_births(B,5,5,1965,2040), certain_to=2030)
    # higher-ed — 18-year-olds
    cliffs['higher_ed']=metric(cohort_from_births(B,18,18,1965,2055), certain_to=2043)
    # manpower — 18-25
    cliffs['manpower']=metric(cohort_from_births(B,18,25,1965,2055), certain_to=2043)
    # first-home — 28-35
    cliffs['first_home']=metric(cohort_from_births(B,28,35,1965,2060), certain_to=2053)
    # peak workers — 15-64 (bands 3..12), structural; decline measured to 2050
    pw={y:v for y,v in pyr_cohort(iso,3,12).items() if 1965<=y<=2060}
    if pw:
        yrs=sorted(pw); pk=max(yrs,key=lambda y:pw[y]); v50=pw.get(2050,pw[max(yrs)])
        cliffs['peak_workers']={'series':{str(y):round(pw[y]) for y in yrs},'peak':[pk,round(pw[pk])],
                                'v2050':round(v50),'pct':round((v50-pw[pk])/pw[pk]*100,1) if pw[pk] else None}
    # silver tsunami — 80+ (bands 16..20), structural
    sv=pyr_cohort(iso,16,20)
    if sv:
        ratio = round(sv.get(2050,0)/sv[2025],2) if sv.get(2025) else None
        cliffs['silver']={'series':{str(y):round(v) for y,v in sv.items() if 2000<=y<=2060},
                          'v2025':round(sv.get(2025,0)),'v2050':round(sv.get(2050,0)),'mult':ratio}
    out[iso]={'name':name,'cont':G.get(iso,{}).get('cont',''),'pop':round(pop,1),'cliffs':cliffs}

json.dump(out,open('public/cliffs_data.json','w'),separators=(',',':'))
print(f"cliffs computed for {len(out)} countries")
# verification
for iso in ('USA','KOR','JPN','CHN'):
    c=out[iso]['cliffs']
    he=c['higher_ed']; bb=c['baby']; pw=c['peak_workers']; sv=c.get('silver',{})
    print(f"\n{iso}:")
    print(f"  higher-ed 18yo: peak {he['peak']} -> {he['end']} ({he['pct']}%)  certain to {he['certainTo']}")
    print(f"  baby births: peak {bb['peak']} -> {bb['end']} ({bb['pct']}%)")
    print(f"  peak workers 15-64: peak {pw['peak']} -> 2050 {pw['series'].get('2050')} ({pw['pct']}%)")
    print(f"  silver 80+: 2025={sv.get('v2025'):,} -> 2050={sv.get('v2050'):,} (x{sv.get('mult')})")
