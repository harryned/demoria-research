"""Restructure topbar to 5 purpose-grouped tabs + add sub-tab bar,
apply the Editorial 60/40 home layout, and expand the home nav grid
to 6 cards in a 2x3 grid.

Tab structure (5 main tabs):
  Home  Explore  Read  Research  Data
With dynamic sub-tabs under each group:
  Explore  → World · Index & Rankings · Compare
  Read     → About · So What? · Methodology · Author
  Data     → Data tables · Raw data explorer
  (Home, Research are single-destination — no sub-tabs)

Idempotent via the TABS-APPLIED marker.
"""
SRC = 'dhi_globe.html'
h = open(SRC).read()
if '/* TABS-APPLIED */' in h:
    print('already applied; skipping')
    raise SystemExit(0)

# ---------- 1. Replace the topbar <nav class="tabs">...</nav> ----------
old_nav = ('<nav class="tabs">'
 '<button class="tab on" data-v="home">Home</button>'
 '<span class="tab-sep"></span>'
 '<button class="tab" data-v="world">World</button>'
 '<span class="tab-sep"></span>'
 '<button class="tab" data-v="rankings">Index &amp; Rankings</button>'
 '<span class="tab-sep"></span>'
 '<button class="tab" data-v="compare">Compare</button>'
 '<span class="tab-sep"></span>'
 '<button class="tab" data-v="about">About</button>'
 '<button class="tab sowhat" data-v="sowhat">So What?</button>'
 '<button class="tab" data-v="method">Methodology</button>'
 '<button class="tab" data-v="author">Author</button>'
 '<span class="tab-sep"></span>'
 '<button class="tab" data-v="research">Research</button>'
 '<span class="tab-sep"></span>'
 '<button class="tab" data-v="data">Data</button>'
 '<button class="tab" data-v="rawdata">Raw Data</button>'
 '</nav>')
new_nav = ('<nav class="tabs">'
 '<button class="tab on" data-v="home">Home</button>'
 '<span class="tab-sep"></span>'
 '<button class="tab" data-grp="explore" data-v="world">Explore</button>'
 '<span class="tab-sep"></span>'
 '<button class="tab" data-grp="read" data-v="about">Read</button>'
 '<span class="tab-sep"></span>'
 '<button class="tab" data-v="research">Research</button>'
 '<span class="tab-sep"></span>'
 '<button class="tab" data-grp="data" data-v="data">Data</button>'
 '</nav>'
 '<nav class="subtabs" id="subtabs" aria-label="Section sub-navigation"></nav>')

assert old_nav in h, 'old topbar nav not found — bail'
h = h.replace(old_nav, new_nav, 1)

