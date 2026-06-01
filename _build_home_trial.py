"""Build dhi_home_trial.html — try five compact home-page layouts on a
single page, with a picker at the bottom to swap between them. Every
variant is designed to fit a 1280x800 viewport without scrolling.

  Current     baseline (as on demoriaresearch.com today)
  A Compact   tight hero stacked over a 1x4 nav strip
  B Split     50/50 — cream hero left, 2x2 navy nav grid right
  C Editorial 60/40 — big cream hero left, stacked nav tiles right
  D Inverted  navy hero (no card) + 4 cream nav tiles below
  E Dashboard horizontal command-bar header + 2x2 cream tiles
"""
import shutil

SRC = 'dhi_globe.html'
DST = 'dhi_home_trial.html'
shutil.copy2(SRC, DST)
h = open(DST).read()

h = h.replace('<title>DHI v2.0 &mdash; The World</title>',
              '<title>DHI v2.0 (home trial) &mdash; The World</title>', 1)
h = h.replace('<title>DHI v2.0 — The World</title>',
              '<title>DHI v2.0 (home trial) — The World</title>', 1)

# Force the Home tab to be visible on load (override default landing).
# Done via a body class + JS to call show('home').
# CSS for each variant scopes everything under body.hl-X.

CSS = r"""
/* ===== HOME LAYOUT TRIAL ===== */
/* All variants assume #view-home is active. Everything fits a
   1280x800 viewport without scroll. */

/* ----- shared reset for all variants ----- */
body[class*="hl-"] #view-home{height:calc(100vh - 88px);overflow:hidden}
body[class*="hl-"] #view-home .home-wrap{height:100%;display:flex;flex-direction:column;padding:0 18px;box-sizing:border-box}
/* Hide spotlight ribbon + dev/API + footer in all trial variants —
   they push the page off-screen and aren't needed for the first viewport. */
body[class*="hl-"] #view-home .home-ribbon,
body[class*="hl-"] #view-home .home-cta-h-2,
body[class*="hl-"] #view-home .hc-api,
body[class*="hl-"] #view-home .home-foot{display:none!important}

/* ============================ */
/* A — COMPACT (current direction, just tighter) */
/* hero card top, 4 nav tiles in a single row of 4, stats strip */
body.hl-A #view-home .home-wrap{padding:14px 22px 16px;gap:14px}
body.hl-A #view-home .home-hero{margin:0 auto;padding:24px 36px 22px;max-width:1180px;border-radius:16px}
body.hl-A #view-home .hh-eye{margin:0 0 4px;font-size:.58rem}
body.hl-A #view-home .hh-title{font-size:clamp(1.4rem,2.4vw,2rem);margin:0 0 6px;line-height:1.08}
body.hl-A #view-home .hh-acr{font-size:.45em;vertical-align:.2em}
body.hl-A #view-home .hh-sub{font-size:.86rem;margin:0 auto 12px;max-width:720px;line-height:1.4}
body.hl-A #view-home .hh-cta{margin-top:4px;max-width:540px;display:block;text-align:center}
body.hl-A #view-home .hh-cta-row{justify-content:center}
body.hl-A #view-home .hh-pick,
body.hl-A #view-home .hh-primary{min-height:46px;padding:0 16px;font-size:.92rem}
body.hl-A #view-home .hh-pick{padding:8px 14px}
body.hl-A #view-home .hh-hint{margin:7px 0 0;font-size:.74rem;text-align:center}
body.hl-A #view-home .hh-or{display:none!important}
body.hl-A #view-home .home-cta-grid{grid-template-columns:repeat(4,1fr)!important;gap:10px;max-width:1180px;margin:0 auto}
body.hl-A #view-home .home-cta-grid .hc-card{padding:14px 16px 16px;min-height:0}
body.hl-A #view-home .home-cta-grid .hc-num{font-size:.52rem;margin-bottom:6px}
body.hl-A #view-home .home-cta-grid .hc-t{font-size:1.02rem;margin-bottom:4px}
body.hl-A #view-home .home-cta-grid .hc-d{font-size:.74rem;line-height:1.35;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
body.hl-A #view-home .home-cta-grid .hc-arr{font-size:1.1rem;align-self:flex-start}
body.hl-A #view-home .home-stats{margin:0 auto;max-width:1180px;border:0;border-top:1px solid rgba(232,184,75,.22)}
body.hl-A #view-home .home-stats .hs-tile{padding:10px 12px}
body.hl-A #view-home .home-stats .hs-v{font-size:1.25rem;margin:2px 0}
body.hl-A #view-home .home-stats .hs-l{font-size:.66rem;line-height:1.3}
body.hl-A #view-home .home-stats .hs-k{font-size:.5rem}

/* ============================ */
/* B — SPLIT 50/50 (cream hero left, navy 2x2 nav right) */
body.hl-B #view-home .home-wrap{padding:18px 22px;gap:14px}
body.hl-B #view-home .hh-or{display:none!important}
body.hl-B #view-home{position:relative}
body.hl-B #view-home .home-hero,
body.hl-B #view-home .home-cta-grid{margin:0!important}
/* the layout wrapper — wrap hero + grid into a 2-col flex */
body.hl-B #view-home .home-wrap > .home-hero{flex:1 1 50%;max-width:none;padding:30px 36px 26px;display:flex;flex-direction:column;justify-content:center;align-items:flex-start;text-align:left;border-radius:16px}
body.hl-B #view-home .home-wrap > .home-hero *{text-align:left}
body.hl-B #view-home .home-wrap > .home-cta-grid{flex:1 1 50%;grid-template-columns:repeat(2,1fr)!important;gap:10px;align-self:stretch}
body.hl-B #view-home .home-wrap{display:grid!important;grid-template-columns:1fr 1fr;grid-template-rows:1fr auto;gap:14px 16px;align-items:stretch;padding:16px 22px}
body.hl-B #view-home .home-wrap > .home-hero{grid-column:1;grid-row:1}
body.hl-B #view-home .home-wrap > .home-cta-grid{grid-column:2;grid-row:1}
body.hl-B #view-home .home-wrap > .home-stats{grid-column:1 / span 2;grid-row:2;margin:0}
body.hl-B #view-home .hh-eye{margin:0 0 6px}
body.hl-B #view-home .hh-title{font-size:clamp(1.6rem,2.8vw,2.4rem);margin:0 0 8px;line-height:1.06;text-align:left}
body.hl-B #view-home .hh-sub{font-size:.92rem;margin:0 0 16px;text-align:left;max-width:none}
body.hl-B #view-home .hh-cta{max-width:none;width:100%;margin:auto 0 0;text-align:left}
body.hl-B #view-home .hh-hint{text-align:left;font-size:.78rem;margin:8px 0 0}
body.hl-B #view-home .home-cta-grid .hc-card{padding:18px 18px;min-height:0}
body.hl-B #view-home .home-cta-grid .hc-num{font-size:.6rem}
body.hl-B #view-home .home-cta-grid .hc-t{font-size:1.1rem}
body.hl-B #view-home .home-cta-grid .hc-d{font-size:.78rem;line-height:1.4;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
body.hl-B #view-home .home-stats{border:0;border-top:1px solid rgba(232,184,75,.22);padding-top:4px}
body.hl-B #view-home .home-stats .hs-tile{padding:8px 12px}
body.hl-B #view-home .home-stats .hs-v{font-size:1.15rem}
body.hl-B #view-home .home-stats .hs-l{font-size:.62rem}

/* ============================ */
/* C — EDITORIAL 60/40 (big cream hero left, 4 stacked nav tiles right) */
body.hl-C #view-home .home-wrap{display:grid!important;grid-template-columns:1.5fr 1fr;grid-template-rows:1fr;gap:14px;padding:18px 22px;align-items:stretch}
body.hl-C #view-home .hh-or{display:none!important}
body.hl-C #view-home .home-stats{display:none!important}
body.hl-C #view-home .home-hero{grid-column:1;margin:0;max-width:none;padding:36px clamp(28px,4vw,52px);border-radius:16px;display:flex;flex-direction:column;justify-content:center;text-align:left;align-items:flex-start}
body.hl-C #view-home .home-hero *{text-align:left}
body.hl-C #view-home .home-cta-grid{grid-column:2;grid-template-columns:1fr!important;grid-template-rows:repeat(4,1fr);gap:8px;margin:0;align-self:stretch}
body.hl-C #view-home .hh-eye{margin:0 0 6px}
body.hl-C #view-home .hh-title{font-size:clamp(1.8rem,3vw,2.6rem);line-height:1.05;margin:0 0 10px;text-align:left}
body.hl-C #view-home .hh-sub{font-size:.95rem;margin:0 0 18px;line-height:1.45;max-width:none;text-align:left}
body.hl-C #view-home .hh-cta{max-width:none;width:100%;text-align:left}
body.hl-C #view-home .hh-hint{text-align:left;font-size:.78rem}
body.hl-C #view-home .home-cta-grid .hc-card{padding:12px 16px;min-height:0;align-items:center}
body.hl-C #view-home .home-cta-grid .hc-num{font-size:.55rem;margin:0 12px 0 0}
body.hl-C #view-home .home-cta-grid .hc-body{flex:1;min-width:0}
body.hl-C #view-home .home-cta-grid .hc-t{font-size:.98rem;margin:0 0 2px}
body.hl-C #view-home .home-cta-grid .hc-d{font-size:.7rem;line-height:1.32;display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden}
body.hl-C #view-home .home-cta-grid .hc-arr{font-size:1.05rem}

/* ============================ */
/* D — INVERTED (navy hero no card + 4 cream nav tiles below) */
body.hl-D #view-home{background:linear-gradient(180deg,#0a1730 0%,#050b1c 100%)}
body.hl-D #view-home .home-wrap{padding:8px 22px 18px;gap:16px}
body.hl-D #view-home .home-stats{display:none!important}
body.hl-D #view-home .hh-or{display:none!important}
body.hl-D #view-home .home-hero{background:transparent!important;box-shadow:none!important;border:0!important;padding:20px 0 6px;margin:0 auto;max-width:980px;border-radius:0;text-align:center}
body.hl-D #view-home .hh-eye{color:var(--gold)!important;margin:0 0 6px}
body.hl-D #view-home .hh-title{color:#fff!important;font-size:clamp(1.6rem,2.8vw,2.3rem);margin:0 0 8px;line-height:1.08}
body.hl-D #view-home .hh-title em{color:var(--gold)!important}
body.hl-D #view-home .hh-title .hh-acr{color:rgba(255,255,255,.45)!important}
body.hl-D #view-home .hh-sub{color:rgba(255,255,255,.78)!important;font-size:.92rem;margin:0 auto 14px;line-height:1.4;max-width:680px}
body.hl-D #view-home .hh-sub b{color:#fff!important}
body.hl-D #view-home .hh-cta{margin:0 auto;max-width:560px;display:block}
body.hl-D #view-home .hh-cta-row{justify-content:center}
body.hl-D #view-home .hh-pick{background:rgba(255,255,255,.06)!important;color:#fff!important;border-color:rgba(232,184,75,.55)!important}
body.hl-D #view-home .hh-pick .hp-k{color:rgba(232,184,75,.78)!important;border-right-color:rgba(255,255,255,.14)!important}
body.hl-D #view-home .hh-pick .hp-name{color:#fff!important}
body.hl-D #view-home .hh-pick .hp-chev{color:rgba(232,184,75,.85)!important}
body.hl-D #view-home .hh-dd{background:rgba(15,28,56,.98)!important;border-color:rgba(232,184,75,.45)!important}
body.hl-D #view-home .hh-dd-in{color:#fff!important}
body.hl-D #view-home .hh-dd-row{color:rgba(255,255,255,.86)!important}
body.hl-D #view-home .hh-dd-row:hover,body.hl-D #view-home .hh-dd-row.kbd{background:rgba(232,184,75,.16)!important;color:#fff!important}
body.hl-D #view-home .hh-hint{color:rgba(255,255,255,.62)!important;text-align:center}
body.hl-D #view-home .hh-hint b{color:#fff!important}
/* 4 cream nav tiles in a row of 4 */
body.hl-D #view-home .home-cta-grid{grid-template-columns:repeat(4,1fr)!important;gap:10px;max-width:1180px;margin:0 auto}
body.hl-D #view-home .home-cta-grid .hc-card{background:#fffaef!important;border:1px solid rgba(181,132,32,.30)!important;color:#0c1a33!important;padding:16px 18px 18px;min-height:0;box-shadow:0 8px 22px rgba(0,0,0,.30)}
body.hl-D #view-home .home-cta-grid .hc-card:hover{background:#fff!important;border-color:rgba(181,132,32,.55)!important;transform:translateY(-2px)}
body.hl-D #view-home .home-cta-grid .hc-num{color:#b58420!important;font-size:.55rem}
body.hl-D #view-home .home-cta-grid .hc-t{color:#0c1a33!important;font-size:1.02rem;margin-bottom:4px}
body.hl-D #view-home .home-cta-grid .hc-d{color:rgba(12,26,51,.62)!important;font-size:.74rem;line-height:1.35;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
body.hl-D #view-home .home-cta-grid .hc-arr{color:#b58420!important;font-size:1.1rem}

/* ============================ */
/* E — DASHBOARD (horizontal command bar + 2x2 cream tiles) */
body.hl-E #view-home{background:linear-gradient(180deg,#0a1730 0%,#050b1c 100%)}
body.hl-E #view-home .home-wrap{padding:14px 22px 16px;gap:12px}
body.hl-E #view-home .home-stats{display:none!important}
body.hl-E #view-home .hh-or{display:none!important}
/* Hero becomes a horizontal bar */
body.hl-E #view-home .home-hero{background:rgba(244,236,211,.06)!important;border:1px solid rgba(232,184,75,.30)!important;box-shadow:none!important;padding:14px 18px!important;margin:0!important;max-width:none!important;border-radius:12px;display:grid;grid-template-columns:auto 1fr auto;gap:18px;align-items:center;text-align:left}
body.hl-E #view-home .hh-eye{display:none!important}
body.hl-E #view-home .hh-title{grid-column:1;color:#fff!important;font-size:1.15rem;margin:0;line-height:1.1;white-space:nowrap;text-align:left}
body.hl-E #view-home .hh-title em{color:var(--gold)!important;font-style:normal}
body.hl-E #view-home .hh-title .hh-acr{color:rgba(255,255,255,.4)!important;font-size:.48em}
body.hl-E #view-home .hh-sub{grid-column:2;color:rgba(255,255,255,.66)!important;font-size:.78rem;margin:0;line-height:1.4;max-width:none;text-align:left}
body.hl-E #view-home .hh-sub b{color:var(--gold)!important;text-decoration:none!important;border-bottom:0!important}
body.hl-E #view-home .hh-cta{grid-column:3;margin:0;max-width:none;width:auto}
body.hl-E #view-home .hh-hint{display:none!important}
body.hl-E #view-home .hh-pick{background:rgba(255,255,255,.06)!important;color:#fff!important;border-color:rgba(232,184,75,.55)!important;min-height:42px;padding:6px 14px}
body.hl-E #view-home .hh-pick .hp-k{color:rgba(232,184,75,.78)!important;border-right-color:rgba(255,255,255,.14)!important}
body.hl-E #view-home .hh-pick .hp-name{color:#fff!important}
body.hl-E #view-home .hh-pick .hp-chev{color:rgba(232,184,75,.85)!important}
body.hl-E #view-home .hh-primary{min-height:42px;padding:0 18px;font-size:.88rem}
body.hl-E #view-home .hh-dd{background:rgba(15,28,56,.98)!important;border-color:rgba(232,184,75,.45)!important}
body.hl-E #view-home .hh-dd-in{color:#fff!important}
body.hl-E #view-home .hh-dd-row{color:rgba(255,255,255,.86)!important}
body.hl-E #view-home .hh-dd-row:hover,body.hl-E #view-home .hh-dd-row.kbd{background:rgba(232,184,75,.16)!important;color:#fff!important}
/* Big 2x2 cream tiles taking the rest of the viewport */
body.hl-E #view-home .home-cta-grid{flex:1;grid-template-columns:repeat(2,1fr)!important;grid-template-rows:repeat(2,1fr);gap:12px;max-width:none;margin:0;min-height:0}
body.hl-E #view-home .home-cta-grid .hc-card{background:#fffaef!important;border:1px solid rgba(181,132,32,.30)!important;color:#0c1a33!important;padding:24px 28px;min-height:0;box-shadow:0 12px 30px rgba(0,0,0,.35);align-items:flex-start;justify-content:space-between}
body.hl-E #view-home .home-cta-grid .hc-card:hover{background:#fff!important;border-color:rgba(181,132,32,.55)!important;transform:translateY(-2px)}
body.hl-E #view-home .home-cta-grid .hc-num{color:#b58420!important;font-size:.7rem;letter-spacing:.16em}
body.hl-E #view-home .home-cta-grid .hc-t{color:#0c1a33!important;font-size:1.4rem;line-height:1.1;margin-bottom:8px}
body.hl-E #view-home .home-cta-grid .hc-d{color:rgba(12,26,51,.62)!important;font-size:.88rem;line-height:1.45;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
body.hl-E #view-home .home-cta-grid .hc-arr{color:#b58420!important;font-size:1.6rem;align-self:flex-end;margin-top:auto}

/* ============================ */
/* Picker (bottom) */
#hlp{position:fixed;left:50%;bottom:14px;transform:translateX(-50%);z-index:99999;display:flex;flex-wrap:wrap;justify-content:center;gap:4px;max-width:94vw;padding:6px 8px;background:rgba(15,28,56,.97);border:1px solid rgba(232,184,75,.55);border-radius:10px;box-shadow:0 12px 32px rgba(0,0,0,.5)}
#hlp button{font-family:'JetBrains Mono',monospace;font-size:.55rem;letter-spacing:.04em;text-transform:uppercase;font-weight:700;padding:6px 9px;border-radius:5px;border:1px solid rgba(255,255,255,.16);background:transparent;color:rgba(255,255,255,.72);cursor:pointer;white-space:nowrap}
#hlp button.on{background:#f4ecd3;color:#0c1a33;border-color:rgba(181,132,32,.65)}
"""

