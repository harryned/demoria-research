#!/usr/bin/env python3
"""Demoria Research — the Pronatal Policy Library.

A curated, honestly-evaluated catalogue of pro-natal policies governments have
tried, so a reader can hand-pick by mechanism, budget and what actually moved
the needle. The editorial spine is honesty: most cash incentives shift the
*timing* of births (tempo), not the number a woman ends up having (quantum);
the most durable effects come from comprehensive work-family reconciliation;
and no country has engineered a return to replacement fertility by policy alone.

Effect summaries synthesise the OECD Family Database and the demographic
literature (e.g. Gauthier; Sobotka, Matysiak & Brzozowska; Bergsvik, Fauske &
Hart 2021; Doepke et al. 2023). Isolating a policy's causal effect on fertility
is genuinely hard — verdicts are deliberately cautious.

Output: public/policies/index.html
"""
import html, json

# mechanism -> colour
MECH = {
    "Cash": "#d6336c", "Leave": "#2e9e5b", "Childcare": "#1d9e8f",
    "Housing": "#d98a2b", "Tax": "#4f5bd5", "Culture": "#7a4fd0",
    "Immigration": "#5a6b82", "Access": "#0d8f9e",
}
# verdict -> (label colour bg)
VERD = {
    "Cautionary": ("#c84a3a", "rgba(200,74,58,.14)"),
    "Mixed": ("#c08a1e", "rgba(192,138,30,.16)"),
    "Promising": ("#2e9e5b", "rgba(46,158,91,.16)"),
}

