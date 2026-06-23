// Ask Demoria — Cloudflare Worker.
// A grounded Q&A endpoint: the model answers in prose, but every figure comes
// from a tool call against the bundled dataset, stamped with its source tier
// (NSO / DRE / WPP). It never invents a number.
//
// Deploy: set the ANTHROPIC_API_KEY secret (wrangler secret put ANTHROPIC_API_KEY),
// then `wrangler deploy`. Locally: `wrangler dev` and open http://localhost:8787.

import DATA from "../data.json";

const MODEL = "claude-opus-4-8";
const ANTHROPIC_URL = "https://api.anthropic.com/v1/messages";

const INDICATORS = {
  tfr: ["Total fertility rate", "children/woman"], pop: ["Total population", "thousands"],
  births: ["Live births", "thousands"], wcba: ["Women 15-49 (childbearing age)", "thousands"],
  wcba_pct: ["Women 15-49, % of population", "%"], dhi: ["DHI composite score", "0-100"],
  medage: ["Median age", "years"], oadr: ["Old-age dependency ratio", "%"],
  netmig: ["Net migration", "people"], workage: ["Working-age population (15-64)", "thousands"],
  pop_u20: ["Population under 20", "people"], cbr: ["Crude birth rate", "per 1,000"],
  cdr: ["Crude death rate", "per 1,000"], nrr: ["Net reproduction rate", "daughters/woman"],
  migstk: ["Migrant stock", "%"], p_fss: ["Pillar - Fertility Strength", "0-100"],
  p_pms: ["Pillar - Population Momentum", "0-100"], p_wss: ["Pillar - Workforce Sustainability", "0-100"],
  p_mrs: ["Pillar - Migration Reliance", "0-100"],
};
const CLIFF_LABELS = {
  baby: "Annual births (the vanishing cradle)", kindergarten: "5-year-olds (the empty classroom)",
  higher_ed: "18-year-olds (the enrollment cliff)", manpower: "Ages 18-25 (the thin ranks)",
  first_home: "Ages 28-35 (the first-home drought)", peak_workers: "Working-age 15-64 (peak labour)",
  silver: "Population 80+ (the silver tsunami)",
};
const ALIASES = {
  usa: "USA", us: "USA", "united states": "USA", america: "USA", uk: "GBR", britain: "GBR",
  "united kingdom": "GBR", england: "GBR", korea: "KOR", "south korea": "KOR", russia: "RUS",
  china: "CHN", japan: "JPN", germany: "DEU", iran: "IRN", taiwan: "TWN", czechia: "CZE",
  "czech republic": "CZE", moldova: "MDA", turkey: "TUR", turkiye: "TUR",
};
const NAME2ISO = {};
for (const [iso, c] of Object.entries(DATA.countries)) {
  NAME2ISO[c.name.toLowerCase()] = iso; NAME2ISO[iso.toLowerCase()] = iso;
}

// ---------- grounded data layer ----------
function resolveCountry(q) {
  if (!q) return null;
  const s = q.trim().toLowerCase();
  if (DATA.countries[s.toUpperCase()]) return s.toUpperCase();
  if (ALIASES[s]) return ALIASES[s];
  if (NAME2ISO[s]) return NAME2ISO[s];
  const hits = Object.entries(NAME2ISO).filter(([n]) => n.includes(s)).map(([, i]) => i);
  return hits.length ? hits[0] : null;
}
const name = (iso) => (DATA.countries[iso] ? DATA.countries[iso].name : iso);
function source(c, k, y) {
  if ((c.dre[k] || []).includes(y)) return "DRE";
  if ((c.nso[k] || []).includes(y)) return "NSO";
  return "WPP";
}
function getValue(iso, ind, year) {
  const c = DATA.countries[iso];
  if (!c || !c.ind[ind]) return null;
  const i = c.yrs.indexOf(year);
  if (i < 0 || c.ind[ind][i] == null) return null;
  return { iso, country: c.name, indicator: ind, label: (INDICATORS[ind] || [ind, ""])[0],
    unit: (INDICATORS[ind] || [ind, ""])[1], year, value: c.ind[ind][i], source: source(c, ind, year) };
}
function getSeries(iso, ind, from = 1965, to = 2025) {
  const c = DATA.countries[iso];
  if (!c || !c.ind[ind]) return null;
  const series = [];
  c.yrs.forEach((y, i) => {
    if (y >= from && y <= to && c.ind[ind][i] != null)
      series.push({ year: y, value: c.ind[ind][i], source: source(c, ind, y) });
  });
  return { iso, country: c.name, indicator: ind, label: (INDICATORS[ind] || [ind, ""])[0], series };
}
function rank(ind, year = 2025, order = "desc", n = 10, sovOnly = true) {
  const rows = [];
  for (const [iso, c] of Object.entries(DATA.countries)) {
    if (sovOnly && c.sov === false) continue;
    const i = c.yrs.indexOf(year);
    if (c.ind[ind] && i >= 0 && c.ind[ind][i] != null)
      rows.push({ iso, country: c.name, value: c.ind[ind][i], source: source(c, ind, year) });
  }
  rows.sort((a, b) => (order === "desc" ? b.value - a.value : a.value - b.value));
  return rows.slice(0, Math.max(1, Math.min(n, 50)));
}
function compare(isos, ind, years) {
  const out = {};
  for (const iso of isos) {
    out[iso] = { country: name(iso), values: {} };
    for (const y of years) out[iso].values[y] = (getValue(iso, ind, y) || {}).value ?? null;
  }
  return { indicator: ind, label: (INDICATORS[ind] || [ind, ""])[0], countries: out };
}
function getCliff(iso, key) {
  const e = DATA.cliffs[iso];
  if (!e || !e.cliffs[key]) return null;
  return { iso, country: e.name, cliff: key, label: CLIFF_LABELS[key] || key, ...e.cliffs[key] };
}
function searchPolicies(mech, verd, country) {
  const wantIso = country ? resolveCountry(country) : null;
  const out = [];
  for (const p of DATA.policies) {
    const [c, yr, pol, mechs, cost, effect, ev, verdict, blurb, src] = p;
    if (mech && !mechs.map((m) => m.toLowerCase()).includes(mech.toLowerCase())) continue;
    if (verd && verd.toLowerCase() !== verdict.toLowerCase()) continue;
    if (country && !((wantIso && resolveCountry(c) === wantIso) || c.toLowerCase().includes(country.toLowerCase()))) continue;
    out.push({ country: c, year: yr, policy: pol, mechanisms: mechs, cost, effect, evidence: ev, verdict, summary: blurb, source: src });
  }
  return out;
}