PICKER = r"""
<div id="hlp" aria-label="Home layout options">
  <button data-h="cur">Current</button>
  <button data-h="A">A &middot; Compact</button>
  <button data-h="B">B &middot; Split 50/50</button>
  <button data-h="C">C &middot; Editorial 60/40</button>
  <button data-h="D">D &middot; Navy hero</button>
  <button data-h="E">E &middot; Dashboard</button>
</div>
<script>
(function(){
  var btns=document.querySelectorAll('#hlp button');
  function apply(v){
    document.body.classList.remove('hl-A','hl-B','hl-C','hl-D','hl-E');
    void document.body.offsetWidth; /* reflow */
    if(v!=='cur') document.body.classList.add('hl-'+v);
    btns.forEach(b=>b.classList.toggle('on', b.dataset.h===v));
    try{localStorage.setItem('dhi_hl', v);}catch(e){}
  }
  btns.forEach(b=>b.addEventListener('click',()=>apply(b.dataset.h)));
  var init='A'; try{ init=localStorage.getItem('dhi_hl')||init; }catch(e){}
  setTimeout(function(){
    /* force the Home tab on initial show */
    if(typeof show==='function') show('home');
    apply(init);
  }, 300);
})();
</script>
"""

assert '</style>' in h, 'no </style> tag found'
h = h.replace('</style>', CSS + '</style>', 1)
assert '</body>' in h, 'no </body> tag found'
h = h.replace('</body>', PICKER + '</body>', 1)

open(DST, 'w').write(h)
print('built ' + DST + ' (' + str(round(len(h)/1024/1024, 2)) + ' MB) — picker with 5 home layouts')
