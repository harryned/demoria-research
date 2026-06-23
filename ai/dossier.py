"""
Demoria country dossier generator.

Assembles a country's structured facts from the grounded data layer, then has
Claude write a one-page brief in the Demoria house voice. Every figure in the
prose is drawn from the FACTS block passed to the model; it is instructed to
introduce no number that is not there.

Usage:
  export ANTHROPIC_API_KEY=...
  python3 dossier.py "South Korea"
  python3 dossier.py KOR --out kor.md
  python3 dossier.py --facts-only "Japan"     # print the grounded facts, no model call
"""
import argparse
import json
import sys
import anthropic

import demoria_data as D

MODEL = "claude-opus-4-8"
IND = ["tfr", "births", "pop", "wcba", "wcba_pct", "medage", "oadr", "netmig", "dhi"]
YEARS = [1965, 1990, 2000, 2025]


def dhi_rank(iso: str, year: int = 2025) -> tuple[int, int] | None:
    rows = D.rank("dhi", year, "desc", n=999, sovereign_only=True)
    for i, r in enumerate(rows, 1):
        if r["iso"] == iso:
            return i, len(rows)
    return None


def build_facts(iso: str) -> dict:
    c = D.DATA[iso]
    cl = D.CLIFFS.get(iso, {})
    facts = {"country": c["name"], "iso": iso,
             "continent": cl.get("cont", ""), "population_basis": "thousands unless noted"}
    # headline score
    dhi = D.get_value(iso, "dhi", 2025)
    rank = dhi_rank(iso)
    facts["dhi_2025"] = (dhi or {}).get("value")
    facts["dhi_rank_2025"] = (f"{rank[0]} of {rank[1]} sovereign states" if rank else None)
    facts["pillars_2025"] = {p: (D.get_value(iso, p, 2025) or {}).get("value")
                             for p in ("p_fss", "p_pms", "p_wss", "p_mrs")}
    # indicator snapshots, with source tier
    snap = {}
    for ind in IND:
        row = {}
        for y in YEARS:
            v = D.get_value(iso, ind, y)
            if v:
                row[y] = {"value": v["value"], "source": v["source"]}
        if row:
            snap[ind] = {"label": D.INDICATORS[ind][0], "unit": D.INDICATORS[ind][1], "by_year": row}
    facts["indicators"] = snap
    # cohort cliffs
    facts["cliffs"] = {k: {kk: vv for kk, vv in (D.get_cliff(iso, k) or {}).items()
                           if kk in ("label", "peak", "end", "pct", "mult", "v2025", "v2050")}
                       for k in cl.get("cliffs", {})}
    # pronatal policies (if any catalogued for this country)
    facts["policies"] = D.search_policies(country=c["name"])
    return facts


SYSTEM = """You write one-page country dossiers for Demoria Research, a demographic-intelligence firm.

Voice: British English, plain and precise, a little dry personality. No em dashes. Avoid the \
"not X but Y" cadence and avoid tricolons. Honest above all: if the picture is grim say so, and \
where a recent rebound is likely compositional, say that too.

Absolute rule: every number in your dossier must come from the FACTS block provided. Do not \
introduce any figure that is not in FACTS. When a figure is a Demoria Research Estimation, note \
it is a DRE; otherwise you need not label sources in prose.

Structure (about 350-450 words, markdown):
  # <Country> — demographic dossier
  A one-line standfirst with the DHI score and rank.
  **The score.** What the DHI and its pillars say.
  **Fertility & births.** The trajectory, the peak-to-now fall, the childbearing base.
  **The cliffs ahead.** The one or two cohort cliffs that bite hardest, with the numbers.
  **What it would take.** If policies are catalogued, what has been tried and whether it worked; \
otherwise the honest options (and their limits).
  End with a single sober sentence."""


def write_dossier(iso: str, model: str = MODEL) -> str:
    facts = build_facts(iso)
    client = anthropic.Anthropic()
    resp = client.messages.create(
        model=model, max_tokens=2200, thinking={"type": "adaptive"},
        system=SYSTEM,
        messages=[{"role": "user", "content":
                   "Write the dossier from these FACTS only.\n\nFACTS:\n" + json.dumps(facts, indent=2)}],
    )
    return "\n".join(b.text for b in resp.content if b.type == "text").strip()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("country")
    ap.add_argument("--out")
    ap.add_argument("--model", default=MODEL)
    ap.add_argument("--facts-only", action="store_true")
    args = ap.parse_args()

    iso = D.resolve_country(args.country)
    if not iso:
        print(f"No country matched '{args.country}'.", file=sys.stderr)
        sys.exit(1)
    if args.facts_only:
        print(json.dumps(build_facts(iso), indent=2))
        return
    md = write_dossier(iso, args.model)
    if args.out:
        open(args.out, "w").write(md)
        print(f"Wrote {args.out}", file=sys.stderr)
    else:
        print(md)


if __name__ == "__main__":
    main()