# Each policy: country, year, policy, mechs[], cost, effect, evidence, verdict, blurb, source
POLICIES = [
 ("France", "1939–", "Code de la famille → allocations familiales, quotient familial, crèches & école maternelle",
  ["Childcare","Tax","Cash"], "~3.5–4% of GDP on family policy",
  "Sustained TFR near 1.9–2.0 for decades — long the highest in Western Europe (1.68 by 2023).",
  "Strong", "Promising",
  "The closest thing to a durable success — and tellingly it is not a baby bonus. A century of comprehensive, predictable support (universal childcare, generous tax treatment of larger families, a pro-family norm) kept fertility unusually high. Even France is now drifting down, which is the honest lesson: comprehensive systems raise the ceiling, they don't defy gravity.",
  "OECD Family Database; INED"),

 ("Sweden", "1974–", "Earnings-related parental leave, subsidised universal childcare, the “speed premium”",
  ["Leave","Childcare"], "~3–3.5% of GDP",
  "Held TFR around 1.7–1.9 for decades on a gender-equal model; fell to ~1.45 by 2023.",
  "Strong", "Promising",
  "The Nordic template: make work and children compatible and fertility holds up without cash bribes. The “speed premium” (keep your benefit level if you have the next child quickly) measurably affected birth spacing. The recent decline across all Nordics is a warning that even the best-designed reconciliation policy has a ceiling.",
  "OECD Family Database; Andersson et al."),

 ("Hungary", "2010–", "Family tax base, CSOK housing grants, lifetime income-tax exemption for mothers of 4+, subsidised loans",
  ["Tax","Housing","Cash"], "~5% of GDP — among the highest in the world",
  "TFR rose from ~1.23 (2011) to ~1.5–1.6 (2021); much is marriage-timing and tempo, and it has since slipped.",
  "Contested", "Mixed",
  "The most aggressive fiscal effort anywhere, and a genuine partial rebound — but how much is durable fertility versus brought-forward births and a marriage boom is hotly debated. Worth studying precisely because it tests whether money at scale can work; the early read is “somewhat, expensively, and not back to replacement.”",
  "Hungarian CSO (KSH); Sobotka et al."),

 ("South Korea", "2006–", "Basic Plan for Low Fertility — cumulative cash, childcare and housing spending exceeding US$280bn",
  ["Cash","Childcare","Housing"], ">US$280bn cumulative",
  "TFR fell to 0.72 (2023) — the lowest ever recorded for a sovereign state.",
  "Strong", "Cautionary",
  "The defining cautionary tale: enormous, sustained spending alongside the world's steepest decline. The lesson is not that policy is useless but that cheques cannot offset crushing education costs, brutal work hours, housing prices and gender-role conflict. Without fixing the structural drivers, the money is poured into a leaking bucket.",
  "Statistics Korea (KOSTAT)"),

 ("Singapore", "1987–", "Baby Bonus cash gift + Child Development Account (matched savings) + Marriage & Parenthood Package",
  ["Cash"], "~S$3bn+/yr across the package",
  "TFR drifted to ~1.0 with no durable rise despite repeated top-ups.",
  "Moderate", "Cautionary",
  "Decades of escalating cash and matched savings have not bent the curve, in a high-cost, high-pressure society. A clean demonstration that bonus size is not the binding constraint when the cost and culture of raising children dominate the decision.",
  "Singapore Dept. of Statistics"),

 ("Russia", "2007–", "Maternity (Family) Capital — large lump sum, originally for a second child",
  ["Cash","Housing"], "~0.4–0.7% of GDP",
  "Produced a clear tempo response — births were pulled forward — with limited effect on completed family size.",
  "Moderate", "Mixed",
  "One of the better-studied cash schemes. It demonstrably shifted the timing and raised second-birth probabilities for a while, but the boost faded as the cohort “caught up.” The canonical example of tempo without much quantum.",
  "Rosstat; academic evaluations"),

 ("Estonia", "2004–", "Parental benefit — up to ~18 months at full previous salary",
  ["Leave"], "~0.8% of GDP",
  "TFR rose from ~1.5 to ~1.7 through the 2010s, among the more credible leave-linked gains.",
  "Moderate", "Promising",
  "A generous, earnings-replacing leave that plausibly contributed to a real (if modest) recovery, especially for educated working women. Evidence that protecting income and career around a birth can move fertility — though Estonia, too, has since softened.",
  "Statistics Estonia; OECD"),

 ("Germany", "2007–", "Elterngeld (earnings-related parental allowance) + large Kita childcare expansion",
  ["Leave","Childcare"], "~0.4% of GDP on Elterngeld + childcare investment",
  "Fathers' leave-taking jumped; TFR recovered modestly from ~1.36 to ~1.5 over a decade.",
  "Moderate", "Promising",
  "A deliberate shift from cash toward time and childcare. The cash allowance changed *who* takes leave (far more fathers) more than the birth rate; the childcare expansion is the part most associated with the fertility uptick. A useful natural experiment in “time and services beat bonuses.”",
  "Destatis; OECD"),

 ("Czechia", "1995–", "Flexible parental allowance (parent chooses duration/intensity) + leave",
  ["Leave","Cash"], "~1% of GDP",
  "TFR recovered strongly from ~1.13 (1999) to ~1.83 (2021) before falling back.",
  "Moderate", "Mixed",
  "One of post-communist Europe's sharpest recoveries, partly a real rise and partly the unwinding of births postponed during the 1990s transition. The flexibility (let parents trade money for time on their own terms) is the interesting design feature.",
  "Czech Statistical Office"),

 ("Japan", "1994–", "Angel Plans → childcare expansion, “ikumen” campaigns, recent child allowances",
  ["Childcare","Cash","Culture"], "rising, ~1.5–2% of GDP on family policy",
  "TFR has hovered ~1.3–1.45 with a long slow decline despite repeated plans.",
  "Moderate", "Cautionary",
  "Thirty years of plans have slowed but not stopped the decline. Long working hours, rigid gender roles and the cost of education keep the realised family below the desired one. Recent allowance expansions are again testing cash where the constraints look structural.",
  "Japan MHLW / NIPSSR"),

 ("Poland", "2016–", "Rodzina 500+ — flat monthly cash benefit per child",
  ["Cash"], "~1.3% of GDP",
  "A small short-term bump faded; TFR fell to ~1.2 by 2023.",
  "Moderate", "Cautionary",
  "A flagship, expensive child transfer that succeeded as anti-poverty policy and largely failed as fertility policy — a brief tempo effect, then decline. Reinforces that unconditional cash rarely changes completed fertility.",
  "Statistics Poland (GUS)"),

 ("Australia", "2004–2014", "“Baby Bonus” lump-sum payment (Costello: “one for mum, one for dad, one for the country”)",
  ["Cash"], "~A$1.2bn/yr at peak",
  "A modest, mostly-tempo bump while it ran; abolished in 2014 with no lasting effect.",
  "Moderate", "Cautionary",
  "A textbook cash bonus: a visible short-run rise in births (and some pulled-forward timing), no durable change in family size, then quietly scrapped on cost grounds. Often cited as the clearest natural experiment in tempo effects.",
  "ABS; academic evaluations"),

 ("Spain", "2007–2010", "“Cheque bebé” — €2,500 universal birth grant",
  ["Cash"], "~€1.2bn/yr",
  "Associated with a small birth increase, then a fertility dip after it was abolished in austerity.",
  "Moderate", "Cautionary",
  "Introduced in good times, cut in the crisis — and studies suggest it both pulled some births forward and that its removal pushed some back. A neat illustration of how cash mainly reschedules births around the policy's own lifespan.",
  "INE; González (2013)"),

 ("Italy", "2022–", "Assegno Unico Universale (universal monthly child allowance), consolidating earlier bonuses",
  ["Cash","Tax"], "~1.2% of GDP",
  "TFR ~1.2 and still falling; too early for a durable verdict, but no rebound yet.",
  "Low", "Cautionary",
  "A sensible simplification of a patchwork of bonuses into one universal allowance. But against very low childcare coverage in the south, precarious youth employment and late home-leaving, a transfer alone is unlikely to move the dial — and so far hasn't.",
  "ISTAT; OECD"),

 ("Finland", "1937–", "The maternity “baby box” + Nordic leave and childcare",
  ["Childcare","Leave"], "~3% of GDP on family policy",
  "Iconic welfare, but TFR still fell sharply to ~1.26 (2022).",
  "Moderate", "Mixed",
  "Proof that even a celebrated, comprehensive, gender-equal welfare model is not fertility-proof. The baby box is wonderful social policy and a weak fertility lever; Finland's steep decline despite Nordic supports is one of the field's genuine puzzles.",
  "Statistics Finland; OECD"),

 ("Georgia", "2008", "Patriarch Ilia II's pledge to personally baptise every third+ child",
  ["Culture"], "≈ zero fiscal cost",
  "A pronounced, well-documented rise in third-plus births around 2008; TFR jumped from ~1.6 toward ~2.0.",
  "Moderate", "Promising",
  "A rare, near-costless cultural lever with a real measured effect — a trusted institution made a high-order birth socially meaningful. Not transplantable as policy, but a powerful reminder that norms and meaning can move fertility where money struggles to.",
  "Georgia Geostat; academic case studies"),

 ("Israel", "ongoing", "Pro-family norms + the world's most generous state-funded IVF",
  ["Culture","Access"], "IVF fully funded to two live births",
  "Sustained TFR ~3.0 — uniquely high for a wealthy country.",
  "Strong", "Promising",
  "The standout high-fertility developed nation, driven overwhelmingly by culture, religiosity and strong family norms — with policy (notably unlimited funded IVF) supporting rather than creating the outcome. The honest reading: the biggest lever is the hardest for a government to pull deliberately.",
  "Israel CBS"),

 ("China", "2016–", "End of the One-Child Policy → two- then three-child limits + local incentives",
  ["Cash","Housing","Culture"], "growing local-government incentives",
  "Births kept falling (to ~9.0m in 2023); the population began shrinking in 2022.",
  "Strong", "Cautionary",
  "The decisive proof that removing a restriction is not the same as raising fertility. Decades of low-fertility norms, sky-high child-rearing and education costs and a shrinking pool of women of childbearing age are now locked in; incentives are arriving against a tide that policy itself helped create.",
  "China NBS"),

 ("Iran", "2012–", "Reversal of a successful family-planning programme: cut contraception access, marriage/baby loans",
  ["Cash","Access"], "subsidised marriage & childbearing loans",
  "TFR has held ~1.7 with little sign the restrictions raised it.",
  "Moderate", "Cautionary",
  "After one of history's fastest fertility declines, the state tried to reverse course by restricting contraception and offering loans. The limited response underlines how hard it is to re-raise fertility once the transition to small families is socially complete.",
  "Statistical Centre of Iran"),

 ("United States", "2021", "One-year expanded Child Tax Credit (the laissez-faire baseline)",
  ["Cash","Tax"], "~US$100bn for the one-year expansion",
  "Sharply cut child poverty; no detectable fertility effect. TFR ~1.6, long propped up by immigration.",
  "Moderate", "Mixed",
  "Included as the “almost no explicit pronatal policy” case. The expanded CTC was excellent anti-poverty policy with no measurable birth effect, and US population growth has leaned on immigration rather than births — a reminder that the migration lever is the one democracies actually use.",
  "US Census Bureau; CBPP"),

 ("Norway", "1990s–", "Cash-for-care benefit (kontantstøtte) for parents not using public childcare",
  ["Cash","Childcare"], "~0.2% of GDP",
  "No fertility gain; evidence it reduced mothers' employment, and TFR fell to ~1.4 (2023).",
  "Moderate", "Cautionary",
  "An instructive counter-design: paying parents to stay *out* of subsidised childcare. It didn't raise births and it lowered maternal employment — the mirror image of the Nordic reconciliation model, and a caution that not all “family cash” points the same way.",
  "Statistics Norway (SSB)"),
]

