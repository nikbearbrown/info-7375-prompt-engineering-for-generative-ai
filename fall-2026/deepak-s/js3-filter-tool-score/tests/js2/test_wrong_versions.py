"""Wrong versions W01-W14 from GATE.md section 6: each test patches in the wrong implementation and
shows that the check which guards it fails. The catch is demonstrated, not claimed.

Written by Claude Code (Claude Opus 5.5), 2026-11-10. The wrong implementations below are
Claude Code's versions of Deepak's one-line descriptions in GATE.md section 6. SEEDED inputs only.
"""
import json
import os
import re
import urllib.request

import pytest

import checks
from js2kit import wd  # noqa: F401
from jobwatch import loop as L
from jobwatch import policy as P
from jobwatch import tools as T
from jobwatch import verify as V
from jobwatch.providers import BoardError, greenhouse, lever


def caught(check, *args):
    with pytest.raises(AssertionError):
        check(*args)


def test_W01_startswith_path_check_is_caught_by_B08(wd, monkeypatch):
    monkeypatch.setattr(P, "is_within", lambda path, base: path.startswith(base))
    caught(checks.check_B08, wd)


def test_W02_substring_host_check_is_caught_by_B02(wd, monkeypatch):
    monkeypatch.setattr(P, "host_allowed", lambda host: any(h in host for h in P.HOST_SYSTEM))
    caught(checks.check_B02, wd)


def test_W03_host_from_raw_string_is_caught_by_B03(wd, monkeypatch):
    def raw_string_parse(url):
        m = re.match(r"^([a-zA-Z]+)://([a-zA-Z0-9.-]+)(?::(\d+))?", url)
        return P.UrlTarget(m.group(1).lower(), False, m.group(2).lower(), int(m.group(3)) if m.group(3) else None)

    monkeypatch.setattr(P, "parse_url", raw_string_parse)
    caught(checks.check_B03, wd)


def test_W04_following_redirects_is_caught_by_B06(wd, monkeypatch):
    monkeypatch.setattr(T, "REDIRECT_HANDLER", urllib.request.HTTPRedirectHandler)
    caught(checks.check_B06, wd)


def test_W05_path_check_without_realpath_is_caught_by_B09(wd, monkeypatch):
    monkeypatch.setattr(P, "resolve", lambda path, root: os.path.abspath(os.path.join(root, path)))
    caught(checks.check_B09, wd)


def test_W06_failed_board_counted_as_zero_new_is_caught(wd, monkeypatch):
    real = L.failed_result

    def zero(base, reason, err, retries):
        return {**real(base, reason, err, retries), "count": 0, "new_ids": []}

    monkeypatch.setattr(L, "failed_result", zero)
    caught(checks.check_failed_board_not_zero, wd)


def test_W07_timeout_reported_as_finished_is_caught(wd, monkeypatch):
    monkeypatch.setattr(L, "decide_exit", lambda results, budget_hit, error:
                        L.ERROR if error else L.BUDGET_EXHAUSTED if budget_hit else L.FINISHED)
    caught(checks.check_timeout_twice_incomplete, wd)


def test_W08_retries_not_counted_is_caught(wd, monkeypatch):
    def count_first_attempts_only(self, is_retry):
        if not is_retry:
            self.requests += 1

    monkeypatch.setattr(L.Budget, "note_request", count_first_attempts_only)
    caught(checks.check_retries_counted, wd)


def test_W09_retrying_a_404_is_caught(wd, monkeypatch):
    real = greenhouse.classify_http

    def retry_4xx(result):
        r = real(result)
        if isinstance(r, BoardError) and r.http_status and 400 <= r.http_status < 500:
            return BoardError(r.kind, True, r.detail, r.http_status, r.retry_after)
        return r

    monkeypatch.setattr(greenhouse, "classify_http", retry_4xx)
    caught(checks.check_404_not_retried, wd)


def test_W10_lever_html_parsed_as_empty_list_is_caught(wd, monkeypatch):
    def lenient(result, board):
        try:
            data = json.loads(result.body)
        except ValueError:
            return []
        return lever.build_postings(data, board, lever._fields)

    monkeypatch.setattr(lever, "parse", lenient)
    caught(checks.check_html_200_fails, wd)


def test_W11_empty_200_with_no_independent_check_is_caught(wd, monkeypatch, capsys):
    monkeypatch.setattr(V, "suspect_check", lambda prior_count, count: False)
    caught(checks.check_verify_flags_suspect, wd, capsys)


def test_W12_host_in_board_identity_is_caught(wd, monkeypatch):
    monkeypatch.setattr(L, "board_key", lambda b: f"{b['system']}:{b['slug']}@{b['host']}")
    caught(checks.check_identity_ignores_host, wd)


def test_W13_duplicate_board_accepted_is_caught(wd, monkeypatch):
    monkeypatch.setattr(L, "check_duplicates", lambda boards: None)
    caught(checks.check_duplicate_board_is_error, wd)


def test_W14_host_not_checked_against_system_is_caught(wd, monkeypatch):
    monkeypatch.setattr(L, "check_host_system", lambda board: None)
    caught(checks.check_host_system_mismatch_is_error, wd)
