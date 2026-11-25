"""Recompute every number in review/AUDIT.md from the hand labels (review/audit-labels.csv), the key (review/audit-key.json)
and the snapshot. Usage: python scripts/audit_summary.py > results/audit-summary.txt
Audit was run on filter v1 (results/filter-v1.json); labels 26 and 34 were changed N -> ? after the key was opened (cbcec48)."""
import collections
import csv
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from earlybird import boards, rule  # noqa: E402
from earlybird.resume import load_resume  # noqa: E402


def wilson(k, n, z=1.96):
    p = k / n
    d = 1 + z * z / n
    c = (p + z * z / (2 * n)) / d
    h = z * math.sqrt(p * (1 - p) / n + z * z / (4 * n * n)) / d
    return f"{max(0, c - h):.1%} to {min(1, c + h):.1%}"


lab = {int(r["n"]): r["verdict"].strip().upper() for r in csv.DictReader(open(ROOT / "review/audit-labels.csv", encoding="utf-8"))}
key = json.loads((ROOT / "review/audit-key.json").read_text(encoding="utf-8"))
by = collections.defaultdict(list)
for k in key:
    k["mine"] = lab[k["n"]]
    by[k["group"]].append(k)

print("== Reject audit (filter v1), my labels as committed now ==")
for g in ("random_reject", "close_call"):
    items = by[g]
    wrong = [i for i in items if i["mine"] == "Y"]
    unsure = [i for i in items if i["mine"] == "?"]
    print(f"{g}: n={len(items)} filter-rejected, I said Y (false rejects)={len(wrong)} ({wilson(len(wrong), len(items))}), "
          f"? ={len(unsure)}; rules in sample: {dict(collections.Counter(i['failed_check'] for i in items))}")
    for i in wrong:
        print(f"   false reject #{i['n']}: {i['title'].strip()} ({i['failed_check']})")
kept = by["kept"]
bad = [i for i in kept if i["mine"] == "N"]
unsure = [i for i in kept if i["mine"] == "?"]
print(f"kept: n={len(kept)}, I said Y={sum(1 for i in kept if i['mine'] == 'Y')}, N={len(bad)} ({wilson(len(bad), len(kept))}), ?={len(unsure)}")
for i in bad + unsure:
    print(f"   kept #{i['n']} label {i['mine']}: {i['title'].strip()[:60]}")

print("\n== False friends, measured on the 2026-11-01 snapshot (3068 postings) ==")
resume = load_resume(ROOT / "data/resume/rohan-desai.example.json")
posts = []
for f in sorted((ROOT / "data/snapshot-2026-11-01").glob("*.json")):
    posts += boards.parse(f.stem.split("_")[0], f.read_text(encoding="utf-8"))
role = [bool(rule.ROLE.search(p["title"])) and not rule.ML.search(p["title"]) for p in posts]
text = [p["descriptionPlain"] for p in posts]
train = [bool(re.search(r"\btraining\b", t, re.I)) for t in text]
print(f"'training' appears in {sum(train)} postings; {sum(1 for a, b in zip(train, role) if a and b)} of them have a role title "
      f"({sum(1 for a, b in zip(train, role) if a and b) / sum(train):.1%}); the other {sum(1 for a, b in zip(train, role) if a and not b)} "
      f"would be wrongly kept by a filter that treats 'training' as a signal (W2)")
sp = [bool(re.search(r"sponsor", t, re.I)) for t in text]
visa = [bool(re.search(r"(?:h-?1b|f-?1|visa|work authori[sz]ation)[^.]{0,80}sponsor|sponsor[^.]{0,80}(?:h-?1b|f-?1|visa|work authori[sz]ation)", t, re.I)) for t in text]
print(f"'sponsor' appears in {sum(sp)} postings; {sum(visa)} of them are about visas ({sum(visa) / sum(sp):.1%}); the rest are things like "
      f"'executive sponsor' (false friend for R4)")
ml = [bool(re.search(r"\bML\b", p["title"], re.I)) for p in posts]
html = [bool(re.search(r"ml", p["title"], re.I)) and not re.search(r"\bML\b", p["title"]) for p in posts]
print(f"'ML' in a title: {sum(ml)} postings (case-insensitive 'ml' substring also hits {sum(html)} more, e.g. HTML)")