CSS = """
:root{--navy:#0f2347;--navy2:#0b1730;--gold:#e8b84b;--golddk:#b58420;--cream:#f4ecd3;--cream2:#fcf4dd;--ink:#0c1a33}
*{box-sizing:border-box}
body{margin:0;background:var(--navy);color:#eef1f6;font-family:'Manrope',system-ui,sans-serif;-webkit-font-smoothing:antialiased}
.tb{position:sticky;top:0;z-index:30;display:flex;align-items:center;gap:14px;background:#ece2c8;padding:11px 22px;border-bottom:2px solid rgba(181,132,32,.45)}
.tb-back{font-family:'JetBrains Mono',monospace;font-size:.7rem;font-weight:700;letter-spacing:.12em;text-transform:uppercase;color:#0c1a33;text-decoration:none}
.tb-back:hover{color:#b58420}
.tb-t{font-weight:800;color:#0c1a33;font-size:1.02rem;letter-spacing:-.01em}
.tb-sep{width:1px;height:16px;background:rgba(12,26,51,.3)}
.wrap{max-width:1180px;margin:0 auto;padding:54px clamp(20px,4vw,56px) 90px}
.eyebrow{font-family:'JetBrains Mono',monospace;font-size:.66rem;letter-spacing:.22em;text-transform:uppercase;color:var(--gold);font-weight:700;text-align:center;margin-bottom:14px}
h1{font-weight:800;font-size:clamp(2.1rem,4.4vw,3.3rem);letter-spacing:-.02em;text-align:center;margin:0 0 16px;line-height:1.05}
h1 em{color:var(--gold);font-style:normal}
.lead{max-width:70ch;margin:0 auto 10px;text-align:center;font-size:1.05rem;line-height:1.6;color:rgba(238,241,246,.82)}
.note{max-width:74ch;margin:0 auto 30px;text-align:center;font-size:.86rem;line-height:1.55;color:rgba(238,241,246,.55)}
.bigtake{max-width:1000px;margin:0 auto 34px;background:rgba(232,184,75,.08);border:1px solid rgba(232,184,75,.34);border-radius:14px;padding:20px 26px}
.bigtake b{color:var(--gold)}
.bigtake p{margin:0;font-size:.96rem;line-height:1.6;color:rgba(238,241,246,.88)}
.filters{display:flex;flex-wrap:wrap;gap:8px;justify-content:center;margin:0 auto 28px;max-width:980px}
.fchip{font-family:'JetBrains Mono',monospace;font-size:.66rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:rgba(238,241,246,.72);background:rgba(255,255,255,.04);border:1px solid rgba(255,255,255,.14);border-radius:999px;padding:7px 13px;cursor:pointer;transition:.14s}
.fchip:hover{color:#fff;border-color:rgba(232,184,75,.5)}
.fchip.on{color:#0c1a33;background:var(--gold);border-color:var(--gold)}
.grid{display:grid;grid-template-columns:repeat(2,1fr);gap:18px}
@media(max-width:820px){.grid{grid-template-columns:1fr}}
.card{background:var(--cream2);color:var(--ink);border-radius:16px;border-top:4px solid var(--mc);padding:22px 24px 20px;display:flex;flex-direction:column;box-shadow:0 16px 40px rgba(0,0,0,.30)}
.c-top{display:flex;align-items:center;gap:8px;flex-wrap:wrap;margin-bottom:12px}
.tag{font-family:'JetBrains Mono',monospace;font-size:.58rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;color:#fff;background:var(--mc);border-radius:5px;padding:3px 7px}
.verd{font-family:'JetBrains Mono',monospace;font-size:.58rem;font-weight:700;letter-spacing:.07em;text-transform:uppercase;border-radius:5px;padding:3px 7px;margin-left:auto}
.c-country{font-weight:800;font-size:1.32rem;letter-spacing:-.01em;line-height:1.1}
.c-country span{font-weight:600;color:rgba(12,26,51,.5);font-size:.92rem}
.c-policy{font-size:.92rem;font-weight:600;color:rgba(12,26,51,.78);margin:5px 0 14px;line-height:1.3}
.kv{display:grid;grid-template-columns:auto 1fr;gap:4px 12px;margin-bottom:12px}
.kv .k{font-family:'JetBrains Mono',monospace;font-size:.58rem;font-weight:700;letter-spacing:.06em;text-transform:uppercase;color:var(--golddk);padding-top:2px}
.kv .v{font-size:.85rem;line-height:1.4;color:rgba(12,26,51,.82)}
.c-blurb{font-size:.88rem;line-height:1.52;color:rgba(12,26,51,.74);flex:1}
.c-src{margin-top:13px;padding-top:11px;border-top:1px solid rgba(12,26,51,.1);font-family:'JetBrains Mono',monospace;font-size:.6rem;letter-spacing:.04em;color:rgba(12,26,51,.5)}
.legend{display:flex;gap:18px;justify-content:center;flex-wrap:wrap;margin:30px auto 0;font-family:'JetBrains Mono',monospace;font-size:.64rem;letter-spacing:.06em;color:rgba(238,241,246,.6)}
.legend span{display:inline-flex;align-items:center;gap:6px}
.dot{width:9px;height:9px;border-radius:50%;display:inline-block}
.empty{display:none;text-align:center;color:rgba(238,241,246,.5);padding:40px;font-size:.95rem}
footer{text-align:center;color:rgba(238,241,246,.4);font-family:'JetBrains Mono',monospace;font-size:.62rem;letter-spacing:.1em;margin-top:46px}
"""

