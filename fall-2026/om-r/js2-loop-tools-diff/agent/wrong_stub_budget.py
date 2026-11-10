"""DELIBERATELY WRONG implementation - kept only as test evidence.

GATE.md wrong version 1, "budget silently ignored": it notices the request
budget is exceeded, LOGS it, and keeps making requests anyway. Board
failures are handled correctly, so only the budget test should catch it.

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
    for board in boards:
        if report["requests_made"] >= max_requests:
            log.warning("budget exceeded: %d requests >= %d", report["requests_made"], max_requests)  # ...and carries on
        report["requests_made"] += 1
        try:
            raw = json.loads(fetch(URLS[board], timeout=30))
            report["boards"][board] = {"board_status": "ok", "error": None, "new": []}
        except Exception as e:
            report["boards"][board] = {"board_status": "failed", "error": str(e), "new": []}
    return report


def format_report(report):
    out = [f"exit: {report['exit']}"]
    for b, r in report["boards"].items():
        out.append(f"{b}: FAILED - {r['error']}" if r["board_status"] == "failed" else f"{b}: ok, {len(r['new'])} new")
    return "\n".join(out)
