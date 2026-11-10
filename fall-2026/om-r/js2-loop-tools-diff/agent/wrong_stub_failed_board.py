"""DELIBERATELY WRONG implementation - kept only as test evidence.

GATE.md wrong version 2, "failed board reported as no new jobs": it catches
the fetch exception, then falls through to the normal path with an empty
job list, so a 404 board reads as "ok, 0 new". The request budget is
enforced correctly, so only the failed-board test should catch it.

Never import this from the agent. It exists so the tests can be shown to fail.
"""
import json
import logging

log = logging.getLogger(__name__)
URLS = {
    "gitlab": "https://boards-api.greenhouse.io/v1/boards/gitlab/jobs?content=true",
    "stripe": "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true",
    "palantir": "https://api.lever.co/v0/postings/palantir?mode=json&limit=100&skip=0",
}


def run(boards, *, root, fetch, budgets=None, approved_new_boards=(), sleep=None, clock=None):
    max_requests = (budgets or {}).get("max_requests", 15)
    report = {"exit": "finished", "requests_made": 0, "budget_hit": None, "not_attempted": [], "boards": {}}
    for i, board in enumerate(boards):
        if report["requests_made"] >= max_requests:
            report.update(exit="budget-exhausted", budget_hit={"budget": "requests", "limit": max_requests},
                          not_attempted=list(boards[i:]))
            break
        report["requests_made"] += 1
        try:
            jobs = json.loads(fetch(URLS[board], timeout=30))
        except Exception as e:
            log.warning("fetch failed for %s: %s", board, e)
            jobs = []  # <- the bug: a failed fetch becomes "nothing new"
        report["boards"][board] = {"board_status": "ok", "error": None, "new": []}
    return report


def format_report(report):
    out = [f"exit: {report['exit']}"]
    for b, r in report["boards"].items():
        out.append(f"{b}: ok, {len(r['new'])} new")
    return "\n".join(out)