# ---------- 2. CSS additions ----------
CSS = r"""
/* TABS-APPLIED */
/* === sub-tab bar === */
.subtabs{display:none;align-items:center;justify-content:center;gap:14px;padding:6px 18px 8px;background:rgba(15,28,56,.94);border-bottom:1px solid rgba(232,184,75,.18);font-family:'JetBrains Mono',monospace}
.subtabs.on{display:flex;flex-wrap:wrap}
.subtabs button{background:transparent;border:0;color:rgba(255,255,255,.55);font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:.18em;text-transform:uppercase;font-weight:700;padding:5px 10px;cursor:pointer;border-radius:5px;transition:color .15s,background .15s}
.subtabs button:hover{color:#fff;background:rgba(232,184,75,.10)}
.subtabs button.on{color:#0c1a33;background:#f4ecd3}
.subtabs .st-sep{color:rgba(255,255,255,.18);font-size:.6rem;letter-spacing:0}

/* hide So What? exception once we collapse into Read */
.tab.sowhat{display:inline-block}

/* === Editorial 60/40 live home === */
#view-home{height:calc(100vh - 90px);overflow:hidden}
#view-home .home-wrap{height:100%;display:grid!important;grid-template-columns:1.5fr 1fr;gap:14px;padding:18px 22px;align-items:stretch;box-sizing:border-box}
#view-home .home-ribbon,
#view-home .home-cta-h,
#view-home .home-cta-h-2,
#view-home .home-stats,
#view-home .hc-api,
#view-home .home-foot{display:none!important}
#view-home .hh-or{display:none!important}
#view-home .home-hero{grid-column:1;margin:0;max-width:none;padding:36px clamp(28px,4vw,52px);border-radius:16px;display:flex;flex-direction:column;justify-content:center;text-align:left;align-items:flex-start}
#view-home .home-hero *{text-align:left}
#view-home .home-hero .hh-eye{margin:0 0 6px}
#view-home .home-hero .hh-title{font-size:clamp(1.7rem,2.8vw,2.4rem);line-height:1.05;margin:0 0 10px;text-align:left}
#view-home .home-hero .hh-sub{font-size:.92rem;margin:0 0 18px;line-height:1.45;max-width:none;text-align:left}
#view-home .home-hero .hh-cta{max-width:none;width:100%;text-align:left;margin-top:auto}
#view-home .home-hero .hh-hint{text-align:left;font-size:.78rem;margin:8px 0 0}
/* Cards: 2x3 grid */
#view-home .home-cta-grid{grid-column:2;grid-template-columns:repeat(2,1fr)!important;grid-template-rows:repeat(3,1fr);gap:8px;margin:0;align-self:stretch;max-width:none;padding:0}
#view-home .home-cta-grid .hc-card{padding:10px 12px;min-height:0;align-items:flex-start;border-radius:12px}
#view-home .home-cta-grid .hc-num{font-size:.5rem;letter-spacing:.16em;margin-bottom:5px}
#view-home .home-cta-grid .hc-body{flex:1;min-width:0}
#view-home .home-cta-grid .hc-t{font-size:.9rem;line-height:1.1;margin:0 0 3px}
#view-home .home-cta-grid .hc-d{font-size:.66rem;line-height:1.32;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden;color:var(--ink2)}
#view-home .home-cta-grid .hc-arr{font-size:1rem;color:var(--gold)}

@media (max-width:900px){
  #view-home{height:auto;overflow:auto}
  #view-home .home-wrap{grid-template-columns:1fr;grid-template-rows:auto auto}
  #view-home .home-hero{grid-column:1;grid-row:1}
  #view-home .home-cta-grid{grid-column:1;grid-row:2;grid-template-rows:repeat(6,auto)}
}
"""
assert '</style>' in h, '</style> not found'
h = h.replace('</style>', CSS + '</style>', 1)

# ---------- 3. Replace the home CTA grid (4 cards → 6 cards) ----------
old_grid = ('<div class="home-cta-grid">\n'
 '  <button class="hc-card hc-world" data-go="world"><div class="hc-num">01</div><div class="hc-body"><div class="hc-t">World map</div><div class="hc-d">Globe &amp; flat map &middot; colour by composite DHI or any single pillar &middot; scrub through 1965&ndash;2100</div></div><div class="hc-arr">&rsaquo;</div></button>\n'
 '  <button class="hc-card hc-rank" data-go="rankings"><div class="hc-num">02</div><div class="hc-body"><div class="hc-t">Index &amp; Rankings</div><div class="hc-d">All 236 countries &amp; territories &middot; ranked, profiled, with pillar contributions and 1965&ndash;2100 trajectory charts</div></div><div class="hc-arr">&rsaquo;</div></button>\n'
 '  <button class="hc-card hc-method" data-go="about"><div class="hc-num">03</div><div class="hc-body"><div class="hc-t">Read the index</div><div class="hc-d">About &middot; So What? &middot; Methodology &middot; Author &mdash; the four-pillar framework, why renewal matters, who built this</div></div><div class="hc-arr">&rsaquo;</div></button>\n'
 '  <button class="hc-card hc-research" data-go="research"><div class="hc-num">04</div><div class="hc-body"><div class="hc-t">Research notes</div><div class="hc-d">Alternative views of the demographic record &mdash; China under Yi Fuxian, with more notes in preparation</div></div><div class="hc-arr">&rsaquo;</div></button>\n'
 '</div>')

