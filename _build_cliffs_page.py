#!/usr/bin/env python3
"""Build public/cliffs/index.html — the 'Demographic Cliffs' section.
Each cliff is a forward cohort already locked in by people alive today,
ranked across major economies, framed for the buyer who budgets around it.
Data: _cliffs_ranked.json (from _build_cliffs.py)."""
import json
R=json.load(open('_cliffs_ranked.json'))

META=[
 ('higher_ed','The enrollment cliff','Future 18-year-olds, 2025 → 2043 — already born','Universities · ed-tech · student housing','pct'),
 ('kindergarten','The kindergarten cliff','Future 5-year-olds, → 2030','School districts · K-12 · children’s brands','pct'),
 ('baby','The baby-economy cliff','Annual births, peak → 2025','Formula · diapers · maternity care','pct'),
 ('manpower','The manpower cliff','Military-age cohort 18–25, → 2043','Defence recruitment · entry-level labour','pct'),
 ('first_home','The first-home wave','Household-formation cohort 28–35, → 2053','Homebuilders · mortgage lenders · REITs','pct'),
 ('peak_workers','Peak workers','Working-age 15–64, change to 2050','Manufacturers · investors · site selection','pct'),
 ('silver','The silver tsunami','80+ population, multiple by 2050','Senior living · home health · pharma','mult'),
]
cards=''
for key,title,sub,buyer,unit in META:
    cards+=('<div class="card" id="__ID__"><div class="c-h">__T__</div><div class="c-sub">__S__</div>'
            '<div class="buyer">Who budgets for this&nbsp;&middot;&nbsp;<b>__B__</b></div>'
            '<svg class="chart" id="svg___ID__" viewBox="0 0 1000 470" xmlns="http://www.w3.org/2000/svg"></svg>'
            '<div class="c-foot"><div class="src">Cohort already born; UN WPP for projected birth-years &amp; age structure. demoriaresearch.com &middot; CC BY</div>'
            '<div class="btns"><button class="btn" onclick="dl(\'svg___ID__\',\'__T__\',\'demoria-__ID__\')">Download PNG</button></div></div></div>'
           ).replace('__ID__',key).replace('__T__',title).replace('__S__',sub).replace('__B__',buyer)

