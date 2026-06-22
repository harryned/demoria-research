"""
Inject the women-of-childbearing-age series (female 15-49) built by
_build_wcba.py into the live database, WITHOUT disturbing anything already
there (e.g. the Ukraine DRE overrides committed into the DATA blob).

Adds two parallel arrays to each country's `ind`, aligned to its `yrs`:
  wcba       female 15-49 total           (thousands of people)
  wcba_pct   female 15-49 / total pop * 100  (% of population)

Touches:
  _data_export.json            (the canonical downloadable database)
  dhi_globe.html               (DATA blob + Data-table GROUPS + explorer INDS)

Idempotent: re-running is a no-op once the keys are present.
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent
WCBA = json.load(open(ROOT / "_wcba.json"))


def add_series(d):
    """Add wcba_pct (WPP female-15-49 share) and wcba (= share × the country's
    authoritative `pop`, in thousands) to a country record `d` in place.
    Tying the count to `pop` keeps count/pop == pct everywhere, and makes the
    count reflect any population override (e.g. Ukraine's de-facto 30M)."""
    iso_e = WCBA.get(d.get("_iso"))
    yrs = d["yrs"]
    pop = d["ind"].get("pop") or [None] * len(yrs)
    idx = {y: i for i, y in enumerate(iso_e["y"])} if iso_e else {}
    pct_l, cnt_l = [], []
    for j, y in enumerate(yrs):
        i = idx.get(y)
        p = iso_e["pct"][i] if (iso_e and i is not None) else None
        pct_l.append(p)
        pv = pop[j] if j < len(pop) else None
        cnt_l.append(round(p / 100 * pv, 1) if (p is not None and pv is not None) else None)
    d["ind"]["wcba"] = cnt_l
    d["ind"]["wcba_pct"] = pct_l


def patch_export():
    fp = ROOT / "_data_export.json"
    data = json.load(open(fp))
    n = 0
    for iso, d in data.items():
        if "ind" not in d or "yrs" not in d:
            continue
        d["_iso"] = iso
        add_series(d)
        d.pop("_iso", None)
        n += 1
    json.dump(data, open(fp, "w"), separators=(",", ":"))
    print(f"_data_export.json: wcba added to {n} countries")


def patch_blob(h):
    a = h.find("const DATA=") + len("const DATA=")
    b = h.find(";const FCAGE=", a)
    blob = json.loads(h[a:b])
    n = 0
    for iso, d in blob.items():
        if not isinstance(d, dict) or "ind" not in d or "yrs" not in d:
            continue
        d["_iso"] = iso
        add_series(d)
        d.pop("_iso", None)
        n += 1
    print(f"DATA blob: wcba added to {n} countries")
    return h[:a] + json.dumps(blob, separators=(",", ":")) + h[b:]


def patch_projd(h):
    """Add wcba / wcba_pct projection arrays (2026-2100) to the PROJD blob so the
    explorer overlays the medium-variant projection like every other indicator."""
    a = h.find("const PROJD=") + len("const PROJD=")
    b = h.find(";const PYR=", a)
    projd = json.loads(h[a:b])
    PY = list(range(2026, 2101))                       # 75 projection years
    n = 0
    for iso, rec in projd.items():
        if not isinstance(rec, dict):
            continue
        e = WCBA.get(iso)
        pop = rec.get("pop")                            # projected pop, thousands
        if not e:
            rec["wcba"] = [None] * len(PY); rec["wcba_pct"] = [None] * len(PY); continue
        idx = {y: i for i, y in enumerate(e["y"])}
        pct, cnt = [], []
        for k, y in enumerate(PY):
            i = idx.get(y)
            p = e["pct"][i] if i is not None else None
            pct.append(p)
            pv = pop[k] if (pop and k < len(pop)) else None
            cnt.append(round(p / 100 * pv, 1) if (p is not None and pv is not None) else None)
        rec["wcba"] = cnt; rec["wcba_pct"] = pct
        n += 1
    print(f"PROJD: wcba projections added to {n} countries")
    return h[:a] + json.dumps(projd, separators=(",", ":")) + h[b:]


def patch_groups(h):
    if "['wcba'," in h:
        print("GROUPS: wcba already present, skipping")
        return h
    anchor = "      ['cbr',     'Crude birth rate',           '/1000',2],\n    ]},"
    assert h.count(anchor) == 1, f"GROUPS anchor count={h.count(anchor)}"
    add = ("      ['cbr',     'Crude birth rate',           '/1000',2],\n"
           "      ['wcba',    'Women 15–49 (childbearing age)','k', 1],\n"
           "      ['wcba_pct','Women 15–49, % of population','%',  2],\n    ]},")
    return h.replace(anchor, add)


def patch_inds(h):
    if "k:'wcba'" in h:
        print("INDS: wcba already present, skipping")
        return h
    anchor = ("      {k:'births',  label:'Live births',                "
              "unit:'births / year', fmt:'big', scale:1000, grp:'Fertility & births'},")
    assert h.count(anchor) == 1, f"INDS anchor count={h.count(anchor)}"
    add = (anchor + "\n"
           "      {k:'wcba',    label:'Women 15–49 (childbearing age)', "
           "unit:'women', fmt:'big', scale:1000, grp:'Fertility & births'},\n"
           "      {k:'wcba_pct',label:'Women 15–49, % of population',   "
           "unit:'%',             fmt:'1', scale:1, grp:'Fertility & births'},")
    return h.replace(anchor, add)


def main():
    patch_export()
    fp = ROOT / "dhi_globe.html"
    h = open(fp, encoding="utf-8").read()
    if '"wcba":' in h or "'wcba'" in h.split("const DATA=")[0][-0:]:  # crude guard
        pass
    h = patch_blob(h)
    h = patch_projd(h)
    h = patch_groups(h)
    h = patch_inds(h)
    open(fp, "w", encoding="utf-8").write(h)
    print("dhi_globe.html: blob + PROJD + GROUPS + INDS patched")


if __name__ == "__main__":
    main()
