#!/usr/bin/env python3
"""eval_rows_after_fix.py — re-run the same 25 evaluation companies after the brand-name fix (2026-11-23).

Same companies, same typed names, same CSV as ../../final-project-film/evidence/eval_rows.py (2026-10-25).
Calls the recipe's own matcher with the recipe's own alias file. Prints JSON.
Usage: python3 eval_rows_after_fix.py <path-to-the-reallocation-engine checkout>
"""
import json, os, sys

REPO = os.path.abspath(sys.argv[1])
RECIPE = os.path.join(REPO, "scripts/contrib/2026fa/arundhatik26-coop-sponsor-swe-15-1252")
sys.path.insert(0, RECIPE)
import coop_sponsor_check as c  # noqa: E402

COMPANIES = ["PayPal", "Visa", "Goldman Sachs", "Mastercard", "BlackRock", "LSEG",
             "JPMorgan Chase", "Morgan Stanley", "Citi", "Bank of America", "Wells Fargo", "Capital One",
             "BNY", "State Street", "Fidelity", "Charles Schwab",
             "Stripe", "Plaid", "Robinhood", "Chime", "Affirm", "Ramp", "Brex", "Coinbase", "SoFi"]
RULES = {"proven_min_approvals": 100, "p_proven": 0.9, "p_likely": 0.6, "p_sponsors_not_software": 0.3}

csv_path = os.path.join(REPO, c.SPONSOR_CSV)
idx = c.load_sponsor_index(csv_path)
aliases = c.load_aliases(c.DEFAULT_ALIASES)
out = []
for co in COMPANIES:
    ev = c.resolve_company({"company": co}, idx, RULES, aliases)
    out.append({"company": co, "status": ev["status"],
                "tier": (ev.get("tier") or {}).get("value"),
                "total_approvals": (ev.get("total_approvals") or {}).get("value"),
                "candidates": ev.get("rows", [])})
print(json.dumps({"csv": c.SPONSOR_CSV, "csv_sha256": c.sha256(csv_path), "aliases": aliases, "rows": out}, indent=2))
