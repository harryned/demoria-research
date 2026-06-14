#!/usr/bin/env python3
"""Build public/charts/index.html — the shareable 'cool charts' gallery.
Each card is self-contained (data embedded inline, no loading state), in the
cream/navy brand aesthetic, with one-click Download PNG + Copy link.
Re-run after the data files (public/charts_*.json) change."""
import json

TFR=json.load(open('public/charts_tfr_shift.json'))
ONS=[o for o in json.load(open('public/charts_onset.json')) if o.get('onset')]
B65=sum(1 for r in TFR if r['a']<2.1); B25=sum(1 for r in TFR if r['b']<2.1)
NDEC=len(ONS)

TPL=r'''<!DOCTYPE html>
<html lang="en"><head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Charts — Demoria Research</title>
<meta name="description" content="Surprising demographic charts, free for journalists to download and share. How the world fell below replacement, and when each country's deaths overtook its births.">
<meta property="og:title" content="Demographic charts, free to share — Demoria Research">
<meta property="og:description" content="The fertility transition in pictures. __B25__ of 236 countries now below replacement; __NDEC__ already in natural decline.">
<meta property="og:image" content="https://demoriaresearch.com/charts/fertility-1965-2025.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="canonical" href="https://demoriaresearch.com/charts/">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
:root{--navy:#0c1a33;--cream:#f4ecd3;--cream2:#fcf4dd;--gold:#b58420;--gold2:#e8b84b;--teal:#1d9e75;--coral:#dd6f3e;--ink:#0c1a33}
*{box-sizing:border-box;margin:0;padding:0}
body{background:linear-gradient(180deg,#0a1730 0%,#091428 100%);color:#fff;font-family:'Manrope',system-ui,-apple-system,sans-serif;min-height:100vh}
.topbar{background:var(--cream);height:50px;display:flex;align-items:center;padding:0 22px;gap:13px;border-bottom:2px solid rgba(12,26,51,.12);position:sticky;top:0;z-index:50}
.tb-back{display:flex;align-items:center;gap:6px;font-size:.66rem;font-weight:600;letter-spacing:.16em;text-transform:uppercase;color:var(--navy);text-decoration:none;opacity:.72}
.tb-title{font-size:.95rem;font-weight:700;color:var(--navy)}
.wrap{max-width:1040px;margin:0 auto;padding:34px 20px 80px}
.eye{font-family:'JetBrains Mono',monospace;font-size:.66rem;letter-spacing:.22em;text-transform:uppercase;color:var(--gold2);text-align:center;margin-bottom:10px}
h1.hd{text-align:center;font-size:clamp(1.8rem,4.5vw,2.7rem);font-weight:800;letter-spacing:-.01em;line-height:1.08;margin-bottom:12px}
h1.hd em{color:var(--gold2);font-style:normal}
.lead{text-align:center;color:rgba(255,255,255,.72);font-size:clamp(.98rem,1.3vw,1.12rem);max-width:60ch;margin:0 auto 26px;line-height:1.55}
.card{background:var(--cream2);border-radius:16px;padding:22px clamp(14px,2.5vw,30px) 18px;box-shadow:0 30px 80px rgba(0,0,0,.45),inset 0 0 0 1px rgba(181,132,32,.30);margin-bottom:26px;scroll-margin-top:64px}
.c-h{font-size:clamp(1.25rem,2.6vw,1.7rem);font-weight:800;color:var(--ink);letter-spacing:-.01em;margin-bottom:3px}
.c-sub{font-family:'JetBrains Mono',monospace;font-size:.72rem;letter-spacing:.04em;color:rgba(12,26,51,.6);margin-bottom:8px}
svg.chart{display:block;width:100%;height:auto}
.c-foot{display:flex;flex-wrap:wrap;gap:10px 18px;align-items:center;justify-content:space-between;margin-top:12px;padding-top:12px;border-top:1px solid rgba(12,26,51,.12)}
.src{font-family:'JetBrains Mono',monospace;font-size:.64rem;letter-spacing:.03em;color:rgba(12,26,51,.55);line-height:1.5}
.btns{display:flex;gap:8px}
.btn{font-family:'JetBrains Mono',monospace;font-size:.66rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;padding:9px 14px;border-radius:7px;border:1px solid rgba(12,26,51,.25);background:transparent;color:var(--ink);cursor:pointer;transition:background .15s,border-color .15s}
.btn:hover{background:rgba(12,26,51,.06)}
.btn.gold{background:var(--gold2);border-color:var(--gold2);color:var(--navy)}
.btn.gold:hover{background:#f0c45e}
.more{text-align:center;color:rgba(255,255,255,.5);font-family:'JetBrains Mono',monospace;font-size:.7rem;letter-spacing:.14em;text-transform:uppercase;margin-top:30px}
@media(max-width:560px){.c-foot{flex-direction:column;align-items:stretch}.btns{justify-content:stretch}.btn{flex:1;text-align:center}}
#ctip{position:fixed;z-index:100;pointer-events:none;display:none;background:var(--navy);color:var(--cream);font-family:'Manrope',sans-serif;font-size:.82rem;line-height:1.3;padding:8px 11px;border-radius:8px;box-shadow:0 10px 30px rgba(0,0,0,.45);border:1px solid rgba(232,184,75,.45);max-width:230px}
#ctip b{color:#fff;font-weight:700}
#ctip .v{font-family:'JetBrains Mono',monospace;color:var(--gold2);font-size:.72rem;margin-top:2px}
svg.chart circle{transition:r .08s}
</style></head>
<body>
<div class="topbar"><a class="tb-back" href="/">&#8249;&nbsp;Demoria Research</a><span style="color:rgba(12,26,51,.3)">|</span><span class="tb-title">Charts</span></div>
<div class="wrap">
  <div class="eye">Demoria Research &middot; Charts</div>
  <h1 class="hd">Demographic charts, <em>free to share</em></h1>
  <p class="lead">Surprising pictures of the global fertility transition &mdash; download any chart as an image, or link straight to it. Attribution baked in. More added as the data moves.</p>

  <div class="card" id="tfr-shift">
    <div class="c-h">The world fell below replacement</div>
    <div class="c-sub">Total fertility rate &middot; every country &amp; territory &middot; 1965 vs 2025</div>
    <svg class="chart" id="svg1" viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg"></svg>
    <div class="c-foot">
      <div class="src">Source: UN World Population Prospects 2024 + national statistical offices.<br>demoriaresearch.com &middot; CC BY &mdash; free with attribution</div>
      <div class="btns"><button class="btn" onclick="copyLink('tfr-shift')">Copy link</button><button class="btn gold" onclick="dlPNG('svg1','The world fell below replacement','Total fertility rate · every country · 1965 vs 2025','demoria-fertility-1965-2025')">Download PNG</button></div>
    </div>
  </div>

  <div class="card" id="natural-decline">
    <div class="c-h">When the dying started</div>
    <div class="c-sub">Year each country&rsquo;s deaths first overtook its births &middot; __NDEC__ of 236, and counting</div>
    <svg class="chart" id="svg2" viewBox="0 0 1000 600" xmlns="http://www.w3.org/2000/svg"></svg>
    <div class="c-foot">
      <div class="src">Source: UN World Population Prospects 2024 + national statistical offices.<br>demoriaresearch.com &middot; CC BY &mdash; free with attribution</div>
      <div class="btns"><button class="btn" onclick="copyLink('natural-decline')">Copy link</button><button class="btn gold" onclick="dlPNG('svg2','When the dying started','Year deaths overtook births · __NDEC__ countries and counting','demoria-natural-decline')">Download PNG</button></div>
    </div>
  </div>

  <div class="more">More charts coming &mdash; fertility collapse &middot; births in free-fall &middot; the ageing race</div>
</div>
<div id="ctip"></div>
<script>
const TFR=__TFR__;
const ONS=__ONS__;
const NS='http://www.w3.org/2000/svg';
function el(n,a){const e=document.createElementNS(NS,n);for(const k in a)e.setAttribute(k,a[k]);return e;}
function tx(x,y,s,cls,extra){const t=el('text',Object.assign({x,y,class:cls},extra||{}));t.textContent=s;return t;}
const STYLE=".ax{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:13px;fill:rgba(12,26,51,.55)}.big{font-family:'Manrope',system-ui,sans-serif;font-weight:800;fill:#0c1a33}.bigl{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:12px;letter-spacing:.06em;fill:rgba(12,26,51,.6)}.repl{font-family:'JetBrains Mono',ui-monospace,monospace;font-size:12px;font-weight:700;fill:#993c1d}.lab{font-family:'Manrope',system-ui,sans-serif;font-size:12px;font-weight:700;fill:#0c1a33}";

/* Chart 1: TFR strip plot */
(function(){
  const SVG=document.getElementById('svg1'),W=1000,H=600,mL=64,mR=34,mT=58,mB=92;
  const x0=mL,x1=W-mR,y0=H-mB,y1=mT,TMAX=8.6, yS=t=>y0+(y1-y0)*(t/TMAX);
  const jit=iso=>{let h=0;for(let i=0;i<iso.length;i++)h=(h*31+iso.charCodeAt(i))&0xffff;return ((h%1000)/1000)*2-1;};
  const st=el('style',{});st.textContent=STYLE;SVG.appendChild(st);
  [0,2,4,6,8].forEach(t=>{const y=yS(t);SVG.appendChild(el('line',{x1:x0,y1:y,x2:x1,y2:y,stroke:'rgba(12,26,51,.10)','stroke-width':1}));SVG.appendChild(tx(x0-10,y+4,t.toFixed(0),'ax',{'text-anchor':'end'}));});
  SVG.appendChild(tx(x0-10,yS(8)-16,'TFR','ax',{'text-anchor':'end'}));
  const groups=[{k:'a',cx:(x0+(x0+x1)/2)/2+40,lab:'1965',th:2.4},{k:'b',cx:((x0+x1)/2+x1)/2-10,lab:'2025',th:2.1}];
  const bw=(x1-x0)/2*0.74;
  groups.forEach(g=>{let below=0;TFR.forEach(r=>{const v=r[g.k],cx=g.cx+jit(r.iso)*bw/2,cy=yS(v),lo=v<g.th;if(lo)below++;var _c=el('circle',{cx:cx.toFixed(1),cy:cy.toFixed(1),r:4.3,fill:lo?'#dd6f3e':'#1d9e75','fill-opacity':0.72,stroke:lo?'#993c1d':'#0f6e56','stroke-width':0.5,'stroke-opacity':0.5});_c.__i={nm:r.nm,yr:g.lab,tfr:v};SVG.appendChild(_c);});
    const ry=yS(g.th),ga=g.cx-bw/2-16,gb=g.cx+bw/2+16;
    SVG.appendChild(el('line',{x1:ga,y1:ry,x2:gb,y2:ry,stroke:'#dd6f3e','stroke-width':1.5,'stroke-dasharray':'6 5'}));
    SVG.appendChild(tx(g.cx,ry-8,'Replacement ≈ '+g.th.toFixed(1),'repl',{'text-anchor':'middle'}));
    SVG.appendChild(tx(g.cx,y0+30,g.lab,'big',{'text-anchor':'middle','font-size':'22'}));
    SVG.appendChild(tx(g.cx,y0+52,below+' of '+TFR.length+' below','bigl',{'text-anchor':'middle'}));});
  SVG.appendChild(tx((x0+x1)/2,y0+74,'Replacement fertility rises with child mortality — Espenshade, Guzmán & Westoff (2003)','ax',{'text-anchor':'middle','font-size':'11'}));
  const lx=x0+4,ly=mT-30;
  SVG.appendChild(el('circle',{cx:lx+6,cy:ly,r:5,fill:'#1d9e75','fill-opacity':.75}));SVG.appendChild(tx(lx+18,ly+4,'at or above replacement','ax'));
  SVG.appendChild(el('circle',{cx:lx+218,cy:ly,r:5,fill:'#dd6f3e','fill-opacity':.8}));SVG.appendChild(tx(lx+230,ly+4,'below replacement','ax'));
})();

/* Chart 2: natural-decline onset */
(function(){
  const SVG=document.getElementById('svg2'),W=1000,H=600,mL=56,mR=20,mT=64,mB=74;
  const x0=mL,x1=W-mR,y0=H-mB,y1=mT,Y0=1965,Y1=2026;
  const xS=y=>x0+(x1-x0)*((y-Y0)/(Y1-Y0));
  const rows=ONS.slice().sort((a,b)=>a.onset-b.onset);
  const CMAX=Math.ceil((rows.length+4)/10)*10, cS=c=>y0+(y1-y0)*(c/CMAX);
  const st=el('style',{});st.textContent=STYLE;SVG.appendChild(st);
  for(let c=0;c<=CMAX;c+=20){const y=cS(c);SVG.appendChild(el('line',{x1:x0,y1:y,x2:x1,y2:y,stroke:'rgba(12,26,51,.10)','stroke-width':1}));SVG.appendChild(tx(x0-9,y+4,String(c),'ax',{'text-anchor':'end'}));}
  SVG.appendChild(tx(x0-9,cS(CMAX)-16,'count','ax',{'text-anchor':'end'}));
  [1970,1980,1990,2000,2010,2020].forEach(yy=>{SVG.appendChild(tx(xS(yy),y0+24,String(yy),'ax',{'text-anchor':'middle'}));SVG.appendChild(el('line',{x1:xS(yy),y1:y0,x2:xS(yy),y2:y0+6,stroke:'rgba(12,26,51,.3)','stroke-width':1}));});
  let d='M '+xS(Y0)+' '+cS(0),cum=0;
  rows.forEach(r=>{const x=xS(r.onset);d+=' L '+x.toFixed(1)+' '+cS(cum).toFixed(1);cum++;d+=' L '+x.toFixed(1)+' '+cS(cum).toFixed(1);});
  d+=' L '+xS(2025).toFixed(1)+' '+cS(cum).toFixed(1);
  SVG.appendChild(el('path',{d:d+' L '+xS(2025).toFixed(1)+' '+cS(0)+' Z',fill:'rgba(181,132,32,.10)',stroke:'none'}));
  SVG.appendChild(el('path',{d:d,fill:'none',stroke:'#b58420','stroke-width':2.5,'stroke-linejoin':'round'}));
  rows.forEach(r=>{const x=xS(r.onset),rr=Math.max(2.5,Math.min(15,Math.sqrt(r.pop||1)*1.25));var _c=el('circle',{cx:x.toFixed(1),cy:(y0-6).toFixed(1),r:rr.toFixed(1),fill:'#dd6f3e','fill-opacity':0.55,stroke:'#993c1d','stroke-width':0.5,'stroke-opacity':0.5});_c.__i={nm:r.nm,onset:r.onset};SVG.appendChild(_c);});
  const cumAt=y=>rows.filter(r=>r.onset<=y).length;
  const M=[[1972,'Germany'],[1992,'Russia'],[2005,'Japan'],[2015,'Spain'],[2022,'China']];
  M.forEach(m=>{const yy=m[0],nm=m[1],x=xS(yy),y=cS(cumAt(yy));
    SVG.appendChild(el('line',{x1:x,y1:y,x2:x-16,y2:y-20,stroke:'rgba(12,26,51,.45)','stroke-width':1}));
    var _m=el('circle',{cx:x,cy:y,r:4,fill:'#0c1a33'});_m.__i={nm:nm,onset:yy};SVG.appendChild(_m);
    SVG.appendChild(tx(x-20,y-34,nm,'lab',{'text-anchor':'end'}));
    SVG.appendChild(tx(x-20,y-19,String(yy),'bigl',{'text-anchor':'end','font-size':'11'}));});
  SVG.appendChild(tx(x0+34,y1+30,rows.length+' countries','big',{'font-size':'24'}));
  SVG.appendChild(tx(x0+34,y1+50,'now in natural decline','bigl'));
})();

/* hover/tap tooltips — which country is this dot? */
(function(){
  const tip=document.getElementById('ctip'); let hl=null;
  function fmt(i){return i.tfr!==undefined?'<b>'+i.nm+'</b><div class="v">'+i.yr+' · TFR '+i.tfr.toFixed(2)+'</div>':'<b>'+i.nm+'</b><div class="v">deaths > births since '+i.onset+'</div>';}
  function unhl(){if(hl){hl.setAttribute('r',hl.__r);hl=null;}}
  function hide(){unhl();tip.style.display='none';}
  function place(cx,cy){let lx=cx+15,ty=cy+15;if(lx+240>window.innerWidth)lx=cx-15-tip.offsetWidth;if(ty+70>window.innerHeight)ty=cy-15-tip.offsetHeight;tip.style.left=lx+'px';tip.style.top=ty+'px';}
  function wire(svg){
    svg.addEventListener('mousemove',function(e){
      const c=(e.target.tagName==='circle'&&e.target.__i)?e.target:null;
      if(!c){hide();svg.style.cursor='';return;}
      if(hl!==c){unhl();hl=c;c.__r=c.getAttribute('r');c.setAttribute('r',(parseFloat(c.__r)*1.7).toFixed(1));c.parentNode.appendChild(c);}
      tip.style.display='block';tip.innerHTML=fmt(c.__i);place(e.clientX,e.clientY);svg.style.cursor='pointer';
    });
    svg.addEventListener('mouseleave',hide);
    svg.addEventListener('click',function(e){const c=(e.target.tagName==='circle'&&e.target.__i)?e.target:null;if(!c){hide();return;}tip.style.display='block';tip.innerHTML=fmt(c.__i);const b=c.getBoundingClientRect();place(b.left+b.width/2,b.bottom);});
  }
  wire(document.getElementById('svg1'));wire(document.getElementById('svg2'));
  document.addEventListener('scroll',hide,true);
})();

function copyLink(id){const u=location.origin+location.pathname+'#'+id;navigator.clipboard.writeText(u).then(()=>{event.target.textContent='Copied!';setTimeout(()=>event.target.textContent='Copy link',1400);});}
function dlPNG(svgId,title,sub,fname){
  const SVG=document.getElementById(svgId),W=1000,H=600;
  const clone=SVG.cloneNode(true);clone.setAttribute('width',W);clone.setAttribute('height',H);
  const bg=el('rect',{x:0,y:0,width:W,height:H,fill:'#fcf4dd'});clone.insertBefore(bg,clone.firstChild);
  const t1=tx(56,30,title,'big',{'font-size':'24'}),t2=tx(56,48,sub+'  —  demoriaresearch.com','bigl',{'font-size':'12.5'});
  clone.insertBefore(t2,clone.firstChild.nextSibling);clone.insertBefore(t1,clone.firstChild.nextSibling);
  const data=new XMLSerializer().serializeToString(clone),img=new Image();
  img.onload=()=>{const sc=2,cv=document.createElement('canvas');cv.width=W*sc;cv.height=H*sc;const ctx=cv.getContext('2d');ctx.scale(sc,sc);ctx.drawImage(img,0,0);cv.toBlob(b=>{const a=document.createElement('a');a.href=URL.createObjectURL(b);a.download=fname+'.png';a.click();});};
  img.src='data:image/svg+xml;base64,'+btoa(unescape(encodeURIComponent(data)));
}
if(location.hash){const t=document.getElementById(location.hash.slice(1));if(t)t.scrollIntoView();}
</script>
</body></html>'''

html=(TPL.replace('__TFR__',json.dumps(TFR,separators=(',',':')))
        .replace('__ONS__',json.dumps(ONS,separators=(',',':')))
        .replace('__B25__',str(B25)).replace('__B65__',str(B65)).replace('__NDEC__',str(NDEC)))
open('public/charts/index.html','w',encoding='utf-8').write(html)
print(f"wrote public/charts/index.html ({len(html)} bytes) — chart1 {B65}->{B25} below, chart2 {NDEC} onsets")
