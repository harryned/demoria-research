"""
Demoria Research — grounded data layer.

The single source of truth that the AI tools query. Every number an "Ask Demoria"
answer contains must come from one of these functions, with its provenance
(NSO / DRE / WPP). The model never invents a figure; it calls these.

Loads:
  _data_export.json        annual per-country indicators 1965-2025 (+ provenance)
  public/cliffs_data.json  the cohort "cliff" metrics
  _build_policies_page.py  the pronatal policy library (imported for one source of truth)
"""
from __future__ import annotations
import json
import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

DATA = json.loads((ROOT / "_data_export.json").read_text())
CLIFFS = json.loads((ROOT / "public" / "cliffs_data.json").read_text())

# import POLICIES from the page generator so the library has one definition
_spec = importlib.util.spec_from_file_location("_pol", ROOT / "_build_policies_page.py")
_pol = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_pol)
POLICIES = _pol.POLICIES  # tuples: (country, year, policy, mechs, cost, effect, evidence, verdict, blurb, source)

# ---- indicator catalogue (key -> label, unit) ----
INDICATORS = {
    "pop":      ("Total population", "thousands"),
    "tfr":      ("Total fertility rate", "children/woman"),
    "nrr":      ("Net reproduction rate", "daughters/woman"),
    "births":   ("Live births", "thousands"),
    "deaths":   ("Deaths", "thousands"),
    "cbr":      ("Crude birth rate", "per 1,000"),
    "cdr":      ("Crude death rate", "per 1,000"),
    "natch5":   ("5-year natural change", "%"),
    "medage":   ("Median age", "years"),
    "workage":  ("Working-age population (15-64)", "thousands"),
    "pop_u20":  ("Population under 20", "people"),
    "oadr":     ("Old-age dependency ratio", "%"),
    "wrr":      ("Worker replacement ratio", "%"),
    "lfpr":     ("Labour-force participation", "%"),
    "netmig":   ("Net migration", "people"),
    "migstk":   ("Migrant stock", "%"),
    "wcba":     ("Women 15-49 (childbearing age)", "thousands"),
    "wcba_pct": ("Women 15-49, % of population", "%"),
    "dhi":      ("DHI composite score", "0-100"),
    "p_fss":    ("Pillar - Fertility Strength", "0-100"),
    "p_pms":    ("Pillar - Population Momentum", "0-100"),
    "p_wss":    ("Pillar - Workforce Sustainability", "0-100"),
    "p_mrs":    ("Pillar - Migration Reliance", "0-100"),
}

CLIFF_LABELS = {
    "baby": "Annual births (the vanishing cradle)",
    "kindergarten": "5-year-olds (the empty classroom)",
    "higher_ed": "18-year-olds (the enrollment cliff)",
    "manpower": "Ages 18-25 (the thin ranks)",
    "first_home": "Ages 28-35 (the first-home drought)",
    "peak_workers": "Working-age 15-64 (peak labour)",
    "silver": "Population 80+ (the silver tsunami)",
}

# ---- name resolution ----
_ALIASES = {
    "usa": "USA", "us": "USA", "united states": "USA", "america": "USA",
    "uk": "GBR", "britain": "GBR", "united kingdom": "GBR", "england": "GBR",
    "korea": "KOR", "south korea": "KOR", "s korea": "KOR",
    "north korea": "PRK",
    "russia": "RUS", "china": "CHN", "japan": "JPN", "germany": "DEU",
    "iran": "IRN", "vietnam": "VNM", "uae": "ARE", "ivory coast": "CIV",
    "czechia": "CZE", "czech republic": "CZE", "moldova": "MDA", "taiwan": "TWN",
    "turkey": "TUR", "turkiye": "TUR", "egypt": "EGY", "syria": "SYR",
}
_NAME2ISO = {}
for _iso, _c in DATA.items():
    _NAME2ISO[_c["name"].lower()] = _iso
    _NAME2ISO[_iso.lower()] = _iso


def resolve_country(q: str) -> str | None:
    """Fuzzy country name / ISO3 -> ISO3 code, or None."""
    if not q:
        return None
    s = q.strip().lower()
    if s.upper() in DATA:
        return s.upper()
    if s in _ALIASES:
        return _ALIASES[s]
    if s in _NAME2ISO:
        return _NAME2ISO[s]
    # substring match on full names
    hits = [iso for name, iso in _NAME2ISO.items() if s in name]
    return hits[0] if len(hits) == 1 else (hits[0] if hits else None)


def country_name(iso: str) -> str:
    c = DATA.get(iso)
    return c["name"] if c else iso