// ---------- tool registry ----------
const TOOLS = [
  { name: "resolve_country", description: "Resolve a country name/alias/ISO3 to its ISO3 code and official name.",
    input_schema: { type: "object", properties: { name: { type: "string" } }, required: ["name"] } },
  { name: "get_indicator_value", description: "One indicator value for one country in one year, with source (NSO/DRE/WPP).",
    input_schema: { type: "object", properties: { country: { type: "string" }, indicator: { type: "string" }, year: { type: "integer" } }, required: ["country", "indicator", "year"] } },
  { name: "get_indicator_series", description: "Time series of one indicator for one country across a year range (1965-2025).",
    input_schema: { type: "object", properties: { country: { type: "string" }, indicator: { type: "string" }, year_from: { type: "integer" }, year_to: { type: "integer" } }, required: ["country", "indicator"] } },
  { name: "rank_countries", description: "Rank countries by an indicator in a year. order='asc' for lowest, 'desc' for highest.",
    input_schema: { type: "object", properties: { indicator: { type: "string" }, year: { type: "integer" }, order: { type: "string" }, n: { type: "integer" } }, required: ["indicator"] } },
  { name: "compare_countries", description: "Compare countries on one indicator across years. countries and years are comma-separated.",
    input_schema: { type: "object", properties: { countries: { type: "string" }, indicator: { type: "string" }, years: { type: "string" } }, required: ["countries", "indicator", "years"] } },
  { name: "get_cohort_cliff", description: "A demographic cliff metric (peak year, current value, % change). cliff in: baby, kindergarten, higher_ed, manpower, first_home, peak_workers, silver.",
    input_schema: { type: "object", properties: { country: { type: "string" }, cliff: { type: "string" } }, required: ["country", "cliff"] } },
  { name: "search_pronatal_policies", description: "Search the pronatal policy library by mechanism, verdict and/or country (any blank).",
    input_schema: { type: "object", properties: { mechanism: { type: "string" }, verdict: { type: "string" }, country: { type: "string" } } } },
];

function runTool(nm, a) {
  try {
    if (nm === "resolve_country") { const iso = resolveCountry(a.name); return iso ? { iso, name: name(iso) } : { error: `No country matched '${a.name}'.` }; }
    if (nm === "get_indicator_value") { const iso = resolveCountry(a.country); return iso ? (getValue(iso, a.indicator, a.year) || { error: "No value." }) : { error: "Unknown country." }; }
    if (nm === "get_indicator_series") { const iso = resolveCountry(a.country); return iso ? (getSeries(iso, a.indicator, a.year_from || 1965, a.year_to || 2025) || { error: "No series." }) : { error: "Unknown country." }; }
    if (nm === "rank_countries") return rank(a.indicator, a.year || 2025, a.order || "desc", a.n || 10);
    if (nm === "compare_countries") { const isos = a.countries.split(",").map((x) => resolveCountry(x.trim())).filter(Boolean); const yrs = a.years.split(",").map((y) => parseInt(y.trim())).filter((y) => !isNaN(y)); return compare(isos, a.indicator, yrs); }
    if (nm === "get_cohort_cliff") { const iso = resolveCountry(a.country); return iso ? (getCliff(iso, a.cliff) || { error: "No such cliff." }) : { error: "Unknown country." }; }
    if (nm === "search_pronatal_policies") return searchPolicies(a.mechanism || null, a.verdict || null, a.country || null);
    return { error: "Unknown tool." };
  } catch (e) { return { error: String(e) }; }
}

