"""GATE.md 'Wrong versions' as code: plausible implementations that must NOT pass.

Each function replaces one piece of the agent. tests/test_wrong_versions_caught.py
swaps it in and checks that the named tests fail. The numbering follows GATE.md.

WV1 has two halves. The 404 half ("a 404 becomes no new postings") is below. The
empty-list half ("an empty jobs list becomes no new postings") is NOT here on purpose:
the student writes that test first, for the review packet.
"""

import http.client
from urllib.parse import urlsplit

from jobwatch import net, policy, state
from jobwatch.errors import PolicyDenied


# WV1 (404 half): a board that answered 404 (or any non-200) is read as a board with
# no postings, so the loop reports "no new postings".
def classify_non_200_as_no_postings(board, response):
    if response.status != 200:
        return "usable", [], None
    return _REAL_CLASSIFY(board, response)


# WV2: a partial run advances state.
def may_advance_state_even_when_incomplete(status):
    return status in ("finished", "incomplete")


# WV3: a duplicate board sends a second request ...
def unique_boards_without_dedupe(requested):
    return [name.strip().lower() for name in requested], []


# ... the request cap is exceeded (checked with > instead of >=) ...
def budget_stop_off_by_one(used, budget, now, run_deadline):
    if used["boards"] > budget.max_boards:
        return "boards"
    if used["requests"] > budget.max_requests:
        return "requests"
    if now >= run_deadline:
        return "seconds"
    return None


# ... or work continues after the deadline.
def budget_stop_ignoring_time(used, budget, now, run_deadline):
    if used["boards"] >= budget.max_boards:
        return "boards"
    if used["requests"] >= budget.max_requests:
        return "requests"
    return None


# WV4: a key from one board suppresses a posting from another ...
def new_keys_with_one_global_seen_set(current_state, board_name, keys):
    if current_state is None or board_name not in current_state["boards"]:
        return None
    seen_anywhere = {k for b in current_state["boards"].values() for k in b["seen"]}
    return [k for k in keys if k not in seen_anywhere]


# ... or a returning posting is marked new (history replaced by the latest snapshot).
_REAL_ADVANCED = state.advanced


def advanced_keeping_only_the_latest_snapshot(current_state, run_id, finished_at, snapshots):
    after = _REAL_ADVANCED(current_state, run_id, finished_at, snapshots)
    for name, (_ats, _slug, keys) in snapshots.items():
        after["boards"][name]["seen"] = {k: after["boards"][name]["seen"][k] for k in keys}
    return after


# WV5: a write is allowed because a read of the same file was allowed.
_REAL_CHECK_FILE = policy.Policy.check_file


def check_file_write_allowed_if_readable(self, operation, path):
    if operation == "write":
        try:
            return _REAL_CHECK_FILE(self, "read", path)
        except PolicyDenied:
            pass
    return _REAL_CHECK_FILE(self, operation, path)


# WV6: an off-list host gets through (a string-prefix test on the URL) ...
def check_request_by_url_prefix(self, method, url):
    if method != "GET":
        raise PolicyDenied("method", f"{method} is not GET")
    if not any(url.startswith(f"https://{host}") for host in policy.ALLOWED_HOSTS):
        raise PolicyDenied("host", url)


# ... a POST to an allowed host gets through ...
_REAL_CHECK_REQUEST = policy.Policy.check_request


def check_request_ignoring_method(self, method, url):
    return _REAL_CHECK_REQUEST(self, "GET", url)


# ... a redirect gets through (the transport follows Location, as urllib does by default) ...
_REAL_HTTPS_GET = net.https_get


def https_get_following_redirects(url, deadline, *, clock=None, connection_factory=None):
    connection_factory = connection_factory or http.client.HTTPSConnection
    for _ in range(5):
        response = _REAL_HTTPS_GET(url, deadline, clock=clock, connection_factory=connection_factory)
        if 300 <= response.status < 400 and response.location:
            url = response.location
            if urlsplit(url).scheme != "https":
                break
            continue
        return response
    return response


# ... a path through `..` gets through (resolved, never refused by its parts) ...
def no_parent_part_check(path):
    return False


# ... `runs-evil/` gets through (containment by string prefix) ...
def inside_by_string_prefix(path, folder):
    return str(path).startswith(str(folder))


# ... or a symlink gets through.
def no_symlink_check(root, full):
    return None


from jobwatch import loop as _loop  # noqa: E402  (imported late so the agent's modules load first)

_REAL_CLASSIFY = _loop.classify_response

