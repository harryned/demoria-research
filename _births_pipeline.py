#!/usr/bin/env python3
"""
Demoria Research — Birth Tracker NSO pipeline.

Run monthly. Pulls live monthly births, computes the same-period year-on-year
comparison for TARGET_YEAR vs TARGET_YEAR-1, and merges the result into
public/births_data.json (fields b25, b26, mon, births_source).

The page frames the current year as 2026, so TARGET_YEAR=2026: a country is
populated only once its 2026 monthly births are published (with matching 2025
months). Until then it stays blank and the card shows "awaiting release".

Primary source : Eurostat demo_fmonth  — one API, ~37 European countries.
Extensible     : add per-NSO fetchers in NONEU_FETCHERS for Korea/Japan/US/etc.

Usage:
  python3 _births_pipeline.py            # dry run: print what would update
  python3 _births_pipeline.py --write    # merge into public/births_data.json
"""
import json, urllib.request, sys

TARGET_YEAR = 2026                 # roll forward to 2027… in future years
PREV_YEAR   = TARGET_YEAR - 1
DATA_PATH   = 'public/births_data.json'

def get(url):
    req=urllib.request.Request(url, headers={'User-Agent':'DemoriaResearch/1.0'})
    with urllib.request.urlopen(req, timeout=40) as r:
        return json.loads(r.read().decode('utf-8'))

EU2ISO3={'AT':'AUT','BE':'BEL','BG':'BGR','HR':'HRV','CY':'CYP','CZ':'CZE','DK':'DNK','EE':'EST',
'FI':'FIN','FR':'FRA','DE':'DEU','EL':'GRC','HU':'HUN','IS':'ISL','IE':'IRL','IT':'ITA','LV':'LVA',
'LT':'LTU','LU':'LUX','MT':'MLT','NL':'NLD','NO':'NOR','PL':'POL','PT':'PRT','RO':'ROU','SK':'SVK',
'SI':'SVN','ES':'ESP','SE':'SWE','CH':'CHE','UK':'GBR','RS':'SRB','ME':'MNE','MK':'MKD','AL':'ALB',
'TR':'TUR','GE':'GEO','AM':'ARM','AZ':'AZE','MD':'MDA','UA':'UKR'}
MONTHS=['M01','M02','M03','M04','M05','M06','M07','M08','M09','M10','M11','M12']

def fetch_eurostat():
    """Return {iso3: {prev, cur, months}} for TARGET_YEAR vs PREV_YEAR (leading run from Jan)."""
    base="https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/demo_fmonth"
    geos='&'.join('geo=%s'%g for g in EU2ISO3)
    d=get(f"{base}?format=JSON&lastTimePeriod=4&{geos}")
    if 'error' in d:
        print("Eurostat error:",d['error']); return {}
    dim=d['dimension']; size=d['size']; order=d['id']
    idx={k:dim[k]['category']['index'] for k in order}
    strides={}; s=1
    for k in reversed(order): strides[k]=s; s*=size[order.index(k)]
    f0=list(idx['freq'])[0]; u0=list(idx['unit'])[0]; val=d['value']
    def at(month,geo,year):
        y=str(year)
        if month not in idx['month'] or geo not in idx['geo'] or y not in idx['time']: return None
        coord={'freq':f0,'unit':u0,'month':month,'geo':geo,'time':y}
        pos=sum(idx[k][coord[k]]*strides[k] for k in order)
        return val.get(str(pos))
    out={}
    for geo,iso3 in EU2ISO3.items():
        run=[]
        for m in MONTHS:
            if at(m,geo,TARGET_YEAR) is not None and at(m,geo,PREV_YEAR) is not None: run.append(m)
            else: break
        if not run: continue
        out[iso3]={'prev':int(sum(at(m,geo,PREV_YEAR) for m in run)),
                   'cur':int(sum(at(m,geo,TARGET_YEAR) for m in run)),
                   'months':len(run),'source':'Eurostat demo_fmonth'}
    return out

# ── Non-EU NSO fetchers (add as built). Each returns {iso3:{prev,cur,months,source}} ──
def fetch_korea():   return {}   # TODO KOSIS API (key)  — KOR
def fetch_japan():   return {}   # TODO e-Stat API (key) — JPN
def fetch_us():      return {}   # TODO CDC WONDER / provisional — USA
def fetch_taiwan():  return {}   # TODO MOI monthly — TWN
NONEU_FETCHERS=[fetch_korea,fetch_japan,fetch_us,fetch_taiwan]

def collect():
    res=dict(fetch_eurostat())
    for fn in NONEU_FETCHERS:
        try: res.update(fn() or {})
        except Exception as e: print(f"  {fn.__name__} failed: {e}")
    return res

def merge(res, write=False):
    data=json.load(open(DATA_PATH,encoding='utf-8'))
    by={c['iso']:c for c in data['countries']}
    updated=[]
    for iso,r in res.items():
        c=by.get(iso)
        if not c: continue
        c['b25']=r['prev']; c['b26']=r['cur']; c['mon']=r['months']; c['births_source']=r['source']
        updated.append((iso,r))
    if write and updated:
        data['updated']=__import__('datetime').date.today().isoformat()
        json.dump(data,open(DATA_PATH,'w',encoding='utf-8'),ensure_ascii=False,separators=(',',':'))
    return updated

if __name__=='__main__':
    write='--write' in sys.argv
    res=collect()
    print(f"\nTarget {TARGET_YEAR} vs {PREV_YEAR}. Sources returned {len(res)} countries with current-year data.")
    upd=merge(res, write=write)
    if not upd:
        print(f"No {TARGET_YEAR} monthly births published yet — nothing to write. Cards stay 'awaiting release'.")
    else:
        print(f"\n{'(WROTE)' if write else '(dry run)'} {len(upd)} countries:")
        for iso,r in sorted(upd,key=lambda x:(x[1]['cur']-x[1]['prev'])/x[1]['prev']):
            chg=(r['cur']-r['prev'])/r['prev']*100
            print(f"  {iso}  {r['cur']:>10,} vs {r['prev']:>10,}  ({r['months']}mo)  {chg:+.1f}%")
        if not write: print("\nRe-run with --write to merge into "+DATA_PATH)
