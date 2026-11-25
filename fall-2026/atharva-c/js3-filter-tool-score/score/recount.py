"""Recount the survey numbers that were first counted by throwaway scripts.

    python3 -m score.recount
"""

from __future__ import annotations

import collections
import re

from agent import filter as F
from agent.label_sheet import stratum
from agent.postings import load_run

ps = load_run(F.RUN)
pairs = collections.Counter((p["board"], p["title"]) for p in ps)
dup = [n for n in pairs.values() if n > 1]
print(f"board+title groups with 2+ postings: {len(dup)}; postings in them: {sum(dup)}; "
      f"extra copies (400 - {len(pairs)} unique): {len(ps) - len(pairs)}")
print("strata:", dict(sorted(collections.Counter(stratum(p) for p in ps).items())))

eng2 = [p for p in ps if re.search(r"\bEngineer II\b", p["title"])]
def bucket(p):
    if re.search(r"No fixed minimum years", p["text"], re.I):
        return "no fixed minimum"
    n = F.min_years(p["text"])
    return "none" if n is None else f"{n}+"
print(f"'Engineer II' titles: {len(eng2)}", dict(collections.Counter(bucket(p) for p in eng2)))

hits = [p["title"] for p in ps if "software engineer i" in p["title"].lower()]
kinds = collections.Counter("SWE I" if re.search(r"Engineer I\b(?!I)", t) else "SWE II" if "Engineer II" in t else "other"
                            for t in hits)
print(f"substring 'Software Engineer I': {len(hits)}", dict(kinds))


def wilson(k: int, n: int, z: float = 1.96) -> tuple[float, float]:
    """95% Wilson score interval for k successes in n trials."""
    p = k / n
    centre = (p + z * z / (2 * n)) / (1 + z * z / n)
    half = z * ((p * (1 - p) / n + z * z / (4 * n * n)) ** 0.5) / (1 + z * z / n)
    return max(0.0, centre - half), min(1.0, centre + half)


lo, hi = wilson(0, 30)
print(f"audit: 0 of 30 random rejects wrong -> 95% Wilson {lo:.1%} to {hi:.1%}; "
      f"x 378 rejects = about {lo * 378:.0f} to {hi * 378:.0f} (a sample estimate for this run)")
