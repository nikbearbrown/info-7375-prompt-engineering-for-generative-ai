"""Hand-weighted scorer for filter results.

Usage (from the repo root):
    python3 -m js3.scorer
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RESULTS = ROOT / "output" / "filter_results.json"
BOARDS = ["databricks", "stripe", "spotify"]  # fixed order; ties keep this order

# All three weights are hand-set by me. None was fitted on labelled data.
DEFAULT_WEIGHTS = {"title_match": 60, "topic_bonus": 20, "description": 20}


def score_posting(posting_result: dict, weights: dict | None = None) -> dict:
    """Score one evaluate() result from js3.filter on a 0-100 scale.

    Components (every weight is HAND-SET, not learned):
    - title_match (60): reason is "title_match" or "title_and_topic".
    - topic_bonus (20): reason is "title_and_topic".
    - description (20): description_available is True.

    A posting that failed the filter (passed is False) scores 0 on every
    component, so a rejected posting with a description doesn't earn 20.

    The default weights sum to 100. Pass ``weights`` to try a different
    hand-set value (for example description=0); missing keys use the defaults.
    Returns {"score": int, "breakdown": {component: points}}.
    """
    w = {**DEFAULT_WEIGHTS, **(weights or {})}
    if posting_result.get("passed") is False:
        return {"score": 0, "breakdown": {k: 0 for k in ("title_match", "topic_bonus", "description")}}
    reason = posting_result.get("reason")
    breakdown = {
        "title_match": w["title_match"] if reason in ("title_match", "title_and_topic") else 0,
        "topic_bonus": w["topic_bonus"] if reason == "title_and_topic" else 0,
        "description": w["description"] if posting_result.get("description_available") is True else 0,
    }
    return {"score": sum(breakdown.values()), "breakdown": breakdown}


def score_all(filter_results_path: Path | str = RESULTS, weights: dict | None = None) -> list[dict]:
    """Score every passed posting, sorted by score descending.

    Ties keep filter_results.json order (databricks, stripe, spotify, then
    file order), because Python's sort is stable.
    """
    with Path(filter_results_path).open("r", encoding="utf-8") as f:
        results = json.load(f)
    scored = []
    for board in BOARDS:
        for r in results.get(board, []):
            if not r.get("passed"):
                continue
            s = score_posting(r, weights)
            scored.append({
                "board": board,
                "id": r.get("id"),
                "title": " ".join(str(r.get("title", "")).split()),
                "reason": r.get("reason"),
                "description_available": r.get("description_available"),
                **s,
            })
    return sorted(scored, key=lambda x: x["score"], reverse=True)


if __name__ == "__main__":
    for row in score_all():
        print(f"{row['score']:>3}  {row['board']:<10} {row['title']}")
