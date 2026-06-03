"""DHI v2.0 build — 16 indicators, 4 pillars, weighted geometric mean.
Migration M1 = Option B 'earned-100' engagement curve (no NRR link).
Reads _dhi_raw_indicators.json via apply_cascade (cascade-applied 2025 panel).
"""
import json, math, statistics, importlib
import dhi_rescore; importlib.reload(dhi_rescore)
from dhi_rescore import apply_cascade, RAW
from dhi_scoring import compute_scores, clip

regimes=json.load(open('migration_regimes.json'))
names=json.load(open('_country_list.json'))
ap=json.load(open('public/age_pyramid.json'))
wpp=json.load(open('_wpp_indicators_2010_2025.json'))
e65=json.load(open('_wpp_e65.json'))
casc=json.load(open('_cascade_applied_2025.json'))   # cascade-applied births/1000
prev={r['iso']:r for r in json.load(open('_dhi_v2_final.json'))}

def s_F1(x):
    if x is None: return None
    if x<1.0:  return clip(100*math.exp(-4*(1.0-x)))
    if x<=1.3: return 100.0
    return max(30.0,100-58.3*(x-1.3))
def s_F2(x):
    if x is None: return None
    return clip(45+(x/0.20)*55) if x>=0 else clip(max(0,45+(x/0.25)*45))
def s_R1(x):
    if x is None: return None
    if x<=-10: return 0.0
    if x<0:    return clip((x+10)/10*28)
    if x<=18:  return clip(28+(x/18)*72)
    return clip(max(88,100-(x-18)*0.8))
def s_R2(x):
    if x is None: return None
    return clip(38+(x/0.012)*62) if x>=0 else clip(max(0,38+(x/0.03)*38))
def s_R3(x):
    if x is None: return None
    return clip(32+(x/0.14)*68) if x>=0 else clip(max(0,32+(x/0.12)*32))
def s_R4(x):
    if x is None: return None
    return clip(35+(x/0.9)*65) if x>=0 else clip(max(0,35+(x/0.6)*35))
def s_R5(r): return None if r is None else clip(30+(r-0.7)/0.45*70)
def s_R6(p): return None if p is None else (100.0 if p<=0 else clip(100-(p/0.5)*100))
def s_A4(t): return None if t is None else (100.0 if t<=0 else clip(100-(t/0.18)*100))

def s_M1(b,m):
    """Option B — 'earned-100' migration-engagement curve.
    rho = net migration / births. Zero migration -> neutral 72;
    sensible net inflow (peak rho ~0.12) earns up to 96;
    inflow beyond that, and emigration, are penalised. No NRR coupling."""
    if b is None or m is None or b<=0: return None
    rho=m/b
    if rho>=0:
        e=72+rho/0.12*24 if rho<=0.12 else max(10.0,min(96.0,96-(rho-0.12)/0.88*86))
    else:
        e=max(0.0,min(72.0,72-(-rho)/0.60*52))
    return e

def cohort(iso):
    e=ap.get(iso)
    if not e or 2025 not in e['y']: return None
    f=e['f'][e['y'].index(2025)]
    return sum(f[0:3])/sum(f[3:6]) if len(f)>=6 and sum(f[3:6])>0 else None
def mpace(iso):
    w=wpp.get(iso)
    if not w: return None
    a,b=w.get('2015',{}).get('MedianAgePop'),w.get('2025',{}).get('MedianAgePop')
    return None if (a is None or b is None) else (b-a)/10
def e65t(iso):
    d=e65.get(iso)
    if not d: return None
    a,b=d.get('2015'),d.get('2025')
    return None if (a is None or b is None) else (b-a)/10

W={'Fertility':0.34,'AgeStruct':0.22,'Renewal':0.28,'Migration':0.16}
PIL_EQ={'Fertility':['F1','F2','F3','F4'],'AgeStruct':['A1','A2','A3','A4'],'Renewal':['R1','R2','R3','R4','R5','R6']}
MW={'M1':0.55,'M2':0.45}
def norm(g): return max(0.0,min(100.0,12+(g-20)/70*86))
TERR={'ABW','AIA','ASM','BES','BLM','BMU','VGB','CYM','COK','CUW','ESH','FLK','FRO','GIB','GLP','GRL','GUF','GUM','GGY','HKG','IMN','JEY','MAC','MAF','MTQ','MYT','MSR','NCL','NIU','MNP','PYF','PRI','REU','SHN','SPM','SXM','TCA','TKL','VIR','WLF'}

