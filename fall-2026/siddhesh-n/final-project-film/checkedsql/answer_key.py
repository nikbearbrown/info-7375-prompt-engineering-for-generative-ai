#!/usr/bin/env python3
"""answer_key.py — computes the expected answer to each test question straight from the CSV,
in plain Python with no SQL, so the key is an independent path from the queries it grades.

    python3 answer_key.py            # print the key and the arithmetic behind it
    python3 answer_key.py --check    # also confirm tests/questions.json holds the same values

Every answer is also small enough to check with a calculator: see HAND-CHECK.md.
"""
import csv
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
rows = list(csv.DictReader(open(HERE / "data" / "campaigns.csv")))
for r in rows:
    for k in ("week", "impressions", "clicks", "conversions", "spend", "revenue"):
        r[k] = int(r[k])


def total(key, where=lambda r: True):
    return sum(r[key] for r in rows if where(r))


def by(group, key):
    out = defaultdict(int)
    for r in rows:
        out[r[group]] += r[key]
    return dict(out)


spend, revenue = total("spend"), total("revenue")
ch_spend, ch_rev, ch_conv = by("channel", "spend"), by("channel", "revenue"), by("channel", "conversions")
ch_roas = {c: ch_rev[c] / ch_spend[c] for c in ch_spend}
wk_profit = {w: by("week", "revenue")[w] - by("week", "spend")[w] for w in by("week", "spend")}

key = {
    "Q01": (spend, f"sum of spend over {len(rows)} rows = {spend}"),
    "Q02": (revenue, f"sum of revenue = {revenue}"),
    "Q03": (round(revenue / spend, 2), f"{revenue} / {spend} = {revenue / spend:.4f}"),
    "Q04": (round(100 * total('clicks') / total('impressions'), 2),
            f"100 * {total('clicks')} / {total('impressions')} = {100 * total('clicks') / total('impressions'):.4f}"),
    "Q05": (max(ch_conv, key=ch_conv.get), f"conversions by channel: {ch_conv}"),
    "Q06": (max(ch_roas, key=ch_roas.get),
            "ROAS by channel (total revenue / total spend): "
            + ", ".join(f"{c} {ch_rev[c]}/{ch_spend[c]} = {v:.3f}" for c, v in ch_roas.items())),
    "Q07": (round(ch_roas["Email"], 2), f"Email {ch_rev['Email']} / {ch_spend['Email']} = {ch_roas['Email']:.4f}"),
    "Q08": (round(100 * total("conversions", lambda r: r["device"] == "Mobile")
                  / total("clicks", lambda r: r["device"] == "Mobile"), 2),
            f"Mobile 100 * {total('conversions', lambda r: r['device'] == 'Mobile')} / "
            f"{total('clicks', lambda r: r['device'] == 'Mobile')}"),
    "Q09": (max(wk_profit, key=wk_profit.get), f"profit by week (revenue - spend): {wk_profit}"),
    "Q10": (sum(1 for r in rows if r["revenue"] < r["spend"]),
            "rows with revenue < spend: "
            + ", ".join(f"wk{r['week']} {r['channel']} {r['device']}" for r in rows if r["revenue"] < r["spend"])),
}

# The trap the film describes: averaging ROAS row by row instead of total / total.
row_avg = defaultdict(list)
for r in rows:
    row_avg[r["channel"]].append(r["revenue"] / r["spend"])
trap = {c: sum(v) / len(v) for c, v in row_avg.items()}

if __name__ == "__main__":
    for q, (ans, why) in key.items():
        print(f"{q}: {ans!r:<12}  {why}")
    print("\nTRAP (row-average ROAS, wrong):", ", ".join(f"{c} {v:.2f}" for c, v in trap.items()),
          "-> winner", max(trap, key=trap.get))
    if "--check" in sys.argv:
        tests = {t["id"]: t["expected"] for t in json.load(open(HERE / "tests" / "questions.json"))}
        bad = [q for q, (ans, _) in key.items() if tests.get(q) != ans]
        print("\nquestions.json matches the key" if not bad else f"\nMISMATCH in questions.json: {bad}")
        sys.exit(1 if bad else 0)