def _source(c: dict, key: str, year: int) -> str:
    dre = set((c.get("dre_yrs") or {}).get(key, []))
    nso = set((c.get("nso_yrs") or {}).get(key, []))
    if year in dre:
        return "DRE"
    if year in nso:
        return "NSO"
    return "WPP"


def get_value(iso: str, indicator: str, year: int) -> dict | None:
    c = DATA.get(iso)
    if not c or indicator not in c["ind"] or year not in c["yrs"]:
        return None
    v = c["ind"][indicator][c["yrs"].index(year)]
    if v is None:
        return None
    return {"iso": iso, "country": c["name"], "indicator": indicator,
            "label": INDICATORS.get(indicator, (indicator, ""))[0],
            "unit": INDICATORS.get(indicator, (indicator, ""))[1],
            "year": year, "value": v, "source": _source(c, indicator, year)}


def get_series(iso: str, indicator: str, year_from: int = 1965, year_to: int = 2025) -> dict | None:
    c = DATA.get(iso)
    if not c or indicator not in c["ind"]:
        return None
    out = []
    for i, y in enumerate(c["yrs"]):
        if year_from <= y <= year_to:
            v = c["ind"][indicator][i]
            if v is not None:
                out.append({"year": y, "value": v, "source": _source(c, indicator, y)})
    return {"iso": iso, "country": c["name"], "indicator": indicator,
            "label": INDICATORS.get(indicator, (indicator, ""))[0],
            "unit": INDICATORS.get(indicator, (indicator, ""))[1], "series": out}


def rank(indicator: str, year: int = 2025, order: str = "desc", n: int = 10,
         sovereign_only: bool = True) -> list[dict]:
    rows = []
    for iso, c in DATA.items():
        if sovereign_only and not c.get("sov", True):
            continue
        if indicator in c["ind"] and year in c["yrs"]:
            v = c["ind"][indicator][c["yrs"].index(year)]
            if v is not None:
                rows.append({"iso": iso, "country": c["name"], "value": v,
                             "source": _source(c, indicator, year)})
    rows.sort(key=lambda r: r["value"], reverse=(order == "desc"))
    return rows[:n]


def compare(isos: list[str], indicator: str, years: list[int]) -> dict:
    out = {}
    for iso in isos:
        out[iso] = {"country": country_name(iso),
                    "values": {y: (get_value(iso, indicator, y) or {}).get("value") for y in years}}
    return {"indicator": indicator,
            "label": INDICATORS.get(indicator, (indicator, ""))[0],
            "unit": INDICATORS.get(indicator, (indicator, ""))[1], "countries": out}


def get_cliff(iso: str, cliff_key: str) -> dict | None:
    e = CLIFFS.get(iso)
    if not e or cliff_key not in e["cliffs"]:
        return None
    m = dict(e["cliffs"][cliff_key])
    m.pop("series", None)  # drop the dense series; keep the headline metrics
    return {"iso": iso, "country": e["name"], "cliff": cliff_key,
            "label": CLIFF_LABELS.get(cliff_key, cliff_key), **m}


def list_cliffs(iso: str) -> dict | None:
    e = CLIFFS.get(iso)
    if not e:
        return None
    return {"iso": iso, "country": e["name"],
            "cliffs": {k: get_cliff(iso, k) for k in e["cliffs"]}}


def search_policies(mechanism: str | None = None, verdict: str | None = None,
                    country: str | None = None) -> list[dict]:
    out = []
    for (c, yr, pol, mechs, cost, effect, ev, verd, blurb, src) in POLICIES:
        if mechanism and mechanism.lower() not in [m.lower() for m in mechs]:
            continue
        if verdict and verdict.lower() != verd.lower():
            continue
        if country and country.lower() not in c.lower():
            continue
        out.append({"country": c, "year": yr, "policy": pol, "mechanisms": mechs,
                    "cost": cost, "effect": effect, "evidence": ev, "verdict": verd,
                    "summary": blurb, "source": src})
    return out


if __name__ == "__main__":
    # self-test
    print("countries:", len(DATA), "| cliffs:", len(CLIFFS), "| policies:", len(POLICIES))
    print("resolve 'south korea' ->", resolve_country("south korea"))
    print("USA TFR 2024:", get_value("USA", "tfr", 2024))
    print("UKR wcba 2024:", get_value("UKR", "wcba", 2024))
    print("lowest TFR 2025 (top 3):", [(r["country"], r["value"]) for r in rank("tfr", 2025, "asc", 3)])
    print("Japan baby cliff:", get_cliff("JPN", "baby"))
    print("Korea policies:", [(p["country"], p["verdict"]) for p in search_policies(country="korea")])
