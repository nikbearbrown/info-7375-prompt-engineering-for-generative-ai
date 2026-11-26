"""FILTER.md §5: the reject-audit draw, the blind worksheet, and the report.

The draw is made from the v0.1 decisions with ``random.Random(20261125)`` in a fixed
order: 40 random rejects, then 12 random kept (excluding the 8 lowest kept). The close
calls are deterministic. The v0.3 "changed or contested" stratum is appended after.
"""

from __future__ import annotations

import math
import random
from collections.abc import Callable, Mapping, Sequence
from typing import Any

from job_search_agent.js3.claims import segments
from job_search_agent.js3.corpus import Entry
from job_search_agent.js3.filter import Scored

SEED = 20261125
N_RANDOM_REJECTS = 40
N_CLOSE_EACH = 8
N_RANDOM_KEPT = 12
CONTESTED_TITLES = ("forward deployed engineer",)
VERDICTS = ("RELEVANT", "NOT_RELEVANT", "CANNOT_TELL")


def _order(s: Scored) -> tuple[str, str]:
    return (s.board, s.posting.posting_id)


def draw(v01: Sequence[Scored], v03: Mapping[str, Scored]) -> dict[str, list[str]]:
    """Returns stratum -> keys, in draw order (FILTER.md §5 and its v0.3 amendment)."""
    rejected = sorted((s for s in v01 if not s.kept), key=_order)
    kept = sorted((s for s in v01 if s.kept), key=_order)
    close_rejected = sorted(rejected, key=lambda s: (-s.total, *_order(s)))[
        :N_CLOSE_EACH
    ]
    close_kept = sorted(kept, key=lambda s: (s.total, *_order(s)))[:N_CLOSE_EACH]
    rng = random.Random(SEED)  # noqa: S311 - seeded draw for a reproducible audit, not security
    random_rejects = rng.sample(rejected, N_RANDOM_REJECTS)
    low = {s.key for s in close_kept}
    random_kept = rng.sample([s for s in kept if s.key not in low], N_RANDOM_KEPT)
    changed = [s for s in v01 if s.kept != v03[s.key].kept]
    contested = [
        s for s in v01 if any(t in s.posting.title.lower() for t in CONTESTED_TITLES)
    ]
    seen: set[str] = set()
    extra = []
    for s in sorted(changed, key=_order) + sorted(contested, key=_order):
        if s.key not in seen:
            seen.add(s.key)
            extra.append(s.key)
    return {
        "random_rejects": [s.key for s in random_rejects],
        "close_rejected": [s.key for s in close_rejected],
        "close_kept": [s.key for s in close_kept],
        "random_kept": [s.key for s in random_kept],
        "changed_or_contested": extra,
    }


def worksheet_order(strata: Mapping[str, list[str]]) -> list[str]:
    """Every drawn key once, shuffled with a generator seeded after the draw."""
    keys = list(dict.fromkeys(k for ks in strata.values() for k in ks))
    random.Random(SEED + 1).shuffle(keys)  # noqa: S311 - seeded shuffle, not security
    return keys


AVOID_UNTIL_DONE = (
    "data/js3/audit/draw.json",
    "FILTER.md §8 and experiments/js3/filters/",
    "docs/js3/SHORTLIST.md and SHORTLIST_NOTES.md",
    "docs/js3/AUDIT.md §2 and docs/js3/filter/",
    "data/js3/filter/ and data/js3/shortlist.json",
    "docs/js3/SCORE.md",
    'the README "What ran" table',
)
"""Files that reveal the filter's decisions on worksheet postings (review fix)."""


