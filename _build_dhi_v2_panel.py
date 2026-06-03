"""DHI v2.0 full-series engine — every year 1965-2025 from the proper full data.
Fertility baseline = pure WPP; NSO overrides applied per country-year via the
cascade; every country-year stamped WPP or NSO. Projection waypoints
2035/2050/2075/2100 are added by the Stage-C extension.
"""
import json, csv, math
from dhi_scoring import (clip, score_Years_Sub_21,
    score_OADR, score_WRR, score_LFPR, score_Immigrant_Stock)

cache=json.load(open('_indicator_sheets_cache.json'))      # structural, 1950-2100
deriv=json.load(open('_v2_panel_derived.json'))            # dTFR_5y, NatChange_5y, ... 1965-2025
statn=json.load(open('_v2_stationary.json'))               # R4 input, 1965-2050
wpp=json.load(open('_wpp_indicators_1960_2025.json'))      # pure WPP baseline
e65=json.load(open('_wpp_e65.json'))
ap=json.load(open('public/age_pyramid.json'))
regimes=json.load(open('migration_regimes.json'))
names=json.load(open('_country_list.json'))
ISOS=[r['iso'] for r in json.load(open('_dhi_v2_final.json'))]

overrides={}
for r in csv.DictReader(open('overrides/tfr.csv')):
    overrides[(r['iso3'],r['year'])]=float(r['value'])

# ---- v2.0 scoring curves ----
def s_F1(x):
    if x is None: return None
    if x<1.0:  return clip(100*math.exp(-6*(1.0-x)))
    if x<=1.7: return 100.0
    return max(50.0,100-18.5*(x-1.7))
def s_F2(x):
    if x is None: return None
    return clip(45+(x/0.12)*55) if x>=0 else clip(max(0,45+(x/0.25)*45))
def s_R1(x):
    if x is None: return None
    if x<=-10: return 0.0
    if x<0:    return clip((x+10)/10*28)
    if x<=12:  return clip(28+(x/12)*72)
    return clip(max(88,100-(x-12)*0.8))
def s_R2(x):
    if x is None: return None
    return clip(38+(x/0.008)*62) if x>=0 else clip(max(0,38+(x/0.03)*38))
def s_R3(x):
    if x is None: return None
    return clip(32+(x/0.10)*68) if x>=0 else clip(max(0,32+(x/0.12)*32))
def s_R4(x):
    if x is None: return None
    return clip(35+(x/0.9)*65) if x>=0 else clip(max(0,35+(x/0.6)*35))
def s_R5(r): return None if r is None else clip(30+(r-0.7)/0.35*70)
def s_R6(p): return None if p is None else (100.0 if p<=0 else clip(100-(p/0.5)*100))
def s_A4(t): return None if t is None else (100.0 if t<=0 else clip(100-(t/0.18)*100))
def s_M1(b,m):
    if b is None or m is None or b<=0: return None
    rho=m/b
    if rho>=0:
        e=72+rho/0.12*24 if rho<=0.12 else max(10.0,min(96.0,96-(rho-0.12)/0.88*86))
    else:
        e=max(0.0,min(72.0,72-(-rho)/0.60*52))
    return e

W={'Fertility':0.34,'AgeStruct':0.22,'Renewal':0.28,'Migration':0.16}
# per-indicator weights within each pillar (weighted arithmetic mean).
# A4 dropped from Age & Workforce. Migration unified into PIL (was MW).
PIL={'Fertility':{'F1':0.48,'F2':0.29,'F3':0.23},
     'AgeStruct':{'A1':0.45,'A2':0.33,'A3':0.22},
     'Renewal':  {'R1':0.25,'R2':0.22,'R3':0.18,'R4':0.08,'R5':0.15,'R6':0.12},
     'Migration':{'M1':0.55,'M2':0.45}}
def norm(g): return max(0.0,min(100.0,12+(g-20)/80*88))  # g in [20,100] -> [12,100], no top clamp under realistic inputs
TERR={'ABW','AIA','ASM','BES','BLM','BMU','VGB','CYM','COK','CUW','ESH','FLK','FRO','GIB','GLP','GRL','GUF','GUM','GGY','HKG','IMN','JEY','MAC','MAF','MTQ','MYT','MSR','NCL','NIU','MNP','PYF','PRI','REU','SHN','SPM','SXM','TCA','TKL','VIR','WLF'}

