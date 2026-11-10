"""Plausible-but-wrong versions from GATE.md section 6, one per entry.

Each WRONG[n] replaces exactly one decision function in jobloop with a faulty one. They are
never used by the real loop; tests/test_wrong_versions.py applies each one in turn and shows
that a test fails against it (and passes against the real code). Use `applied(n)`.
"""
from __future__ import annotations

from contextlib import contextmanager
from dataclasses import dataclass
from typing import Callable
from unittest import mock

from jobloop import loop, policy, state


@dataclass(frozen=True)
class WrongVersion:
    number: int
    gate_text: str
    module: object
    name: str
    replacement: Callable


def _w1_classify(provider, board, resp):
    kind, detail, postings = _real_classify(provider, board, resp)
    if kind == "empty":
        return "ok", "HTTP 200, 0 postings", []          # WRONG: empty board treated as a normal observation
    return kind, detail, postings


def _w2_classify(provider, board, resp):
    if resp.status == 404:
        return "ok", "HTTP 404 treated as an empty board", []   # WRONG: an error becomes []
    return _real_classify(provider, board, resp)


def _w3_overall(outcomes, budget_hit, interrupted):
    if budget_hit:
        return loop.BUDGET_EXHAUSTED
    # WRONG: "most boards worked" counts as finished; the failure disappears from the exit.
    good = sum(o["outcome"] == loop.OBSERVED for o in outcomes)
    return loop.FINISHED if good >= 3 or good == len(outcomes) else loop.INCOMPLETE


def _w4_retry(kind, retries_used, budget):
    return kind in ("transient", "failed") and retries_used < 3     # WRONG: retries 404s, more than once


def _w5_count(run, got_response):
    if got_response:                                               # WRONG: failures cost nothing
        run.attempts_used += 1


def _w6_timeout(budget, remaining):
    return budget.request_timeout                                  # WRONG: ignores the remaining run time


def _w7_not_observed(b, reason):
    return {"outcome": loop.OBSERVED, "reason": reason, "postings": []}   # WRONG: unvisited looks like 0 jobs


def _w8_validate(cfg, budget):
    boards = cfg["boards"]                                         # WRONG: no duplicate (or any) check
    for b in boards:
        b["url"] = loop.providers.endpoint(b["provider"], b["board"])
    return boards


def _w9_state_allowed(status):
    return True                                                    # WRONG: any run may write state


def _w10_board_key(provider, board):
    return "all/boards"                                            # WRONG: ids from every board share one set


def _w13_fetch_once(method, url, allowed, transport, timeout):
    resp = transport(url, timeout)                                 # WRONG: follows the redirect unchecked
    if 300 <= resp.status < 400 and resp.headers.get("location"):
        return transport(resp.headers["location"], timeout)
    return resp


def _w16_mode(replay):
    return loop.LIVE                                               # WRONG: replays labeled as live


def _w11_check_write(path, *, root=policy.PROJECT_ROOT, approve_state_write=False, run_status=""):
    text = str(path)                                               # WRONG: string-prefix containment
    if text.startswith("runs") or text.startswith("tests/tmp"):
        return policy.Decision(policy.ALLOW, "prefix match")
    return _real_check_write(path, root=root, approve_state_write=approve_state_write, run_status=run_status)


def _w12_check_request(method, url, allowed_endpoints):
    from urllib.parse import urlsplit                              # WRONG: substring host match
    host = urlsplit(url).hostname or ""
    if method == "GET" and any(h in host for h in policy.ALLOWED_HOSTS):
        return policy.Decision(policy.ALLOW, "host contains an allowed name")
    return policy.Decision(policy.DENY, "not allowed")


def _w14_check_request(method, url, allowed_endpoints):
    return _real_check_request("GET", url, allowed_endpoints)      # WRONG: any method allowed if GET would be


def _w15_check_write(path, *, root=policy.PROJECT_ROOT, approve_state_write=False, run_status=""):
    # WRONG: the state write needs approval only "in spirit": no flag check, any status.
    if str(path).startswith("state/"):
        return policy.Decision(policy.ALLOW, "state write")
    return _real_check_write(path, root=root, approve_state_write=approve_state_write, run_status=run_status)


_real_classify = loop.classify_response
_real_check_write = policy.check_write
_real_check_request = policy.check_request

WRONG = {w.number: w for w in [
    WrongVersion(1, "A valid empty response becomes 'no new jobs' and finished.", loop, "classify_response", _w1_classify),
    WrongVersion(2, "A 404 is converted to a successful empty board.", loop, "classify_response", _w2_classify),
    WrongVersion(3, "Three successful boards hide the deliberate failure in the overall exit.", loop, "overall_status", _w3_overall),
    WrongVersion(4, "A retry loop repeats a 404 or exceeds one retry.", loop, "retry_allowed", _w4_retry),
    WrongVersion(5, "Failed attempts or retries are omitted from the request budget.", loop, "count_attempt", _w5_count),
    WrongVersion(6, "A timeout or delay extends beyond the remaining work budget.", loop, "request_timeout", _w6_timeout),
    WrongVersion(7, "An unvisited board is reported as having no new jobs.", loop, "not_observed_outcome", _w7_not_observed),
    WrongVersion(8, "Duplicate configuration entries fetch the same board twice.", loop, "validate_config", _w8_validate),
    WrongVersion(9, "A failed or incomplete run changes persistent seen IDs.", loop, "state_update_allowed", _w9_state_allowed),
    WrongVersion(10, "Posting IDs from different providers or boards collide.", loop, "board_key", _w10_board_key),
    WrongVersion(11, "A prefix path check permits runs-evil, .., or a symlink escape.", policy, "check_write", _w11_check_write),
    WrongVersion(12, "A substring host check permits boards-api.greenhouse.io.evil.example.", policy, "check_request", _w12_check_request),
    WrongVersion(13, "An allowed initial URL redirects to a disallowed destination.", loop, "fetch_once", _w13_fetch_once),
    WrongVersion(14, "A network write is allowed because a network read was allowed.", policy, "check_request", _w14_check_request),
    WrongVersion(15, "A state write happens without approval, or text supplied by the model grants approval.", policy, "check_write", _w15_check_write),
    WrongVersion(16, "A seeded replay is presented as a live observation.", loop, "mode_label", _w16_mode),
]}


@contextmanager
def applied(number: int):
    w = WRONG[number]
    with mock.patch.object(w.module, w.name, w.replacement):
        yield w
