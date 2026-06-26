#!/usr/bin/env python3
"""Bake births_data.json INTO public/births/index.html so the page renders with
no client-side fetch ("Loading…" never ships to crawlers or users):

  1. splice the JSON into  /*__BD__*/ ... /*__/BD__*/  (window.__BD__=…)
  2. regenerate a static, crawler-readable country listing between
     <!--SSR--> ... <!--/SSR-->  inside #regions (JS overwrites it on boot)

Run after every births_data.json update, before deploying.
"""
import json, re

PAGE='public/births/index.html'
DATA='public/births_data.json'

bd=json.load(open(DATA,encoding='utf-8'))
h=open(PAGE,encoding='utf-8').read()

# ---- 0. attach the most accurate total population (what the Data Tables show) ----
# Latest available pop from _data_export.json (thousands), stamped with its
# provenance: NSO override, DRE estimate, or UN WPP baseline. Kept here (not in
# births_data.json) so it always tracks the canonical dataset on every embed.
EXP='_data_export.json'
def attach_pop(countries):
    exp=json.load(open(EXP,encoding='utf-8'))
    n=0
    for c in countries:
        e=exp.get(c['iso'])
        if not e: continue
        pop=(e.get('ind') or {}).get('pop'); yrs=e.get('yrs')
        if not pop or not yrs: continue
        adj=set((e.get('nso_yrs') or {}).get('pop') or []) | set((e.get('dre_yrs') or {}).get('pop') or [])
        for i in range(len(yrs)-1,-1,-1):       # latest non-null year
            v=pop[i] if i<len(pop) else None
            if v is None: continue
            yr=yrs[i]
            c['pop']=round(v,2); c['pop_yr']=yr
            # Total mid-year population is a modelled quantity, never a live
            # NSO count. Where the pipeline adjusted it off the UN baseline
            # (its "overrides"), that is a Demoria Research Estimation
            # synthesised from national/official sources (DRE); otherwise it
            # is the raw UN WPP 2024 projection (WPP). It is never labelled NSO.
            c['pop_src']='dre' if yr in adj else 'wpp'
            n+=1; break
    return n
_np=attach_pop(bd['countries'])

# ---- 1. inline data ----
payload=json.dumps(bd,ensure_ascii=False,separators=(',',':')).replace('</','<\\/')
h2,n=re.subn(r'/\*__BD__\*/.*?/\*__/BD__\*/',
             lambda m:'/*__BD__*/window.__BD__='+payload+';/*__/BD__*/',
             h, count=1, flags=re.S)
assert n==1, "BD marker not found"

# ---- 2. static SSR listing ----
CAT={'nso':'NSO','dre':'DRE','wpp':'UN WPP 2024'}
POPCAT={'nso':'NSO','dre':'DRE','wpp':'UN WPP'}
def pop_txt(c):
    v=c.get('pop')
    if v is None: return ''
    p=v*1000
    if   p>=1e9: s=f"{p/1e9:.2f}bn"
    elif p>=1e6: s=f"{p/1e6:.0f}M" if p>=1e8 else f"{p/1e6:.1f}M"
    elif p>=1e3: s=f"{round(p/1e3)}k"
    else:        s=f"{round(p):,}"
    return f" · population {s} ({POPCAT.get(c.get('pop_src'),'UN WPP')}{', '+str(c['pop_yr']) if c.get('pop_yr') else ''})"
def tfr_cur(c):
    t=c.get('tfr',{}); t25=t.get('2025')
    if c.get('b25') and c.get('b26') and t25:
        return round(t25*(c['b26']/c['b25']),2), True
    return t25, False
def births_txt(c):
    if c.get('b25') is not None and c.get('b26') is not None:
        chg=(c['b26']-c['b25'])/c['b25']*100
        return f"2026 births so far: {c['b26']:,} vs {c['b25']:,} in 2025 ({chg:+.1f}%, first {c['mon']} months)"
    if c.get('ba'):
        ba=c['ba']; chg=(ba['cur']-ba['prev'])/ba['prev']*100
        return f"{ba['year']} births: {ba['cur']:,} vs {ba['prev']:,} in {ba['year']-1} ({chg:+.1f}%, full year)"
    if c.get('est'):
        e=c['est']; return f"{e['year']} births (estimate): ~{e['cur']:,}"
    return "awaiting current-year data"

order=bd.get('subregion_order') or sorted({c['region'] for c in bd['countries']})
byreg={}
for c in bd['countries']: byreg.setdefault(c['region'],[]).append(c)
parts=[]
for reg in order:
    rows=sorted(byreg.get(reg,[]),key=lambda c:(c.get('tfr',{}).get('2025') or 99))
    if not rows: continue
    lis=[]
    for c in rows:
        cur,est=tfr_cur(c)
        tfr=f"TFR {cur:.2f}{' (2026 estimate)' if est else ' (2025)'}" if cur else "TFR n/a"
        lis.append(f"<li><strong>{c['name']}</strong> — {tfr} · {births_txt(c)}{pop_txt(c)} · source: {CAT.get(c.get('src_cat'),'UN WPP 2024')}</li>")
    parts.append(f"<section><h2 style=\"padding:14px 26px 4px\">{reg}</h2><ul style=\"padding:0 26px 8px 44px;line-height:1.7;color:rgba(238,241,246,.7);font-size:.85rem\">{''.join(lis)}</ul></section>")
ssr='<!--SSR-->'+''.join(parts)+'<!--/SSR-->'
h2,n=re.subn(r'<!--SSR-->.*?<!--/SSR-->', lambda m:ssr, h2, count=1, flags=re.S)
assert n==1, "SSR marker not found"

open(PAGE,'w',encoding='utf-8').write(h2)
live=sum(1 for c in bd['countries'] if c.get('b26') is not None or c.get('ba'))
print(f"embedded: {len(bd['countries'])} countries ({live} live, {_np} with population) -> {PAGE} ({len(h2):,} bytes)")
