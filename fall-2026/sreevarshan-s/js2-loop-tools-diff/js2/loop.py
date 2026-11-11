"""The loop: check each board once under a fixed budget, then pick an exit.

Exit statuses (GATE.md section 1):
  finished          every planned board was checked successfully
  incomplete        at least one board failed, was empty, or was invalid
  budget-exhausted  a board, request, or time limit stopped the run
  error             something unexpected stopped the run

Budgets are fixed by GATE.md section 2 and are never raised in code.
"""

import json
import os
import time

from js2 import fetch, policy

MAX_BOARDS = 4
MAX_REQUESTS = 8
MAX_SECONDS = 90

BOARDS = [
    {"name": "Databricks", "ats": "greenhouse", "token": "databricks"},
    {"name": "Stripe", "ats": "greenhouse", "token": "stripe"},
    {"name": "Spotify", "ats": "lever", "token": "spotify"},
    {"name": "invalid-board-xyz", "ats": "greenhouse", "token": "invalid-board-xyz"},
]

FETCHERS = {"greenhouse": fetch.fetch_greenhouse, "lever": fetch.fetch_lever}
URLS = fetch.URL_BUILDERS


class InvalidBoardResponse(Exception):
    """A response parsed as JSON but is empty or not a postings list."""


def _utc_iso():
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def parse_postings(ats, data):
    """Return the posting IDs in a response, or raise InvalidBoardResponse.

    An empty board is a failure, not zero new jobs (GATE.md sections 1 and 7).
    """
    if ats == "greenhouse":
        if not isinstance(data, dict) or not isinstance(data.get("jobs"), list):
            raise InvalidBoardResponse("greenhouse response has no 'jobs' list")
        postings = data["jobs"]
    elif ats == "lever":
        if not isinstance(data, list):
            raise InvalidBoardResponse("lever response is not a list")
        postings = data
    else:
        raise InvalidBoardResponse("unknown ATS %r" % ats)
    if not postings:
        raise InvalidBoardResponse("board returned no postings")
    ids = []
    for p in postings:
        if not isinstance(p, dict) or p.get("id") in (None, ""):
            raise InvalidBoardResponse("a posting has no id")
        ids.append(str(p["id"]))
    return ids