def wv(iso,yr,k): return wpp.get(iso,{}).get(str(yr),{}).get(k)
def cohort(iso,yr):
    e=ap.get(iso)
    if not e: return None
    cand=min(e['y'],key=lambda y:abs(y-yr))
    f=e['f'][e['y'].index(cand)]
    return sum(f[0:3])/sum(f[3:6]) if len(f)>=6 and sum(f[3:6])>0 else None
def mpace(iso,yr):
    a=cache.get(iso,{}).get(str(yr-10),{}).get('Median_Age')
    b=cache.get(iso,{}).get(str(yr),{}).get('Median_Age')
    return None if (a is None or b is None) else (b-a)/10
def e65t(iso,yr):
    d=e65.get(iso)
    if not d: return None
    a,b=d.get(str(yr-10)),d.get(str(yr))
    return None if (a is None or b is None) else (b-a)/10
def cval(iso,yr,k): return cache.get(iso,{}).get(str(yr),{}).get(k)
def carry(iso,yr,k,span=6):
    """most-recent available value of cache key k within `span` years back."""
    for dd in range(0,span):
        v=cval(iso,yr-dd,k)
        if v is not None: return v
    return None
def u20share(iso,yr):
    u=cval(iso,yr,'Pop_under20'); p=wv(iso,yr,'TPopulation1July')
    return (u/(p*1000)) if (u is not None and p) else None
def dunder20(iso,yr):
    """5-yr absolute change in under-20 share of total population."""
    a,b=u20share(iso,yr-5),u20share(iso,yr)
    return (b-a) if (a is not None and b is not None) else None
def netmig5(iso,yr):
    """5-yr mean of net migration per 1000."""
    vs=[cval(iso,t,'NetMig') for t in range(yr-4,yr+1)]
    vs=[x for x in vs if x is not None]
    return sum(vs)/len(vs) if len(vs)>=3 else None
def lfgrowth5(iso,yr):
    """R3 — 5-yr growth of the working-age (15-64) population."""
    a,b=cval(iso,yr-5,'WorkAge_15_64'),cval(iso,yr,'WorkAge_15_64')
    return (b/a-1) if (a and b) else None
def eff_tfr(iso,t):
    """effective TFR — NSO override if present, else pure WPP."""
    o=overrides.get((iso,str(t)))
    return o if o is not None else wv(iso,t,'TFR')
def dtfr5_eff(iso,yr):
    """5-yr proportional change in TFR. Endpoints must share provenance — comparing
    an NSO-override year against a pure-WPP year registers the source level-gap as a
    phantom fertility swing — so use the NSO series only when BOTH ends carry an
    override, else the internally-consistent pure-WPP series."""
    oa,ob=overrides.get((iso,str(yr))),overrides.get((iso,str(yr-5)))
    if oa is not None and ob is not None:
        a,b=oa,ob
    else:
        a,b=wv(iso,yr,'TFR'),wv(iso,yr-5,'TFR')
    return ((a-b)/b) if (a is not None and b is not None and b>0) else None
def ysub_eff(iso,yr):
    """count of years (from 1960) with effective TFR below 2.1 — cascade-aware F3."""
    return sum(1 for t in range(1960,yr+1)
               if eff_tfr(iso,t) is not None and eff_tfr(iso,t)<2.1)

def kfor(iso,t):
    """Per-year TFR-override multiplier; 1.0 when no override or for Ukraine
    (which has direct multi-indicator overrides already committed)."""
    if iso=='UKR': return 1.0
    o=overrides.get((iso,str(t)))
    if not o: return 1.0
    tw=wv(iso,t,'TFR')
    return (o/tw) if (tw and tw>0) else 1.0
def extra_b(iso,t):
    """Extra births (thousands) from TFR cascade in year t."""
    k=kfor(iso,t)
    if k==1.0: return 0.0
    b=wv(iso,t,'Births')
    return 0.0 if b is None else b*(k-1)
def nc5_eff(iso,yr):
    """5-yr rolling mean of CBR*k_t - CDR — full cascade across the window."""
    vals=[]
    for t in range(yr-4,yr+1):
        cb=cval(iso,t,'CBR'); cd=cval(iso,t,'CDR')
        if cb is None or cd is None: continue
        vals.append(cb*kfor(iso,t)-cd)
    return sum(vals)/len(vals) if len(vals)==5 else None
