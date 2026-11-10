"""Run the 14 boundary cases and print predicted (PREDICTIONS.md) vs actual.

    python3 -B review/boundary_table.py
"""
import pathlib
import re
import shutil
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from tests.boundary_cases import CASES, outcome, sandbox  # noqa: E402

pred = {}
for line in (ROOT / "PREDICTIONS.md").read_text().splitlines():
    m = re.match(r"\| (\d+) \|.*?\| \*\*(Allow|Refuse|Ask me)\*\* \|", line)
    if m:
        pred[int(m.group(1))] = {"Allow": "allow", "Refuse": "refuse",
                                 "Ask me": "ask"}[m.group(2)]
tmp, policy, outside = sandbox()
try:
    print("| # | predicted | actual | match |")
    print("|---|---|---|---|")
    wrong = 0
    for n, op, target, _ in CASES:
        act = outcome(policy, outside, op, target)
        ok = act == pred[n]
        wrong += not ok
        print(f"| {n} | {pred[n]} | {act} | {'yes' if ok else 'NO'} |")
    print(f"\n{len(CASES) - wrong}/{len(CASES)} predictions matched")
finally:
    shutil.rmtree(tmp)