const SYSTEM = `You are Ask Demoria, the question-answering layer of Demoria Research (demoriaresearch.com), a demographic-intelligence firm.
Voice: British English, plain and precise, a touch of dry personality. No em dashes. Avoid the "not X but Y" cadence. Keep answers tight.
Hard rules:
- Every figure you state MUST come from a tool call. Never recall or estimate a number yourself.
- When you give a figure, name its source tier in brackets: (NSO) national statistics, (DRE) a Demoria Research Estimation, or (WPP) the UN baseline.
- Data covers 236 countries and territories, annual 1965 to 2025. If asked for something outside that, say so plainly.
- Resolve country names with the tools before querying. Be honest about limits.
Indicator keys: ${Object.entries(INDICATORS).map(([k, v]) => `${k} (${v[0]})`).join(", ")}.
Cliff keys: ${Object.keys(CLIFF_LABELS).join(", ")}.`;

async function ask(question, apiKey) {
  let messages = [{ role: "user", content: question }];
  for (let step = 0; step < 8; step++) {
    const r = await fetch(ANTHROPIC_URL, {
      method: "POST",
      headers: { "x-api-key": apiKey, "anthropic-version": "2023-06-01", "content-type": "application/json" },
      body: JSON.stringify({ model: MODEL, max_tokens: 4000, thinking: { type: "adaptive" }, system: SYSTEM, tools: TOOLS, messages }),
    });
    if (!r.ok) return { error: `Anthropic ${r.status}: ${(await r.text()).slice(0, 300)}` };
    const resp = await r.json();
    if (resp.stop_reason !== "tool_use") {
      const text = (resp.content || []).filter((b) => b.type === "text").map((b) => b.text).join("\n").trim();
      return { answer: text };
    }
    messages.push({ role: "assistant", content: resp.content });
    const results = resp.content.filter((b) => b.type === "tool_use").map((b) => ({
      type: "tool_result", tool_use_id: b.id, content: JSON.stringify(runTool(b.name, b.input)),
    }));
    messages.push({ role: "user", content: results });
  }
  return { error: "Too many tool steps." };
}

const CORS = { "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "content-type" };

export default {
  async fetch(request, env) {
    if (request.method === "OPTIONS") return new Response(null, { headers: CORS });
    if (request.method === "GET") return new Response(DEMO_HTML, { headers: { "content-type": "text/html" } });
    if (request.method !== "POST") return new Response("Method not allowed", { status: 405 });
    if (!env.ANTHROPIC_API_KEY) return json({ error: "Server missing ANTHROPIC_API_KEY secret." }, 500);
    let body;
    try { body = await request.json(); } catch { return json({ error: "Bad JSON." }, 400); }
    const q = (body.question || "").toString().slice(0, 600);
    if (!q.trim()) return json({ error: "Ask a question." }, 400);
    const out = await ask(q, env.ANTHROPIC_API_KEY);
    return json(out, out.error ? 502 : 200);
  },
};
const json = (o, status = 200) => new Response(JSON.stringify(o), { status, headers: { "content-type": "application/json", ...CORS } });

const DEMO_HTML = `<!doctype html><meta charset=utf-8><meta name=viewport content="width=device-width,initial-scale=1">
<title>Ask Demoria</title><style>body{font-family:Manrope,system-ui,sans-serif;background:#0f2347;color:#eef1f6;max-width:680px;margin:8vh auto;padding:0 20px}
h1{font-weight:800}.eye{font-family:'JetBrains Mono',monospace;color:#e8b84b;letter-spacing:.2em;font-size:.7rem;text-transform:uppercase}
input{width:100%;padding:14px 16px;border-radius:10px;border:1px solid rgba(232,184,75,.4);background:#0b1730;color:#fff;font-size:1rem}
.a{margin-top:18px;line-height:1.6;white-space:pre-wrap;background:#fcf4dd;color:#0c1a33;border-radius:12px;padding:18px 20px;display:none}
small{color:rgba(238,241,246,.55)}</style>
<div class=eye>Demoria Research</div><h1>Ask Demoria</h1>
<p><small>Every figure is pulled from the dataset and stamped NSO / DRE / WPP. Try: "Which countries have the lowest fertility in 2025?"</small></p>
<input id=q placeholder="Ask about any country's demographics…" autofocus>
<div class=a id=a></div>
<script>const q=document.getElementById('q'),a=document.getElementById('a');
q.addEventListener('keydown',async e=>{if(e.key!=='Enter')return;const v=q.value.trim();if(!v)return;
a.style.display='block';a.textContent='Thinking…';
try{const r=await fetch(location.pathname,{method:'POST',headers:{'content-type':'application/json'},body:JSON.stringify({question:v})});
const d=await r.json();a.textContent=d.answer||('Error: '+(d.error||'unknown'));}catch(err){a.textContent='Error: '+err}});</script>`;