JS = """
var chips=[].slice.call(document.querySelectorAll('.fchip'));
var cards=[].slice.call(document.querySelectorAll('.card'));
var state={mech:'all',verd:'all'};
function apply(){
  var shown=0;
  cards.forEach(function(c){
    var okM=state.mech==='all'||(c.dataset.mech||'').split('|').indexOf(state.mech)>=0;
    var okV=state.verd==='all'||c.dataset.verd===state.verd;
    var on=okM&&okV; c.style.display=on?'flex':'none'; if(on)shown++;
  });
  document.getElementById('empty').style.display=shown?'none':'block';
}
chips.forEach(function(ch){ch.addEventListener('click',function(){
  var g=ch.dataset.g, v=ch.dataset.v;
  chips.filter(function(o){return o.dataset.g===g;}).forEach(function(o){o.classList.remove('on');});
  ch.classList.add('on'); state[g]=v; apply();
});});
"""


def esc(s):
    return html.escape(str(s))


def card_html(p):
    country, year, policy, mechs, cost, effect, evidence, verdict, blurb, source = p
    mc = MECH[mechs[0]]
    vcol, vbg = VERD[verdict]
    tags = "".join('<span class="tag" style="background:%s">%s</span>' % (MECH[m], esc(m)) for m in mechs)
    return (
        '<article class="card" data-mech="%s" data-verd="%s" style="--mc:%s">'
        '<div class="c-top">%s<span class="verd" style="color:%s;background:%s">%s</span></div>'
        '<div class="c-country">%s <span>· %s</span></div>'
        '<div class="c-policy">%s</div>'
        '<div class="kv">'
        '<div class="k">Cost</div><div class="v">%s</div>'
        '<div class="k">Effect</div><div class="v">%s</div>'
        '<div class="k">Evidence</div><div class="v">%s</div>'
        '</div>'
        '<div class="c-blurb">%s</div>'
        '<div class="c-src">Source · %s</div>'
        '</article>'
    ) % (
        "|".join(mechs), esc(verdict), mc, tags, vcol, vbg, esc(verdict),
        esc(country), esc(year), esc(policy), esc(cost), esc(effect), esc(evidence),
        esc(blurb), esc(source),
    )