ALL = {
    "WV1 a 404 becomes no new postings": ("jobwatch.loop.classify_response", classify_non_200_as_no_postings),
    "WV2 partial run advances state": ("jobwatch.loop.may_advance_state", may_advance_state_even_when_incomplete),
    "WV3 duplicate board fetched twice": ("jobwatch.loop.unique_boards", unique_boards_without_dedupe),
    "WV3 request cap exceeded": ("jobwatch.loop.budget_stop", budget_stop_off_by_one),
    "WV3 work continues after the deadline": ("jobwatch.loop.budget_stop", budget_stop_ignoring_time),
    "WV4 key from one board suppresses another": ("jobwatch.state.new_keys", new_keys_with_one_global_seen_set),
    "WV4 returning posting marked new": ("jobwatch.state.advanced", advanced_keeping_only_the_latest_snapshot),
    "WV5 write allowed because read allowed": ("jobwatch.policy.Policy.check_file", check_file_write_allowed_if_readable),
    "WV6 off-list host via URL prefix": ("jobwatch.policy.Policy.check_request", check_request_by_url_prefix),
    "WV6 POST to an allowed host": ("jobwatch.policy.Policy.check_request", check_request_ignoring_method),
    "WV6 redirect followed": ("jobwatch.net.https_get", https_get_following_redirects),
    "WV6 path through ..": ("jobwatch.policy._has_parent_part", no_parent_part_check),
    "WV6 look-alike folder by string prefix": ("jobwatch.policy._inside", inside_by_string_prefix),
    "WV6 symlink": ("jobwatch.policy._symlink_in_path", no_symlink_check),
}

# Tests each wrong version must fail (by unittest name).
CAUGHT_BY = {
    "WV1 a 404 becomes no new postings": [
        "tests.test_loop.ExitTest.test_a_failed_normal_board_makes_the_run_incomplete_and_its_count_unknown",
        "tests.test_loop.ExitTest.test_the_failure_run_is_incomplete_and_leaves_the_state_byte_identical"],
    "WV2 partial run advances state": [
        "tests.test_loop.ExitTest.test_the_failure_run_is_incomplete_and_leaves_the_state_byte_identical"],
    "WV3 duplicate board fetched twice": [
        "tests.test_loop.RepeatRuleTest.test_a_board_listed_twice_is_fetched_once"],
    "WV3 request cap exceeded": [
        "tests.test_loop.BudgetTest.test_the_request_budget_stops_the_loop",
        "tests.test_loop.BudgetTest.test_a_board_past_the_board_budget_is_not_checked"],
    "WV3 work continues after the deadline": [
        "tests.test_loop.BudgetTest.test_no_request_starts_once_the_run_deadline_has_passed"],
    "WV4 key from one board suppresses another": [
        "tests.test_loop.HistoryTest.test_the_same_key_on_another_board_is_new_there",
        "tests.test_state.NewKeysTest.test_a_key_seen_on_another_board_is_still_new_here"],
    "WV4 returning posting marked new": [
        "tests.test_loop.HistoryTest.test_a_posting_that_disappears_and_returns_is_not_new"],
    "WV5 write allowed because read allowed": [
        "tests.test_policy.FileCasesTest.test_F10_a_state_write_without_approval_is_refused",
        "tests.test_policy.FileCasesTest.test_X2_reading_a_file_does_not_allow_writing_it"],
    "WV6 off-list host via URL prefix": [
        "tests.test_policy.RequestCasesTest.test_N7_an_unconfigured_board_on_an_allowed_host_is_refused",
        "tests.test_policy.RequestCasesTest.test_X10_an_allowed_name_before_an_at_sign_is_not_the_host",
        "tests.test_policy.RequestCasesTest.test_X11_an_allowed_name_as_a_prefix_of_another_host_is_refused"],
    "WV6 POST to an allowed host": [
        "tests.test_policy.RequestCasesTest.test_N2_a_post_to_the_same_address_is_refused"],
    "WV6 redirect followed": [
        "tests.test_net.HttpsGetTest.test_a_redirect_is_returned_and_not_followed"],
    "WV6 path through ..": [
        "tests.test_policy.FileCasesTest.test_X1_dot_dot_is_refused_even_when_it_lands_in_the_current_run"],
    "WV6 look-alike folder by string prefix": [
        "tests.test_policy.FileCasesTest.test_X13_a_look_alike_of_the_current_run_folder_is_refused",
        "tests.test_policy.FileCasesTest.test_X14_reading_from_a_look_alike_of_runs_is_refused"],
    "WV6 symlink": [
        "tests.test_policy.FileCasesTest.test_F8_a_symlink_that_leads_outside_is_refused",
        "tests.test_policy.FileCasesTest.test_F9_a_symlink_is_refused_even_when_it_points_inside"],
}

assert set(ALL) == set(CAUGHT_BY)
