"""Deliberately WRONG versions, so tests can prove they catch them.

JS1: two wrong versions of the rule, from JS1_CONTRACT.md, caught by
check_verdicts(). JS2: wrong versions W1-W11 from GATE.md section 6, caught
by the JS2 test suite (see the second half of this file). Never import any
of this from agent/.
"""

import contextlib
import json
import os
import tempfile
from pathlib import Path
from unittest import mock

from agent import loop, policy, rule


def misaligned_labels(postings, resume, target):
    """WRONG 1: verdicts computed in reverse order, zipped against postings.

    Each verdict is relabeled with the posting_id it is zipped against, so the
    id looks right; only the cited evidence gives the bug away.
    """
    verdicts = [rule.evaluate(p, resume, target) for p in reversed(postings)]
    return [dict(v, posting_id=p["id"]) for p, v in zip(postings, verdicts)]


def empty_justification(postings, resume, target):
    """WRONG 2: correct verdict label, but a justification citing nothing."""
    out = []
    for posting in postings:
        real = rule.evaluate(posting, resume, target)
        out.append({
            "posting_id": posting["id"],
            "verdict": real["verdict"],
            "failed_condition": real["failed_condition"],
            "citations": [],
            "justification": ["Strong ML fit."],
        })
    return out


# ---------------------------------------------------------------------------
# JS2: wrong versions W1-W11 from GATE.md section 6.
#
# Each is a context manager that patches ONE decision in agent/ for the
# duration of a `with` block, so tests/test_mutants.py can run the JS2 suite
# against it and show that the suite fails. Nothing here changes agent/ on
# disk, and every patch is undone when the block ends.
# ---------------------------------------------------------------------------

def _w1_budget_block(self, action):
    """WRONG: a limit is only noticed after it has been passed."""
    b = self.budgets
    if self.requests_sent > b["max_requests"]:
        return "max_requests"
    if self.elapsed() > b["max_run_seconds"]:
        return "max_run_seconds"
    return None


@contextlib.contextmanager
def W1_budget_checked_after():
    with mock.patch.object(loop.Runner, "_budget_block", _w1_budget_block):
        yield


@contextlib.contextmanager
def W2_retry_treated_as_repeat():
    """WRONG: the allowed second attempt is blocked as a repeat."""
    with mock.patch.object(loop.Runner, "_is_allowed_retry",
                           lambda self, action, key: False):
        yield


@contextlib.contextmanager
def W3_failed_board_reported_as_zero():
    with mock.patch.object(loop, "failed_board_new", lambda: 0):
        yield


@contextlib.contextmanager
def W4_failed_board_state_updated():
    def boards_to_save(self):
        return [b for b in self.boards if b["status"] in ("ok", "failed")]

    with mock.patch.object(loop.Runner, "_boards_to_save", boards_to_save):
        yield


@contextlib.contextmanager
def W5_finished_although_a_board_failed():
    def decide_exit(boards, budget_limit):
        return loop.BUDGET_EXHAUSTED if budget_limit else loop.FINISHED

    with mock.patch.object(loop, "decide_exit", decide_exit):
        yield


@contextlib.contextmanager
def W6_retries_a_404():
    def is_retryable(outcome):
        return bool(outcome) and outcome.get("kind") in (
            loop.RETRYABLE_KINDS | {"client_error"})

    with mock.patch.object(loop, "is_retryable", is_retryable):
        yield


@contextlib.contextmanager
def W7_host_check_ends_with():
    def host_allowed(host):
        return any(host.endswith(allowed) for allowed in policy.ALLOWED_HOSTS)

    with mock.patch.object(policy, "_host_allowed", host_allowed):
        yield


@contextlib.contextmanager
def W7_host_check_contains():
    def host_allowed(host):
        return any(allowed in host for allowed in policy.ALLOWED_HOSTS)

    with mock.patch.object(policy, "_host_allowed", host_allowed):
        yield


def _no_symlink_resolve(path, root):
    path = Path(path)
    if not path.is_absolute():
        path = Path(root) / path
    return Path(os.path.abspath(path))  # collapses "..", ignores symlinks


def _no_symlink_area(root, parts):
    return Path(os.path.abspath(Path(root).joinpath(*parts)))


def _string_prefix_inside(path, area):
    return str(path).startswith(str(area))


@contextlib.contextmanager
def W8_string_prefix_and_no_symlinks():
    with mock.patch.object(policy, "_resolve", _no_symlink_resolve), \
            mock.patch.object(policy, "_area", _no_symlink_area), \
            mock.patch.object(policy, "_inside", _string_prefix_inside):
        yield


@contextlib.contextmanager
def W8_string_prefix_only():
    with mock.patch.object(policy, "_inside", _string_prefix_inside):
        yield


@contextlib.contextmanager
def W8_symlinks_not_resolved_only():
    with mock.patch.object(policy, "_resolve", _no_symlink_resolve), \
            mock.patch.object(policy, "_area", _no_symlink_area):
        yield


@contextlib.contextmanager
def W9_approval_defaults_to_yes():
    def ask(approver, prompt):
        if approver is None:
            return "yes"
        try:
            return approver(prompt)
        except Exception:
            return "yes"

    with mock.patch.object(policy, "_ask", ask):
        yield


@contextlib.contextmanager
def W10_duplicate_posting_counted_twice():
    with mock.patch.object(loop, "dedupe",
                           lambda postings, on_duplicate: list(postings)):
        yield


@contextlib.contextmanager
def W11_budgets_json_differs_from_gate():
    """WRONG config: max_requests raised to 9 in a copy of budgets.json."""
    import test_budgets_config
    real = json.loads(test_budgets_config.BUDGETS_PATH.read_text())
    with tempfile.TemporaryDirectory() as tmp:
        wrong = Path(tmp) / "budgets.json"
        wrong.write_text(json.dumps(dict(real, max_requests=9)))
        with mock.patch.object(test_budgets_config, "BUDGETS_PATH", wrong):
            yield


# Mutant -> a test that must fail on it (the suite may fail more).
GATE_MUTANTS = {
    "W1": (W1_budget_checked_after,
           "test_max_requests_checked_before_the_request"),
    "W2": (W2_retry_treated_as_repeat,
           "test_timeout_retried_once_after_2_seconds"),
    "W3": (W3_failed_board_reported_as_zero,
           "test_failed_board_new_is_unknown_never_zero"),
    "W4": (W4_failed_board_state_updated,
           "test_failed_board_state_file_untouched"),
    "W5": (W5_finished_although_a_board_failed,
           "test_incomplete_exit_1_when_a_board_fails"),
    "W6": (W6_retries_a_404, "test_404_not_retried"),
    "W7-endswith": (W7_host_check_ends_with,
                    "test_extra_host_suffix_trick_refused"),
    "W7-contains": (W7_host_check_contains,
                    "test_B04_lookalike_host_refused_exact_match"),
    "W8": (W8_string_prefix_and_no_symlinks,
           "test_B11_prefix_trick_out_evil_refused"),
    "W8-prefix": (W8_string_prefix_only,
                  "test_B11_prefix_trick_out_evil_refused"),
    "W8-symlink": (W8_symlinks_not_resolved_only,
                   "test_B12_symlink_out_of_project_refused"),
    "W9": (W9_approval_defaults_to_yes,
           "test_B19_reset_with_no_one_to_answer_refused"),
    "W10": (W10_duplicate_posting_counted_twice,
            "test_duplicate_posting_ids_counted_once"),
    "W11": (W11_budgets_json_differs_from_gate,
            "test_W11_budgets_json_matches_gate_section_2"),
}