rows=[]
for iso in RAW:
    base=RAW[iso].get('2025')
    if not base: continue
    eff,changed,k,basis=apply_cascade(iso,2025,base)
    if 'LFPR' not in eff and RAW[iso].get('2024',{}).get('LFPR') is not None:
        eff=dict(eff); eff['LFPR']=RAW[iso]['2024']['LFPR']
    ind,cat,v11=compute_scores(eff,regimes.get(iso))
    s={'F1':s_F1(eff.get('NRR')),'F2':s_F2(eff.get('∆_TFR_5yr')),'F3':ind.get('Years_Sub_2.1'),'F4':None,
       'A1':ind.get('OADR'),'A2':ind.get('WRR (20-29/60-69)'),'A3':ind.get('LFPR'),'A4':s_A4(e65t(iso)),
       'R1':s_R1(eff.get('NatChange_per_1000_5y_avg')),'R2':s_R2(eff.get('∆_pop_under20_5yr')),
       'R3':s_R3(eff.get('Labour_Force_Growth_%5yrs')),'R4':s_R4(eff.get('Stationary_vs_Total')),
       'R5':s_R5(cohort(iso)),'R6':s_R6(mpace(iso)),
       'M1':s_M1(casc.get(iso,{}).get('Births_per_1000'),eff.get('Net_Mig_per_1000_5y_avg')),
       'M2':ind.get('Immigrant_Stock_%')}
    ma,tb=ind.get('Mean_Age_Childbearing'),ind.get('Teen_Birth_Share_%')
    if ma is not None and tb is not None: s['F4']=(ma+tb)/2
    pillar={}; ok=True
    for p,codes in PIL_EQ.items():
        vals=[s[c] for c in codes if s[c] is not None]
        if not vals: ok=False; break
        pillar[p]=sum(vals)/len(vals)
    mv=[(s[c],MW[c]) for c in ('M1','M2') if s[c] is not None]
    if not mv: ok=False
    else: pillar['Migration']=sum(v*w for v,w in mv)/sum(w for _,w in mv)
    if not ok: continue
    geo=math.exp(sum(W[p]*math.log(max(pillar[p],5)) for p in W))
    pop=wpp.get(iso,{}).get('2025',{}).get('TPopulation1July')
    rows.append({'iso':iso,'name':names.get(iso,iso),'final':round(norm(geo),1),
                 'pillars':{k2:round(v,1) for k2,v in pillar.items()},
                 'sov':iso not in TERR,'pop_m':round(pop/1000,3) if pop else None})
rows.sort(key=lambda r:-r['final'])
for i,r in enumerate(rows,1): r['rank']=i
json.dump(rows,open('_dhi_v2_final.json','w'),separators=(',',':'))

N=len(rows); fs=sorted(r['final'] for r in rows)
print(f"v2.0 REBUILT (Migration Option B) — {N} countries")
print(f"  distribution: min {fs[0]:.1f}  median {statistics.median(fs):.1f}  max {fs[-1]:.1f}  span {fs[-1]-fs[0]:.1f}")
mig=sorted(r['pillars']['Migration'] for r in rows)
print(f"  Migration pillar: min {mig[0]:.1f}  median {statistics.median(mig):.1f}  max {mig[-1]:.1f}  =100:{sum(x>=99.5 for x in mig)}  >=90:{sum(x>=90 for x in mig)}")
for iso in ['GBR','USA','CHN','KOR','JPN','DEU','NGA','IND']:
    r=[x for x in rows if x['iso']==iso][0]; p=prev.get(iso,{})
    print(f"  {iso}: {p.get('final','?')} (rank {p.get('rank','?')}) -> {r['final']} (rank {r['rank']})   Migration {p.get('pillars',{}).get('Migration','?')}->{r['pillars']['Migration']}")
