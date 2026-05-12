#!/usr/bin/env python3
"""
Fetch 5-year age × sex population structure for every country from the
World Bank API (which mirrors UN WPP 2024) across a set of decadal
historical years and compact into a single JSON file.

Output: public/age_pyramid.json
Shape:  {
  "USA": {
    "1965": { "popM": [17 ints], "popF": [17 ints], "totalM": N, "totalF": N },
    "1975": { ... },
    ...
    "2023": { ... }
  },
  ...
}
Bands: 0-4, 5-9, 10-14, ..., 70-74, 75-79, 80+
Years fetched: see YEARS below.
"""
import json, sys, time
from pathlib import Path
import urllib.request

BANDS = [
    "0004", "0509", "1014", "1519", "2024", "2529", "3034",
    "3539", "4044", "4549", "5054", "5559", "6064", "6569",
    "7074", "7579", "80UP",
]
SEXES = ["MA", "FE"]
# Decadal coverage 1965 → present, plus the most recent year (2023 — the
# latest WB-published value). Inflates the JSON ~7× but keeps the inline
# bundle under ~600 KB.
YEARS = [1965, 1975, 1985, 1995, 2005, 2015, 2023]

DEST = Path(__file__).parent / "public" / "age_pyramid.json"


def fetch_indicator_all_years(ind, year_min, year_max):
    """Fetch one indicator for all countries × year range. Returns {year: {iso: val}}."""
    url = (f"https://api.worldbank.org/v2/country/all/indicator/{ind}"
           f"?format=json&date={year_min}:{year_max}&per_page=20000")
    req = urllib.request.Request(url, headers={"User-Agent": "demoria-research/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        data = json.load(resp)
    if not isinstance(data, list) or len(data) < 2:
        raise RuntimeError(f"bad shape from {ind}")
    out = {}
    for row in data[1] or []:
        iso = row.get("countryiso3code")
        yr  = int(row.get("date", 0))
        v   = row.get("value")
        if iso and v is not None and yr in YEARS:
            out.setdefault(yr, {})[iso] = v
    return out


def main():
    y_min, y_max = min(YEARS), max(YEARS)
    print(f"Fetching {len(BANDS)*len(SEXES) + 2} indicators × years {YEARS}...")
    # pct[sex][band][year] -> {iso: pct}
    pct = {}
    for sex in SEXES:
        pct[sex] = {}
        for b in BANDS:
            ind = f"SP.POP.{b}.{sex}.5Y"
            try:
                pct[sex][b] = fetch_indicator_all_years(ind, y_min, y_max)
                tot = sum(len(v) for v in pct[sex][b].values())
                print(f"  {ind}: {tot} (country,year) pairs across {len(pct[sex][b])} years")
            except Exception as e:
                print(f"  {ind}: ERROR {e}", file=sys.stderr)
                pct[sex][b] = {}
            time.sleep(0.20)

    print("Fetching total male/female populations across years...")
    totalM = fetch_indicator_all_years("SP.POP.TOTL.MA.IN", y_min, y_max)
    totalF = fetch_indicator_all_years("SP.POP.TOTL.FE.IN", y_min, y_max)
    print(f"  totalM years: {sorted(totalM.keys())}, totalF years: {sorted(totalF.keys())}")

    # Build output: ISO -> { year -> {popM, popF, totalM, totalF} }
    out = {}
    all_isos = set()
    for yr in YEARS:
        all_isos.update(totalM.get(yr, {}).keys())
        all_isos.update(totalF.get(yr, {}).keys())
    for iso in sorted(all_isos):
        per_year = {}
        for yr in YEARS:
            tm = totalM.get(yr, {}).get(iso)
            tf = totalF.get(yr, {}).get(iso)
            if tm is None or tf is None:
                continue
            popM = []; popF = []
            complete = True
            for b in BANDS:
                pm = pct["MA"][b].get(yr, {}).get(iso)
                pf = pct["FE"][b].get(yr, {}).get(iso)
                if pm is None or pf is None:
                    complete = False; break
                popM.append(round(tm * pm / 100.0))
                popF.append(round(tf * pf / 100.0))
            if complete:
                per_year[str(yr)] = {
                    "popM": popM, "popF": popF,
                    "totalM": round(tm), "totalF": round(tf),
                }
        if per_year:
            out[iso] = per_year

    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(out, separators=(",", ":")))
    print(f"Wrote {len(out)} countries × {len(YEARS)} years → {DEST} ({DEST.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