TPL=r'''<!DOCTYPE html><html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Demographic Cliffs — Demoria Research</title>
<meta name="description" content="The demographic cliffs already locked in: future students, workers, homebuyers and retirees by country, derived from the people alive today.">
<meta property="og:title" content="Demographic Cliffs — the cohorts already locked in">
<meta property="og:image" content="https://demoriaresearch.com/charts/fertility-1965-2025.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://demoriaresearch.com/cliffs/">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{--navy:#0c1a33;--cream:#f4ecd3;--cream2:#fcf4dd;--gold:#b58420;--gold2:#e8b84b;--coral:#dd6f3e;--ink:#0c1a33}
*{box-sizing:border-box;margin:0;padding:0}
body{background:linear-gradient(180deg,#0a1730,#091428);color:#fff;font-family:'Manrope',system-ui,sans-serif;min-height:100vh}
.topbar{background:var(--cream);height:50px;display:flex;align-items:center;padding:0 22px;gap:13px;position:sticky;top:0;z-index:50;border-bottom:2px solid rgba(12,26,51,.12)}
.tb-back{font-size:.66rem;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--navy);text-decoration:none;opacity:.72}
.tb-title{font-size:.95rem;font-weight:700;color:var(--navy)}
.wrap{max-width:1040px;margin:0 auto;padding:34px 20px 80px}
.eye{font-family:'JetBrains Mono',monospace;font-size:.66rem;letter-spacing:.22em;text-transform:uppercase;color:var(--gold2);text-align:center;margin-bottom:10px}
h1.hd{text-align:center;font-size:clamp(1.8rem,4.5vw,2.7rem);font-weight:800;line-height:1.08;margin-bottom:12px}
h1.hd em{color:var(--gold2);font-style:normal}
.lead{text-align:center;color:rgba(255,255,255,.72);font-size:clamp(.98rem,1.3vw,1.12rem);max-width:64ch;margin:0 auto 26px;line-height:1.55}
.card{background:var(--cream2);border-radius:16px;padding:22px clamp(14px,2.5vw,30px) 18px;box-shadow:0 30px 80px rgba(0,0,0,.45),inset 0 0 0 1px rgba(181,132,32,.30);margin-bottom:24px;scroll-margin-top:64px}
.c-h{font-size:clamp(1.25rem,2.6vw,1.7rem);font-weight:800;color:var(--ink);margin-bottom:2px}
.c-sub{font-family:'JetBrains Mono',monospace;font-size:.72rem;letter-spacing:.04em;color:rgba(12,26,51,.6)}
.buyer{font-size:.8rem;color:rgba(12,26,51,.7);margin:7px 0 4px}.buyer b{color:var(--ink)}
svg.chart{display:block;width:100%;height:auto}
.c-foot{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;justify-content:space-between;margin-top:10px;padding-top:12px;border-top:1px solid rgba(12,26,51,.12)}
.src{font-family:'JetBrains Mono',monospace;font-size:.62rem;color:rgba(12,26,51,.55);line-height:1.5}
.btn{font-family:'JetBrains Mono',monospace;font-size:.66rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;padding:9px 14px;border-radius:7px;border:1px solid rgba(12,26,51,.25);background:var(--gold2);color:var(--navy);cursor:pointer}
.note{text-align:center;color:rgba(255,255,255,.5);font-family:'JetBrains Mono',monospace;font-size:.68rem;letter-spacing:.06em;margin-top:24px;line-height:1.6}
</style></head><body>
<div class="topbar"><a class="tb-back" href="/">&#8249;&nbsp;Demoria Research</a><span style="color:rgba(12,26,51,.3)">|</span><span class="tb-title">Demographic Cliffs</span></div>
<div class="wrap">
<div class="eye">Demoria Research &middot; Demographic Cliffs</div>
<h1 class="hd">The cohorts <em>already locked in</em></h1>
<p class="lead">Every chart below is a future cohort &mdash; students, workers, homebuyers, retirees &mdash; whose size is largely fixed by the people alive today. A 5-year-old in 2030 was born in 2025; an 18-year-old in 2043 was born in 2025. That is what makes these forecasts unusually certain &mdash; and what a planner can budget against.</p>
__CARDS__
<div class="note">Steepest among economies &gt;10M. Young cohorts derived from national births (near-certain while already born); structural cohorts from UN&nbsp;WPP age structure.</div>
</div>
<script>
const R=__DATA__;
const META=__META__;
const NS='http://www.w3.org/2000/svg';
function el(n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}
function tx(x,y,s,cls,extra){const t=el('text',Object.assign({x,y,class:cls},extra||{}));t.textContent=s;return t;}
function nm(s){return s.replace('China, Taiwan Province of China','Taiwan').replace('Republic of Korea','South Korea').replace('Russian Federation','Russia').replace('Iran (Islamic Republic of)','Iran').replace('United States of America','United States').replace('Viet Nam','Vietnam');}
const STY=".ax{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:13px;fill:rgba(12,26,51,.6)}.val{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:13px;font-weight:700;fill:#0c1a33}.cn{font-family:'Manrope',system-ui,sans-serif;font-size:13.5px;font-weight:600;fill:#0c1a33}";
function bars(svgId,key,unit){
  const svg=document.getElementById(svgId); const rows=R[key]; if(!rows)return;
  const W=1000,H=470,L=210,Rm=70,T=16,B=16, n=rows.length;
  const rowH=(H-T-B)/n; const x0=L, x1=W-Rm;
  const st=el('style',{});st.textContent=STY;svg.appendChild(st);
  const isMult=unit==='mult';
  const maxv=Math.max.apply(null,rows.map(r=>Math.abs(r.v)));
  const sc=v=>(Math.abs(v)/maxv)*(x1-x0);
  rows.forEach((r,i)=>{
    const cy=T+i*rowH+rowH/2;
    svg.appendChild(tx(L-12,cy+5,nm(r.nm),'cn',{'text-anchor':'end'}));
    const w=sc(r.v);
    const col=isMult?'#b58420':'#dd6f3e';
    svg.appendChild(el('rect',{x:x0,y:cy-rowH*0.32,width:Math.max(2,w).toFixed(1),height:rowH*0.64,rx:3,fill:col,'fill-opacity':isMult?0.85:0.8}));
    const lab=isMult?('×'+r.v.toFixed(1)):((r.v>0?'+':'')+Math.round(r.v)+'%');
    svg.appendChild(tx(x0+w+8,cy+5,lab,'val'));
  });
}
META.forEach(m=>bars('svg_'+m[0],m[0],m[4]));
function dl(svgId,title,fname){
  const svg=document.getElementById(svgId),W=1000,H=470;
  const c=svg.cloneNode(true);c.setAttribute('width',W);c.setAttribute('height',H);
  const bg=el('rect',{x:0,y:0,width:W,height:H,fill:'#fcf4dd'});c.insertBefore(bg,c.firstChild);
  c.insertBefore(tx(210,12,title+'  —  demoriaresearch.com','ax',{'font-size':'12'}),c.firstChild.nextSibling);
  const data=new XMLSerializer().serializeToString(c),img=new Image();
  img.onload=()=>{const s=2,cv=document.createElement('canvas');cv.width=W*s;cv.height=H*s;const x=cv.getContext('2d');x.scale(s,s);x.drawImage(img,0,0);cv.toBlob(b=>{const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=fname+'.png';a.click();});};
  img.src='data:image/svg+xml;base64,'+btoa(unescape(encodeURIComponent(data)));
}
</script></body></html>'''
html=(TPL.replace('__CARDS__',cards)
        .replace('__DATA__',json.dumps(R,separators=(',',':')))
        .replace('__META__',json.dumps([list(m) for m in META],separators=(',',':'))))
open('public/cliffs/index.html','w',encoding='utf-8').write(html)
print(f"wrote public/cliffs/index.html ({len(html)} bytes), {len(META)} cliff cards")