def u20share_eff(iso,yr):
    u=cval(iso,yr,'Pop_under20'); p=wv(iso,yr,'TPopulation1July')
    if u is None or p is None: return None
    eu=sum(extra_b(iso,t) for t in range(max(1965,yr-19), yr+1))*1000
    ep=sum(extra_b(iso,t) for t in range(1965,yr)) + 0.5*extra_b(iso,yr)
    return (u+eu)/((p+ep)*1000)
def dunder20_eff(iso,yr):
    a,b=u20share_eff(iso,yr-5),u20share_eff(iso,yr)
    return (b-a) if (a is not None and b is not None) else None

out={}; ncas=0; deg=0; panelS={}
for iso in ISOS:
    reg=regimes.get(iso)
    scores={}; pillars={}; prov={}
    for yr in range(1965,2026):
        sy=str(yr)
        c=cache.get(iso,{}).get(sy,{}); d=deriv.get(iso,{}).get(sy,{})
        # ---- cascade: pure WPP baseline, explicit NSO override ----
        wtfr=wv(iso,yr,'TFR')
        o=overrides.get((iso,sy))
        if o and wtfr and wtfr>0:
            k=o/wtfr; prov[sy]='NSO'; ncas+=1
        else:
            k=1.0; prov[sy]='WPP'
        nrr=wv(iso,yr,'NRR'); nrr_eff=nrr*k if nrr is not None else None
        cbr=c.get('CBR')
        # NatChange_5y: full rolling cascade (not just current-year k adjustment)
        nc5=nc5_eff(iso,yr)
        if nc5 is None: nc5=d.get('NatChange_5y')
        births1000=(cbr*k) if cbr is not None else None
        pop=wv(iso,yr,'TPopulation1July')
        immstk=carry(iso,yr,'Mig_Stock')          # 5-yearly series — carry last known
        immf=(immstk/(pop*1000)) if (immstk is not None and pop) else None
        oadr=c.get('OADR')
        oadr=(oadr/100) if oadr is not None else None   # cache OADR is per-100; score expects fraction
        S={'F1':s_F1(nrr_eff),'F2':s_F2(dtfr5_eff(iso,yr)),
           'F3':score_Years_Sub_21(ysub_eff(iso,yr)),
           'A1':score_OADR(oadr),'A2':score_WRR(c.get('WRR')),
           'A3':score_LFPR(carry(iso,yr,'LFPR')),
           'R1':s_R1(nc5),'R2':s_R2(dunder20_eff(iso,yr)),'R3':s_R3(lfgrowth5(iso,yr)),
           'R4':s_R4(statn.get(iso,{}).get(sy)),'R5':s_R5(cohort(iso,yr)),'R6':s_R6(mpace(iso,yr)),
           'M1':s_M1(births1000,netmig5(iso,yr)),
           'M2':score_Immigrant_Stock(immf,reg)}
        # weighted arithmetic mean within each pillar
        pil={}; ok=True
        for p,weights in PIL.items():
            pairs=[(S[x],weights[x]) for x in weights if S[x] is not None]
            if not pairs: ok=False; break
            pil[p]=sum(v*w for v,w in pairs)/sum(w for _,w in pairs)
            if len(pairs)<len(weights): deg+=1
        if not ok: continue
        # weighted ARITHMETIC mean across the four pillars
        scores[sy]=round(sum(W[p]*pil[p] for p in W),2)
        pillars[sy]={k2:round(v,1) for k2,v in pil.items()}
        if yr==2025: panelS[iso]=dict(S)
    if scores:
        out[iso]={'iso':iso,'name':names.get(iso,iso),'sov':iso not in TERR,
                  'scores':scores,'pillars':pillars,'prov':prov}
json.dump(panelS,open('_panel_S_2025.json','w'),separators=(',',':'))
json.dump({'countries':out,'years':list(range(1965,2026)),
           'meta':{'vintage':'DHI v2.0','built':'full-series engine',
                   'baseline':'WPP 2024','overrides':'NSO TFR cascade'}},
          open('dhi_data_v2_unified.json','w'),separators=(',',':'))
nyr=sum(len(c['scores']) for c in out.values())
print(f'v2.0 full-series engine — {len(out)} countries, {nyr} country-years (1965-2025)')
print(f'NSO override cells via cascade: {ncas}   degraded pillar-cells: {deg}')
for iso in ['GBR','USA','CHN','JPN','NER','DEU','KOR']:
    c=out.get(iso,{}).get('scores',{})
    print(f"  {iso}: 1965={c.get('1965')}  1995={c.get('1995')}  2025={c.get('2025')}")