new_grid = ('<div class="home-cta-grid">\n'
 '  <button class="hc-card hc-world" data-go="world"><div class="hc-num">01</div><div class="hc-body"><div class="hc-t">World map</div><div class="hc-d">Globe &amp; flat map &middot; recolour by any pillar &middot; scrub 1965&ndash;2100</div></div><div class="hc-arr">&rsaquo;</div></button>\n'
 '  <button class="hc-card hc-rank" data-go="rankings"><div class="hc-num">02</div><div class="hc-body"><div class="hc-t">Index &amp; Rankings</div><div class="hc-d">All 236 ranked &middot; pillar contributions &middot; trajectory charts</div></div><div class="hc-arr">&rsaquo;</div></button>\n'
 '  <button class="hc-card hc-cmp" data-go="compare"><div class="hc-num">03</div><div class="hc-body"><div class="hc-t">Compare</div><div class="hc-d">Up to three countries side-by-side &mdash; scores, pillars, projections</div></div><div class="hc-arr">&rsaquo;</div></button>\n'
 '  <button class="hc-card hc-method" data-go="about"><div class="hc-num">04</div><div class="hc-body"><div class="hc-t">Read the index</div><div class="hc-d">About &middot; So What? &middot; Methodology &middot; Author</div></div><div class="hc-arr">&rsaquo;</div></button>\n'
 '  <button class="hc-card hc-research" data-go="research"><div class="hc-num">05</div><div class="hc-body"><div class="hc-t">Research notes</div><div class="hc-d">Alternative views &mdash; China under Yi Fuxian, with more in preparation</div></div><div class="hc-arr">&rsaquo;</div></button>\n'
 '  <button class="hc-card hc-data" data-go="data"><div class="hc-num">06</div><div class="hc-body"><div class="hc-t">Data &amp; explorer</div><div class="hc-d">JSON / CSV downloads &middot; raw indicator series &middot; sourcing PDF</div></div><div class="hc-arr">&rsaquo;</div></button>\n'
 '</div>')

assert old_grid in h, 'old home grid not found — bail'
h = h.replace(old_grid, new_grid, 1)

# ---------- 4. Patch show() for group on-state + sub-tab render ----------
JS_PATCH = r"""
/* === group on-state + sub-tab rendering === */
(function(){
  var TAB_GROUP={world:'explore',rankings:'explore',compare:'explore',about:'read',sowhat:'read',method:'read',author:'read',data:'data',rawdata:'data'};
  var SUBTABS={
    explore:[{v:'world',label:'World map'},{v:'rankings',label:'Index &amp; Rankings'},{v:'compare',label:'Compare'}],
    read:[{v:'about',label:'About'},{v:'sowhat',label:'So What?'},{v:'method',label:'Methodology'},{v:'author',label:'Author'}],
    data:[{v:'data',label:'Data tables'},{v:'rawdata',label:'Raw data explorer'}]
  };
  var bar=document.getElementById('subtabs'); if(!bar) return;
  function render(v){
    var grp=TAB_GROUP[v]||null;
    var tabs=document.querySelectorAll('.tabs .tab');
    tabs.forEach(function(t){
      var on = (t.dataset.v===v) || (grp && t.dataset.grp===grp);
      t.classList.toggle('on', on);
    });
    if(!grp || !SUBTABS[grp]){ bar.classList.remove('on'); bar.innerHTML=''; return; }
    var items=SUBTABS[grp];
    bar.innerHTML = items.map(function(it,i){
      var sep = i ? '<span class="st-sep">&middot;</span>' : '';
      return sep+'<button data-v="'+it.v+'"'+(it.v===v?' class="on"':'')+'>'+it.label+'</button>';
    }).join('');
    bar.classList.add('on');
  }
  // Wire sub-tab clicks
  bar.addEventListener('click', function(e){
    var btn=e.target.closest('button[data-v]'); if(!btn) return;
    if(typeof show==='function') show(btn.dataset.v);
  });
  // Hook into show() — wrap once
  if(typeof window.show==='function' && !window.__showWrapped){
    var orig=window.show;
    window.show=function(v){
      orig(v);
      render(v);
    };
    window.__showWrapped=true;
    // Initial render
    var cur=(document.querySelector('.view.on')||{}).id;
    if(cur){
      cur=cur.replace(/^view-/,'');
      render(cur);
    }
  }
})();
"""
# Inject right before </body>
assert '</body>' in h, '</body> not found'
h = h.replace('</body>', '<script>'+JS_PATCH+'</script></body>', 1)

open(SRC, 'w').write(h)
print('applied tabs + Editorial 60/40 home + 6-card 2x3 grid to '+SRC+' ('+str(round(len(h)/1024/1024,2))+' MB)')
