"""
Build women-of-childbearing-age (female 15-49) annual series from the UN WPP
2024 source CSV — the same PopulationByAge5GroupSex file the age pyramid is
built from, but read at FULL annual resolution (not 5-year snapshots).

For every country and every year 1965-2100 we record:
  wcba   = female population aged 15-49, total            (thousands of people)
  total  = total population (both sexes, all ages)        (thousands of people)
  pct    = wcba / total * 100                             (% of population)

Female 15-49 = the seven 5-year bands 15-19 … 45-49.

Output: _wcba.json  ->  {iso: {"y":[...], "wcba":[...], "pct":[...]}}
(values rounded: wcba to 1 decimal-thousand, pct to 3 dp.)
"""
import csv, gzip, json
from pathlib import Path
import urllib.request

WPP_URL = ("https://population.un.org/wpp/assets/Excel%20Files/"
           "1_Indicator%20(Standard)/CSV_FILES/"
           "WPP2024_PopulationByAge5GroupSex_Medium.csv.gz")
LOCAL_GZ = Path("/tmp/wpp_age5.csv.gz")
DEST = Path(__file__).parent / "_wcba.json"

YEARS = set(range(1965, 2101))            # full annual span
CBA_BANDS = {"15-19", "20-24", "25-29", "30-34", "35-39", "40-44", "45-49"}
ALL_BANDS = {
    "0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39",
    "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79",
    "80-84", "85-89", "90-94", "95-99", "100+",
}


def ensure_csv():
    if not LOCAL_GZ.exists() or LOCAL_GZ.stat().st_size < 10_000_000:
        print(f"Downloading WPP CSV ({WPP_URL}) ...")
        urllib.request.urlretrieve(WPP_URL, LOCAL_GZ)
    print(f"Local CSV: {LOCAL_GZ} ({LOCAL_GZ.stat().st_size // (1024*1024)} MB gz)")


def main():
    ensure_csv()
    # {iso: {year: [wcba_k, total_k]}}
    acc = {}
    rows = 0
    with gzip.open(LOCAL_GZ, "rt", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows += 1
            iso = (row.get("ISO3_code") or "").strip()
            if len(iso) != 3:
                continue
            try:
                yr = int(row.get("Time", 0))
            except ValueError:
                continue
            if yr not in YEARS:
                continue
            band = (row.get("AgeGrp") or "").strip()
            if band not in ALL_BANDS:
                continue
            try:
                pm = float(row.get("PopMale", "") or 0)
                pf = float(row.get("PopFemale", "") or 0)
            except ValueError:
                continue
            d = acc.setdefault(iso, {}).setdefault(yr, [0.0, 0.0])
            d[1] += pm + pf                       # total (both sexes)
            if band in CBA_BANDS:
                d[0] += pf                         # female 15-49
            if rows % 1_000_000 == 0:
                print(f"  ...{rows:,} rows")
    print(f"Parsed {rows:,} rows, {len(acc)} countries")

    out = {}
    for iso in sorted(acc):
        ys = sorted(acc[iso])
        wcba = []; pct = []
        for y in ys:
            w, tot = acc[iso][y]
            wcba.append(round(w, 1))
            pct.append(round(w / tot * 100, 3) if tot else None)
        out[iso] = {"y": ys, "wcba": wcba, "pct": pct}

    DEST.write_text(json.dumps(out, separators=(",", ":")))
    print(f"Wrote {len(out)} countries -> {DEST} ({DEST.stat().st_size//1024} KB)")
    # quick sanity
    for iso in ("USA", "JPN", "NGA"):
        e = out.get(iso)
        if not e:
            continue
        i = e["y"].index(2024)
        print(f"  {iso} 2024: female15-49 = {e['wcba'][i]:,.0f}k  ({e['pct'][i]}% of pop)")


if __name__ == "__main__":
    main()
