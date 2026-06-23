"""
Ask Demoria — a grounded natural-language layer over the Demoria dataset.

The model answers questions in plain English, but every figure it returns comes
from a tool call against the real database (demoria_data.py), stamped with its
provenance (NSO / DRE / WPP). It never invents a number. Built on the Anthropic
SDK tool-runner.

Usage:
  export ANTHROPIC_API_KEY=...
  python3 ask_demoria.py "Which countries have the lowest fertility in 2025?"
  python3 ask_demoria.py            # interactive REPL

Model defaults to claude-opus-4-8; override with --model.
"""
import json
import sys
import anthropic
from anthropic import beta_tool

import demoria_data as D

MODEL = "claude-opus-4-8"

# ---------- tools (each returns a JSON string the model reads) ----------

@beta_tool
def resolve_country(name: str) -> str:
    """Resolve a country name or ISO3 code to its canonical ISO3 code and official name.

    Args:
        name: A country name, common alias, or ISO3 code (e.g. "South Korea", "UK", "USA").
    """
    iso = D.resolve_country(name)
    if not iso:
        return json.dumps({"error": f"No country matched '{name}'."})
    return json.dumps({"iso": iso, "name": D.country_name(iso)})


@beta_tool
def get_indicator_value(country: str, indicator: str, year: int) -> str:
    """Get one indicator value for one country in one year, with its source (NSO/DRE/WPP).

    Args:
        country: Country name or ISO3 code.
        indicator: Indicator key (e.g. tfr, pop, births, dhi, wcba, wcba_pct, oadr, medage).
        year: A year from 1965 to 2025.
    """
    iso = D.resolve_country(country)
    if not iso:
        return json.dumps({"error": f"No country matched '{country}'."})
    r = D.get_value(iso, indicator, year)
    return json.dumps(r or {"error": f"No value for {indicator} in {iso} {year}."})


@beta_tool
def get_indicator_series(country: str, indicator: str, year_from: int = 1965, year_to: int = 2025) -> str:
    """Get a time series of one indicator for one country across a year range, each year sourced.

    Args:
        country: Country name or ISO3 code.
        indicator: Indicator key (e.g. tfr, births, pop, wcba).
        year_from: First year (>= 1965).
        year_to: Last year (<= 2025).
    """
    iso = D.resolve_country(country)
    if not iso:
        return json.dumps({"error": f"No country matched '{country}'."})
    r = D.get_series(iso, indicator, year_from, year_to)
    return json.dumps(r or {"error": "No series."})


@beta_tool
def rank_countries(indicator: str, year: int = 2025, order: str = "desc", n: int = 10) -> str:
    """Rank countries by an indicator in a given year. Use order='asc' for lowest, 'desc' for highest.

    Args:
        indicator: Indicator key (e.g. tfr, dhi, oadr, wcba_pct).
        year: The year (1965-2025).
        order: 'asc' (lowest first) or 'desc' (highest first).
        n: How many to return.
    """
    return json.dumps(D.rank(indicator, year, order, max(1, min(n, 50))))


@beta_tool
def compare_countries(countries: str, indicator: str, years: str) -> str:
    """Compare several countries on one indicator across several years.

    Args:
        countries: Comma-separated country names or ISO3 codes (e.g. "Korea, Italy, Japan").
        indicator: Indicator key.
        years: Comma-separated years (e.g. "2000, 2025").
    """
    isos = [D.resolve_country(c.strip()) for c in countries.split(",") if c.strip()]
    isos = [i for i in isos if i]
    yrs = [int(y.strip()) for y in years.split(",") if y.strip().isdigit()]
    return json.dumps(D.compare(isos, indicator, yrs))


@beta_tool
def get_cohort_cliff(country: str, cliff: str) -> str:
    """Get a demographic 'cliff' metric for a country (peak year, current value, % change).

    Args:
        country: Country name or ISO3 code.
        cliff: One of baby, kindergarten, higher_ed, manpower, first_home, peak_workers, silver.
    """
    iso = D.resolve_country(country)
    if not iso:
        return json.dumps({"error": f"No country matched '{country}'."})
    r = D.get_cliff(iso, cliff)
    return json.dumps(r or {"error": f"No '{cliff}' cliff for {iso}."})


@beta_tool
def search_pronatal_policies(mechanism: str = "", verdict: str = "", country: str = "") -> str:
    """Search the pronatal policy library. Filter by mechanism, verdict, and/or country (any may be blank).

    Args:
        mechanism: Cash, Leave, Childcare, Housing, Tax, Culture, Immigration, Access (or blank).
        verdict: Cautionary, Mixed, Promising (or blank).
        country: Country name substring (or blank).
    """
    return json.dumps(D.search_policies(mechanism or None, verdict or None, country or None))


TOOLS = [resolve_country, get_indicator_value, get_indicator_series, rank_countries,
         compare_countries, get_cohort_cliff, search_pronatal_policies]

_IND_LIST = "\n".join(f"  {k} — {label} ({unit})" for k, (label, unit) in D.INDICATORS.items())
_CLIFF_LIST = "\n".join(f"  {k} — {label}" for k, label in D.CLIFF_LABELS.items())

SYSTEM = f"""You are Ask Demoria, the question-answering layer of Demoria Research \
(demoriaresearch.com), a demographic-intelligence firm.

Voice: British English, plain and precise, a touch of dry personality. No em dashes. \
Avoid the "not X but Y" cadence. Keep answers tight.

Hard rules:
- Every figure you state MUST come from a tool call. Never recall or estimate a number yourself.
- When you give a figure, name its source tier in brackets: (NSO) national statistics, \
(DRE) a Demoria Research Estimation, or (WPP) the UN baseline.
- The data covers 236 countries and territories, annual 1965 to 2025. If a question asks for \
something outside that (e.g. a 2030 value, or an indicator we do not hold), say so plainly \
rather than guessing.
- Resolve country names with the tools before querying. If a name is ambiguous or unknown, say so.
- Be honest about limits, in the house style: most pronatal policy barely moves completed \
fertility; current-year rebounds may be compositional.

Indicator keys you can query:
{_IND_LIST}

Cohort cliff keys:
{_CLIFF_LIST}

Answer the user's question, calling tools as needed, then give a clear final answer that a \
journalist or policymaker could quote."""


def ask(question: str, model: str = MODEL) -> str:
    client = anthropic.Anthropic()
    runner = client.beta.messages.tool_runner(
        model=model,
        max_tokens=4000,
        thinking={"type": "adaptive"},
        system=SYSTEM,
        tools=TOOLS,
        messages=[{"role": "user", "content": question}],
    )
    final = None
    for message in runner:
        final = message
        for block in message.content:
            if block.type == "tool_use":
                print(f"  · {block.name}({json.dumps(block.input)})", file=sys.stderr)
    if not final:
        return "(no response)"
    return "\n".join(b.text for b in final.content if b.type == "text").strip()


def main():
    args = [a for a in sys.argv[1:]]
    model = MODEL
    if "--model" in args:
        i = args.index("--model")
        model = args[i + 1]
        del args[i:i + 2]
    if args:
        print(ask(" ".join(args), model))
        return
    print("Ask Demoria. Type a question (blank line to quit).")
    while True:
        try:
            q = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if not q:
            break
        print(ask(q, model))


if __name__ == "__main__":
    main()