def render_worksheet(order: Sequence[str], entries: Mapping[str, Entry]) -> str:
    """The blind worksheet: full posting text; no score, no decision, no stratum."""
    lines = [
        "# Reject-audit worksheet (JS3, FILTER.md §5)",
        "",
        "Judge each posting yourself, for Kiran Joshi: "
        "`RELEVANT` (a role Kiran targets, at a level",
        "and in a place Kiran could take, so you would want to see it), "
        "`NOT_RELEVANT`, or",
        "`CANNOT_TELL`. Write the verdict and a short reason into",
        "`experiments/js3/audit/hand_verdicts.json` (copy the template beside it). "
        "The filter's",
        "score, decision and stratum are deliberately not shown.",
        "",
        "**Until every verdict is written, do not open:**",
        "",
        *[f"- {item}" for item in AVOID_UNTIL_DONE],
        "",
        f"{len(order)} postings, each with its full saved text (collected on or "
        "before 2026-11-11; the link may no longer work).",
        "",
    ]
    for n, key in enumerate(order, 1):
        e = entries[key]
        p = e.posting
        deps = ", ".join(d for d in p.department_names if d) or "—"
        where = p.location_name if p.location_name is not None else "(none given)"
        body = segments(p.content_raw) or ["(no text)"]
        lines += [
            f"## {n}. {p.title.strip()}",
            "",
            f"- **Key:** `{key}`",
            f"- **Location:** {where}",
            f"- **Departments:** {deps}",
            f"- **Link:** {e.url}",
            "",
            "<details><summary>Full text</summary>",
            "",
            *[f"> {line}  " for line in body],
            "",
            "</details>",
            "",
        ]
    return "\n".join(lines)


def template(order: Sequence[str], entries: Mapping[str, Entry]) -> dict[str, Any]:
    """The blank verdict file, in worksheet order."""
    return {
        "judged_by": None,
        "judged_on": None,
        "verdict_values": list(VERDICTS),
        "verdicts": [
            {
                "key": k,
                "title": entries[k].posting.title.strip(),
                "verdict": None,
                "reason": "",
            }
            for k in order
        ],
    }


def _binom_cdf(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k + 1))


def clopper_pearson(k: int, n: int, alpha: float = 0.05) -> tuple[float, float]:
    """Exact two-sided binomial interval for k successes in n, by bisection."""
    if n <= 0:
        raise ValueError("n must be positive")

    def solve(f: Callable[[float], bool]) -> float:
        lo, hi = 0.0, 1.0
        for _ in range(100):
            mid = (lo + hi) / 2
            lo, hi = (mid, hi) if f(mid) else (lo, mid)
        return (lo + hi) / 2

    lower = 0.0 if k == 0 else solve(lambda p: 1 - _binom_cdf(k - 1, n, p) < alpha / 2)
    upper = 1.0 if k == n else solve(lambda p: _binom_cdf(k, n, p) > alpha / 2)
    return lower, upper


def validate_verdicts(doc: Mapping[str, Any], order: Sequence[str]) -> list[str]:
    """Problems with a filled verdict file.

    Empty when it is complete and matches the draw.
    """
    problems = []
    if not doc.get("judged_by") or not doc.get("judged_on"):
        problems.append("judged_by and judged_on must be filled")
    got = [v.get("key") for v in doc.get("verdicts", [])]
    if sorted(got) != sorted(order):
        problems.append("the verdict keys do not match the draw")
    for v in doc.get("verdicts", []):
        if v.get("verdict") not in VERDICTS:
            problems.append(f"{v.get('key')}: verdict must be one of {VERDICTS}")
    return problems


def tally(
    strata: Mapping[str, list[str]],
    verdicts: Mapping[str, str],
    kept: Mapping[str, bool],
) -> dict[str, dict[str, int]]:
    """Per stratum: n, filter wrong, filter right, cannot tell, for one filter version.

    A kept posting judged NOT_RELEVANT and a rejected one judged RELEVANT are wrong.
    """
    out = {}
    for name, keys in strata.items():
        row = {"n": len(keys), "wrong": 0, "right": 0, "cannot_tell": 0}
        for k in keys:
            v = verdicts[k]
            if v == "CANNOT_TELL":
                row["cannot_tell"] += 1
            elif (v == "RELEVANT") == kept[k]:
                row["right"] += 1
            else:
                row["wrong"] += 1
        out[name] = row
    return out
