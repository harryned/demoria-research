"""Build a compact per-year (1965-2025) Human-Capital series blob for the Raw
Data explorer, interpolated from the 5-yearly Wittgenstein source, and embed it
into dhi_globe.html as `const HCX=...;` right after `const GLOBE=...;`.

Fields surfaced (raw values, explorer-appropriate):
  mysf  mean years schooling, women 20-39   (mys_20_39_F)
  myst  mean years schooling, adults 25+    (mys_25p_T)
  upps  upper-secondary attainment, 25+ (%) (uppsec_25p_T)
  ggap  schooling gender gap, 25+ (years)   (ggap_mys_25p)
Only the 236 ISOs the explorer actually shows are included."""
import json, re

DATA_ISOS = "UZB,SLB,GNQ,KIR,TKM,BEN,MDG,VUT,NGA,COG,GHA,ISR,LBR,NAM,KEN,KGZ,CIV,PSE,PNG,KHM,GAB,TGO,RWA,BDI,CMR,MYT,ERI,AGO,ZWE,PAK,EGY,TZA,BWA,ETH,MOZ,SEN,TJK,COM,GIN,GNB,COD,HTI,IRQ,GMB,BFA,MNG,MLI,WSM,TLS,ZMB,LAO,MWI,SLE,YEM,KAZ,SSD,NRU,UGA,DZA,SDN,TCD,ZAF,NER,LSO,MRT,TUV,MHL,CAF,TON,IDN,LBY,FJI,PER,GUF,FSM,ESH,AFG,STP,SOM,DJI,BOL,GUY,SWZ,MMR,BGD,PRY,LBN,SUR,GTM,NIU,FRO,VEN,IND,GUM,HND,VNM,PAN,SYR,MAR,NIC,SAU,ECU,PHL,NCL,CPV,NPL,SLV,BLZ,PRK,JOR,REU,ATG,DOM,MDA,MEX,GRL,GEO,ARM,SYC,MDV,BTN,ASM,BRA,NZL,BHS,BRB,MYS,ARG,TUR,GIB,PLW,LCA,IRN,BRN,TTO,LKA,USA,KNA,CYP,VCT,AZE,TUN,MNE,COK,MAF,TKL,GRD,JAM,URY,COL,BGR,PYF,CUW,DMA,ISL,MUS,OMN,RUS,AUS,SVK,GBR,CRI,NOR,ROU,FRA,DNK,JEY,TCA,FLK,SWE,NLD,SRB,SVN,BEL,MNP,ALB,XKX,HRV,THA,GGY,CHL,MKD,CAN,HUN,WLF,ABW,IMN,FIN,MCO,IRL,CZE,AUT,LVA,CHN,DEU,SPM,BLR,PRT,BHR,QAT,POL,AIA,CUB,LTU,SHN,KWT,MSR,ARE,EST,GLP,JPN,BES,BLM,ESP,CHE,BIH,CYM,LIE,UKR,VGB,ITA,MTQ,LUX,VIR,KOR,MLT,SXM,GRC,BMU,PRI,TWN,AND,SMR,SGP,HKG,MAC".split(',')

hc = json.load(open('_human_capital.json'))['countries']
FIELDS = [('mysf','mys_20_39_F',2),('myst','mys_25p_T',2),('upps','uppsec_25p_T',1),('ggap','ggap_mys_25p',2)]
TARGET = list(range(1965, 2026))   # 61 yearly points

def interp_series(cy, field):
    # cy: dict {yearstr: {field:val}}; source years are 5-yearly ints
    pts = sorted((int(y), rec.get(field)) for y, rec in cy.items() if rec.get(field) is not None)
    if not pts: return None
    out = []
    for ty in TARGET:
        # clamp to endpoints
        if ty <= pts[0][0]: out.append(pts[0][1]); continue
        if ty >= pts[-1][0]: out.append(pts[-1][1]); continue
        # find bracketing source years
        for i in range(1, len(pts)):
            y1, v1 = pts[i-1]; y2, v2 = pts[i]
            if y1 <= ty <= y2:
                v = v1 + (v2 - v1) * (ty - y1) / (y2 - y1)
                out.append(v); break
    return out

blob, missing, partial = {}, [], []
for iso in DATA_ISOS:
    cy = hc.get(iso)
    if not cy: missing.append(iso); continue
    rec = {}
    for key, field, nd in FIELDS:
        s = interp_series(cy, field)
        if s is not None:
            rec[key] = [round(v, nd) for v in s]
    if rec: blob[iso] = rec
    if len(rec) < len(FIELDS): partial.append(iso)

js = 'const HCX=' + json.dumps(blob, separators=(',', ':')) + ';'
print(f'covered={len(blob)}/{len(DATA_ISOS)}  missing={missing}  partial_fields={partial}')
print(f'blob bytes={len(js):,}')

# embed right after the GLOBE blob terminator `;const PYR=` ... actually inject as its
# own const just before `;const PYR=` so it sits alongside GLOBE in the same script.
h = open('dhi_globe.html').read()
# Remove any prior HCX embed (idempotent)
h = re.sub(r'const HCX=\{.*?\};', '', h, count=1, flags=re.S)
marker = ';const PYR='
idx = h.find(marker)
assert idx > 0, 'PYR marker not found'
h = h[:idx+1] + js + h[idx+1:]
open('dhi_globe.html','w').write(h)
print('embedded HCX before const PYR=')
