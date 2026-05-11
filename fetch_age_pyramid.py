#!/usr/bin/env python3
"""
Fetch 5-year age × sex population structure for every country from the
World Bank API (which mirrors UN WPP 2024) and compact it into a single
JSON file the dashboard can load directly.

Output: public/age_pyramid_2023.json
Shape:  {
  "USA": {
    "year": 2023,
    "popM": [<absolute male population in each 5-yr band, 17 bands>],
    "popF": [<absolute female population in each 5-yr band, 17 bands>],
    "totalM": <total male pop>,
    "totalF": <total female pop>
  },
  ...
}
Bands: 0-4, 5-9, 10-14, ..., 70-74, 75-79, 80+
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
YEAR = 2023

DEST = Path(__file__).parent / "public" / "age_pyramid_2023.json"


def fetch_indicator(ind):
    """Fetch one indicator for all countries for YEAR. Returns dict {iso3: value}."""
    url = (f"https://api.worldbank.org/v2/country/all/indicator/{ind}"
           f"?format=json&date={YEAR}&per_page=400")
    req = urllib.request.Request(url, headers={"User-Agent": "demoria-research/1.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        data = json.load(resp)
    if not isinstance(data, list) or len(data) < 2:
        raise RuntimeError(f"bad shape from {ind}")
    out = {}
    for row in data[1] or []:
        iso = row.get("countryiso3code")
        v = row.get("value")
        if iso and v is not None:
            out[iso] = v
    return out


def main():
    print(f"Fetching {len(BANDS)*len(SEXES) + 2} indicators for {YEAR}...")
    pct = {}   # pct[sex][band] -> {iso: percentage}
    for sex in SEXES:
        pct[sex] = {}
        for b in BANDS:
            ind = f"SP.POP.{b}.{sex}.5Y"
            try:
                pct[sex][b] = fetch_indicator(ind)
                print(f"  {ind}: {len(pct[sex][b])} countries")
            except Exception as e:
                print(f"  {ind}: ERROR {e}", file=sys.stderr)
                pct[sex][b] = {}
            time.sleep(0.15)

    # Total male/female pop in absolute counts
    print("Fetching total male/female populations...")
    totalM = fetch_indicator("SP.POP.TOTL.MA.IN")
    totalF = fetch_indicator("SP.POP.TOTL.FE.IN")
    print(f"  totalM: {len(totalM)} totalF: {len(totalF)}")

    # Build output: ISO -> { popM[], popF[], totalM, totalF }
    out = {}
    isos = set(totalM.keys()) | set(totalF.keys())
    for iso in sorted(isos):
        tm = totalM.get(iso); tf = totalF.get(iso)
        if tm is None or tf is None:
            continue
        popM = []
        popF = []
        complete = True
        for b in BANDS:
            pm = pct["MA"][b].get(iso)
            pf = pct["FE"][b].get(iso)
            if pm is None or pf is None:
                complete = False; break
            popM.append(round(tm * pm / 100.0))
            popF.append(round(tf * pf / 100.0))
        if complete:
            out[iso] = {
                "year": YEAR,
                "popM": popM,
                "popF": popF,
                "totalM": round(tm),
                "totalF": round(tf),
            }

    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(out, separators=(",", ":")))
    print(f"Wrote {len(out)} countries → {DEST} ({DEST.stat().st_size // 1024} KB)")


if __name__ == "__main__":
    main()