def build():
    mechs = list(MECH.keys())
    mech_chips = '<button class="fchip on" data-g="mech" data-v="all">All mechanisms</button>' + "".join(
        '<button class="fchip" data-g="mech" data-v="%s">%s</button>' % (m, esc(m)) for m in mechs)
    verd_chips = '<button class="fchip on" data-g="verd" data-v="all">All verdicts</button>' + "".join(
        '<button class="fchip" data-g="verd" data-v="%s">%s</button>' % (v, esc(v)) for v in VERD)
    cards = "".join(card_html(p) for p in POLICIES)
    legend = "".join(
        '<span><i class="dot" style="background:%s"></i>%s</span>' % (VERD[v][0], esc(v)) for v in VERD)

    page = """<!DOCTYPE html><html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>The Pronatal Policy Library · Demoria Research</title>
<meta name="description" content="A curated, honestly-evaluated catalogue of pro-natal policies governments have tried — filter by mechanism, budget and what actually moved the needle.">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&family=JetBrains+Mono:wght@400;700&display=swap" rel="stylesheet">
<style>__CSS__</style></head>
<body>
<div class="tb"><a class="tb-back" href="/dhi/">&lsaquo; Back to DHI</a><span class="tb-sep"></span><span class="tb-t">Pronatal Policy Library</span></div>
<div class="wrap">
<div class="eyebrow">Demoria Research · Insights</div>
<h1>The Pronatal <em>Policy</em> Library</h1>
<p class="lead">What governments have actually tried when births fall — and what really moved the needle. Pick by mechanism, budget and result.</p>
<p class="note">Effects are summarised from the OECD Family Database and the demographic literature. Isolating a single policy's causal effect on fertility is genuinely hard, so verdicts are deliberately cautious.</p>
<div class="bigtake"><p><b>What the evidence says.</b> Across the record, three patterns hold. Cash bonuses mostly change the <b>timing</b> of births, not the number a family ends up having. The most durable effects come from <b>comprehensive work-family reconciliation</b> — childcare, leave and predictable support — not one-off cheques. And <b>no country has engineered a return to replacement fertility by policy alone</b>; culture, cost and norms do most of the work. The honest use of this library is to find the least-bad bet for your context, not a silver bullet.</p></div>
<div class="filters">__MECHCHIPS__</div>
<div class="filters">__VERDCHIPS__</div>
<div class="grid">__CARDS__</div>
<div class="empty" id="empty">No policies match that combination.</div>
<div class="legend">__LEGEND__</div>
<footer>DEMORIA RESEARCH · DEMORIARESEARCH.COM</footer>
</div>
<script>__JS__</script>
</body></html>"""
    page = (page.replace("__CSS__", CSS).replace("__MECHCHIPS__", mech_chips)
            .replace("__VERDCHIPS__", verd_chips).replace("__CARDS__", cards)
            .replace("__LEGEND__", legend).replace("__JS__", JS))
    import os
    os.makedirs("public/policies", exist_ok=True)
    open("public/policies/index.html", "w", encoding="utf-8").write(page)
    print("wrote public/policies/index.html (%d bytes, %d policies)" % (len(page), len(POLICIES)))


if __name__ == "__main__":
    build()