def run(boards=None, fetchers=None, clock=time.monotonic, write_trace=True,
        output_dir=None, label=None, notes=None, parse=parse_postings):
    """Run the loop and return the trace.

    label (e.g. "SEEDED") is stored in the trace and appended to the trace
    file name. parse is swappable only so the wrong-answer demo can show a
    bug; normal runs always use parse_postings.
    """
    boards = BOARDS if boards is None else boards
    fetchers = FETCHERS if fetchers is None else fetchers
    output_dir = policy.ALLOWED_OUTPUT if output_dir is None else output_dir
    started = clock()
    decisions_start = len(policy.DECISIONS)

    trace = {
        "label": label,
        "notes": notes,
        "started_utc": _utc_iso(),
        "budget": {"max_boards": MAX_BOARDS, "max_requests": MAX_REQUESTS, "max_seconds": MAX_SECONDS},
        "boards": [],
        "attempts": [],
    }
    requests_used = 0
    successes = {}
    failures = set()
    budget_hit = None
    status = None
    error = None

    def elapsed():
        return clock() - started

    def budget_reason(boards_done):
        if boards_done >= MAX_BOARDS:
            return "board limit %d reached" % MAX_BOARDS
        if requests_used >= MAX_REQUESTS:
            return "request limit %d reached" % MAX_REQUESTS
        if elapsed() >= MAX_SECONDS:
            return "time limit %ds reached" % MAX_SECONDS
        return None

    def attempt(board, url, number, reason):
        nonlocal requests_used
        requests_used += 1
        entry = {
            "board": board["name"],
            "ats": board["ats"],
            "token": board["token"],
            "url": url,
            "attempt": number,
            "reason": reason,
            "time_utc": _utc_iso(),
            "elapsed_s": round(elapsed(), 3),
        }
        trace["attempts"].append(entry)
        timeout = max(0.1, min(fetch.REQUEST_TIMEOUT, MAX_SECONDS - elapsed()))
        try:
            result = fetchers[board["ats"]](board["token"], timeout=timeout)
        except fetch.BoardFetchError as e:
            entry.update(outcome="failed", kind=e.kind, status_code=e.status_code,
                         retriable=e.retriable, message=str(e))
            raise
        entry.update(outcome="fetched", status_code=result["status_code"],
                     raw_path=result["raw_path"], raw_write_decision=result["raw_write_decision"])
        if "seeded_from" in result:
            entry.update(source="SEEDED", seeded_from=result["seeded_from"])
        return result, entry

    try:
        for i, board in enumerate(boards):
            reason = budget_reason(i)
            if reason:
                budget_hit = reason
                for skipped in boards[i:]:
                    trace["boards"].append({"board": skipped["name"], "ats": skipped["ats"],
                                            "outcome": "not_checked", "reason": reason})
                break

            url = URLS[board["ats"]](board["token"])
            key = ("GET", board["ats"], board["token"], url)
            record = {"board": board["name"], "ats": board["ats"], "token": board["token"], "url": url,
                      "outcome": "in_progress"}
            trace["boards"].append(record)

            if key in successes:
                prior = successes[key]
                record.update(outcome="ok", reused=True, posting_count=prior["posting_count"],
                              posting_ids=prior["posting_ids"], raw_path=prior["raw_path"])
                trace["attempts"].append({"board": board["name"], "url": url, "outcome": "reused",
                                          "reason": "repeat rule: same request already succeeded this run",
                                          "time_utc": _utc_iso(), "elapsed_s": round(elapsed(), 3)})
                continue

            if key in failures:
                record.update(outcome="failed", kind="repeat_failed", reused=True,
                              message="already failed permanently this run; not fetched again")
                trace["attempts"].append({"board": board["name"], "url": url, "outcome": "skipped",
                                          "reason": "repeat rule: same request already failed permanently this run",
                                          "time_utc": _utc_iso(), "elapsed_s": round(elapsed(), 3)})
                continue

            try:
                try:
                    result, entry = attempt(board, url, 1, "first attempt")
                except fetch.BoardFetchError as e:
                    if not e.retriable:
                        raise
                    retry_block = budget_reason(0)
                    if retry_block:
                        budget_hit = retry_block
                        record["retry_skipped"] = retry_block
                        raise
                    result, entry = attempt(board, url, 2, "retry after retriable %s" % e.kind)
                ids = parse(board["ats"], result["data"])
            except fetch.BoardFetchError as e:
                record.update(outcome="failed", kind=e.kind, status_code=e.status_code, message=str(e))
                if "retry_skipped" not in record:
                    failures.add(key)
                continue
            except InvalidBoardResponse as e:
                entry.update(outcome="invalid", message=str(e))
                record.update(outcome="failed", kind="invalid", status_code=result["status_code"],
                              message=str(e), raw_path=result["raw_path"])
                failures.add(key)
                continue

            record.update(outcome="ok", reused=False, posting_count=len(ids),
                          posting_ids=ids, raw_path=result["raw_path"])
            successes[key] = record
    except Exception as e:
        status = "error"
        error = "%s: %s" % (type(e).__name__, e)
        for b in trace["boards"]:
            if b["outcome"] == "in_progress":
                b.update(outcome="error", message=error)

    checked = [b for b in trace["boards"] if b["outcome"] in ("ok", "failed")]
    failed = [b for b in checked if b["outcome"] == "failed"]
    if status is None:
        if budget_hit:
            status, stop_reason = "budget-exhausted", budget_hit
        elif failed:
            status, stop_reason = "incomplete", "%d board(s) failed" % len(failed)
        else:
            status, stop_reason = "finished", "all planned boards checked successfully"
    else:
        stop_reason = error

    trace.update(
        status=status,
        stop_reason=stop_reason,
        boards_planned=len(boards),
        boards_checked=len(checked),
        boards_succeeded=len(checked) - len(failed),
        boards_failed=len(failed),
        requests_used=requests_used,
        elapsed_s=round(elapsed(), 3),
        finished_utc=_utc_iso(),
        policy_decisions=policy.DECISIONS[decisions_start:],
    )

    if write_trace:
        name = fetch.utc_stamp() + ("-%s" % label if label else "") + ".json"
        path = os.path.join(output_dir, "traces", name)
        body = json.dumps(trace, indent=2).encode("utf-8")
        decision = policy.write_bytes(path, body)
        trace["trace_path"] = path if decision is True else None
        trace["trace_write_decision"] = decision
    return trace
