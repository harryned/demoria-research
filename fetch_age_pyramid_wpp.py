"""
Build the age-pyramid dataset from UN WPP 2024 CSV directly.

Why not the World Bank API? WB only publishes WPP-derived 5-year band data
through 2024; for projections (2025–2100) we need the WPP source CSV.
Going to WPP for everything also gives a single canonical dataset.

Years: every 5 years 1965 → 2100 (28 snapshots) — smooth enough for a
slider, small enough not to bloat the bundle. WPP's age groups go up to
"100+", which we collapse into "80+" to match the existing 17-band layout
(0-4, 5-9, ..., 70-74, 75-79, 80+).

Output: public/age_pyramid.json (column-oriented compact format, headcounts
in thousands so each number is 5-7 chars).
"""
import csv, gzip, json, sys, time
from pathlib import Path
import urllib.request

WPP_URL = ("https://population.un.org/wpp/assets/Excel%20Files/"
           "1_Indicator%20(Standard)/CSV_FILES/"
           "WPP2024_PopulationByAge5GroupSex_Medium.csv.gz")
LOCAL_GZ = Path("/tmp/wpp_age5.csv.gz")
DEST     = Path(__file__).parent / "public" / "age_pyramid.json"

YEARS = list(range(1965, 2101, 5))  # 1965, 1970, ..., 2100 = 28 years

# Display bands (must match the dashboard's PYRAMID_BANDS order: 0-4 first → 100+ last)
# Now keeps every 5-year band WPP publishes — including the very-elderly bands
# 80-84, 85-89, 90-94, 95-99 and 100+ that are essential for visualising the
# top of an ageing-population pyramid.
DISPLAY_BANDS = [
    "0-4", "5-9", "10-14", "15-19", "20-24", "25-29", "30-34", "35-39",
    "40-44", "45-49", "50-54", "55-59", "60-64", "65-69", "70-74", "75-79",
    "80-84", "85-89", "90-94", "95-99", "100+",
]


def ensure_csv():
    if not LOCAL_GZ.exists() or LOCAL_GZ.stat().st_size < 10_000_000:
        print(f"Downloading WPP CSV ({WPP_URL})...")
        urllib.request.urlretrieve(WPP_URL, LOCAL_GZ)
    print(f"Local CSV: {LOCAL_GZ} ({LOCAL_GZ.stat().st_size // (1024*1024)} MB gz)")


def main():
    ensure_csv()
    # Per-country, per-year accumulation: {iso: {year: {band: (m, f)}}}
    by_iso = {}
    rows_processed = 0
    rows_kept = 0
    target_years = set(YEARS)
    print(f"Processing... target years: {sorted(target_years)}")
    with gzip.open(LOCAL_GZ, "rt", encoding="utf-8-sig") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            rows_processed += 1
            iso = row.get("ISO3_code", "").strip()
            if not iso or len(iso) != 3:
                continue
            try:
                yr = int(row.get("Time", 0))
            except ValueError:
                continue
            if yr not in target_years:
                continue
            disp = row.get("AgeGrp", "").strip()
            if not disp or disp not in DISPLAY_BANDS:
                continue
            try:
                pm = float(row.get("PopMale", "") or 0)
                pf = float(row.get("PopFemale", "") or 0)
            except ValueError:
                continue
            d = by_iso.setdefault(iso, {}).setdefault(yr, {})
            prev = d.get(disp, (0.0, 0.0))
            d[disp] = (prev[0] + pm, prev[1] + pf)
            rows_kept += 1
            if rows_processed % 500_000 == 0:
                print(f"  ...processed {rows_processed:,} rows, kept {rows_kept:,}")
    print(f"Done parsing. Total rows processed: {rows_processed:,}, kept: {rows_kept:,}")
    print(f"Countries with data: {len(by_iso)}")

    # Build column-oriented compact output.
    # Precision: full integers for countries large enough that 1k-resolution
    # is fine (≥1M total pop ≈ ≥50k per band on average), but 1-decimal for
    # smaller countries. At 0.1k resolution a Tuvalu-sized band of 480 people
    # rounds to 0.5 instead of 0 (or 1), so the bar widths actually differ
    # across bands instead of all collapsing to "1×1k = same bar".
    def make_K(total_pop_k):
        if total_pop_k >= 1_000:  # ≥1M total
            return lambda n: int(round(n))
        else:
            return lambda n: round(n, 1)
    out = {}
    for iso in sorted(by_iso):
        years_present = sorted(by_iso[iso].keys())
        # Decide precision based on the country's MAXIMUM total population
        # across the observed/projected window — so the precision is stable
        # across the year slider (no flicker between integer and decimal as
        # the slider moves).
        max_total_k = 0.0
        for yr in years_present:
            bands_d = by_iso[iso][yr]
            yr_total = sum((pair[0] + pair[1]) for pair in bands_d.values())
            if yr_total > max_total_k: max_total_k = yr_total
        K = make_K(max_total_k)
        ys = []; m = []; f = []; tm_arr = []; tf_arr = []
        for yr in years_present:
            bands_d = by_iso[iso][yr]
            popM = []; popF = []
            complete = True
            for disp in DISPLAY_BANDS:
                pair = bands_d.get(disp)
                if pair is None:
                    complete = False; break
                popM.append(K(pair[0]))
                popF.append(K(pair[1]))
            if complete:
                ys.append(yr)
                m.append(popM)
                f.append(popF)
                tm_arr.append(round(sum(popM), 1))
                tf_arr.append(round(sum(popF), 1))
        if ys:
            out[iso] = {"y": ys, "m": m, "f": f, "tm": tm_arr, "tf": tf_arr}

    DEST.parent.mkdir(parents=True, exist_ok=True)
    DEST.write_text(json.dumps(out, separators=(",", ":")))
    sz_kb = DEST.stat().st_size // 1024
    print(f"Wrote {len(out)} countries × up to {len(YEARS)} years → {DEST} ({sz_kb} KB)")


if __name__ == "__main__":
    main()
