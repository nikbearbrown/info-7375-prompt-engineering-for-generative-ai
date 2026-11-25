"""The loop: exits (GATE.md section 1), budgets (2), repeat rule (3), error policy (4), config (0).

Written by Claude Code (Claude Opus 5.5), 2026-11-10. Every run here is SEEDED: a fake transport
(tests/js2/js2kit.py) serving fixtures from fixtures/seeded/. Summaries carry "label": "SEEDED".
"""
import json
from datetime import timedelta

import pytest

import checks
from js2kit import (ASHBY, GH, JSON, LEVER_EU, NOW, THREE, FakeClock, SeededTransport, board, board_result,
                    ok, run_dir, run_loop, seeded, summary, three_ok_routes, trace, wd)  # noqa: F401
from jobwatch import cli
from jobwatch.tools import PolicyDenied, RepeatRefused, Tools
from jobwatch.policy import Policy


def state(workdir):
    return json.loads((workdir / "state" / "seen.json").read_text(encoding="utf-8"))


# --- the four exits ------------------------------------------------------------------------
def test_exit_finished_three_boards_two_systems_baseline(wd):
    t = SeededTransport(three_ok_routes())
    assert run_loop(t) == 0
    s = summary(wd)
    assert s["exit"] == "FINISHED" and s["exit_code"] == 0 and s["label"] == "SEEDED"
    assert {b["system"] for b in s["boards"]} == {"greenhouse", "lever", "ashby"}
    assert [(b["count"], b["new_ids"], b["baseline"]) for b in s["boards"]] == [(2, [], True), (6, [], True), (2, [], True)]
    assert sorted(state(wd)["boards"]) == ["ashby:seeded-ab", "greenhouse:seeded-gh", "lever:seeded-lv"]
    assert [r["method"] for r in t.requests] == ["GET"] * 3


def test_exit_finished_second_run_reports_new_posting_with_record_verdict(wd):
    assert run_loop(SeededTransport(three_ok_routes())) == 0
    routes = three_ok_routes()
    routes[GH.format("seeded-gh")] = ok(seeded("SEEDED_greenhouse_three_jobs.json"))
    later = NOW + timedelta(minutes=5)
    assert run_loop(SeededTransport(routes), now=later) == 0
    gh = board_result(summary(wd, later), "greenhouse:seeded-gh")
    assert gh["baseline"] is False and gh["new_ids"] == ["9000003"]
    (rec,) = gh["record"]
    assert rec["id"] == "9000003" and rec["verdict"] == "relevant"  # "AI Engineer", "Remote" in the persona targets
    assert "9000003" in state(wd)["boards"]["greenhouse:seeded-gh"]["seen_ids"]


def test_exit_incomplete_on_404_board_and_state_only_for_ok_boards(wd, capsys):
    checks.write_boards(wd, THREE + [board("greenhouse", "seeded-bad", "boards-api.greenhouse.io")])
    routes = three_ok_routes()
    routes[GH.format("seeded-bad")] = (404, seeded("SEEDED_greenhouse_404.json"), JSON)
    assert run_loop(SeededTransport(routes)) == 3
    s = summary(wd)
    assert s["exit"] == "INCOMPLETE" and s["state_updated"] is True
    assert "greenhouse:seeded-bad" not in state(wd)["boards"]
    err = capsys.readouterr().err.strip().splitlines()
    assert err == ["jobwatch: INCOMPLETE: failed boards: greenhouse:seeded-bad (http_404)"]


def test_exit_budget_exhausted_on_max_requests_state_not_updated(wd):
    budgets = json.loads((wd / "config" / "budgets.json").read_text(encoding="utf-8"))
    budgets["max_requests"] = 2
    (wd / "config" / "budgets.json").write_text(json.dumps(budgets), encoding="utf-8")
    t = SeededTransport(three_ok_routes())
    assert run_loop(t) == 4
    s = summary(wd)
    assert len(t.requests) == 2
    assert s["exit"] == "BUDGET_EXHAUSTED" and s["budget_exhausted"]["budget"] == "max_requests"
    assert s["budget_exhausted"]["board_in_progress"] == "ashby:seeded-ab"
    assert board_result(s, "ashby:seeded-ab")["count"] is None
    assert s["state_updated"] is False and not (wd / "state" / "seen.json").exists()


def test_exit_budget_exhausted_on_too_many_boards(wd):
    budgets = json.loads((wd / "config" / "budgets.json").read_text(encoding="utf-8"))
    budgets["max_boards"] = 2
    (wd / "config" / "budgets.json").write_text(json.dumps(budgets), encoding="utf-8")
    t = SeededTransport(three_ok_routes())
    assert run_loop(t) == 4
    s = summary(wd)
    assert len(t.requests) == 2 and s["budget_exhausted"]["budget"] == "max_boards"
    assert s["budget_exhausted"]["unvisited"] == ["ashby:seeded-ab"]
    assert board_result(s, "ashby:seeded-ab")["status"] == "UNVISITED"


def test_exit_budget_exhausted_on_max_seconds(wd):
    budgets = json.loads((wd / "config" / "budgets.json").read_text(encoding="utf-8"))
    budgets["max_seconds"] = 15
    (wd / "config" / "budgets.json").write_text(json.dumps(budgets), encoding="utf-8")
    clock = FakeClock()
    routes = three_ok_routes()
    routes[GH.format("seeded-gh")] = "timeout"
    t = SeededTransport(routes, clock=clock, timeout_cost=10)
    assert run_loop(t, clock=clock) == 4
    s = summary(wd)
    # gh: timeout at t=10, backoff to t=12 (< 15, so the retry is sent), timeout again at t=22.
    # The check before lever's first request sees 22 >= 15: lever is the board in progress.
    assert s["budget_exhausted"]["budget"] == "max_seconds"
    assert s["budget_exhausted"]["board_in_progress"] == "lever:seeded-lv"
    assert board_result(s, "greenhouse:seeded-gh")["reason"] == "timeout"
    assert board_result(s, "lever:seeded-lv")["reason"] == "budget"
    assert board_result(s, "ashby:seeded-ab")["status"] == "UNVISITED"
    assert len(t.requests) == 2


def test_exit_error_on_corrupt_state_before_any_fetch(wd):
    (wd / "state").mkdir()
    (wd / "state" / "seen.json").write_bytes(b"{not json")
    t = SeededTransport(three_ok_routes())
    assert run_loop(t) == 1
    s = summary(wd)
    assert t.requests == [] and s["exit"] == "ERROR" and s["needs_deepak"] is True
    assert "corrupt state" in s["error"]["error"]
    assert (wd / "state" / "seen.json").read_bytes() == b"{not json"


def test_exit_error_on_unknown_system(wd):
    checks.write_boards(wd, [board("workday", "x", "api.lever.co")])
    t = SeededTransport({})
    assert run_loop(t) == 1 and t.requests == []


def test_exit_code_and_summary_always_agree(wd):
    codes = {"FINISHED": 0, "ERROR": 1, "INCOMPLETE": 3, "BUDGET_EXHAUSTED": 4}
    assert run_loop(SeededTransport(three_ok_routes())) == codes[summary(wd)["exit"]]


def test_timeout_twice_board_failed_run_incomplete(wd):
    checks.check_timeout_twice_incomplete(wd)


# --- error policy (GATE.md section 4) ------------------------------------------------------
def test_404_board_counts_null_not_zero(wd):
    checks.check_failed_board_not_zero(wd)


def test_404_fetched_once_no_retry(wd):
    checks.check_404_not_retried(wd)


def test_429_not_retried_retry_after_recorded(wd):
    checks.write_boards(wd, [board("greenhouse", "seeded-gh", "boards-api.greenhouse.io")])
    t = SeededTransport({GH.format("seeded-gh"): (429, b"", {"Retry-After": "30"})})
    assert run_loop(t) == 3
    gh = board_result(summary(wd), "greenhouse:seeded-gh")
    assert len(t.requests) == 1 and gh["reason"] == "http_429" and gh["retry_after"] == "30"


def test_5xx_then_200_succeeds_after_one_retry_with_backoff(wd):
    checks.write_boards(wd, [board("greenhouse", "seeded-gh", "boards-api.greenhouse.io")])
    clock = FakeClock()
    t = SeededTransport({GH.format("seeded-gh"): [(503, b"", {}), ok(seeded("SEEDED_greenhouse_two_jobs.json"))]})
    assert run_loop(t, clock=clock) == 0
    gh = board_result(summary(wd), "greenhouse:seeded-gh")
    assert gh["status"] == "OK" and gh["retries_used"] == 1 and 2 in clock.sleeps


def test_html_200_is_failed_not_empty(wd):
    checks.check_html_200_fails(wd)


def test_html_body_with_json_content_type_is_failed(wd):
    checks.check_html_200_with_json_content_type_fails(wd)


def test_wrong_shape_failed_without_retry(wd):
    checks.write_boards(wd, [board("ashby", "seeded-ab", "api.ashbyhq.com")])
    t = SeededTransport({ASHBY.format("seeded-ab"): ok(seeded("SEEDED_wrong_shape.json"))})
    assert run_loop(t) == 3
    assert len(t.requests) == 1 and board_result(summary(wd), "ashby:seeded-ab")["reason"] == "wrong_shape"


def test_redirect_in_loop_is_failed_not_followed(wd):
    checks.write_boards(wd, [board("greenhouse", "seeded-gh", "boards-api.greenhouse.io")])
    t = SeededTransport({GH.format("seeded-gh"): (302, b"", {"Location": "https://evil.example.net/"})})
    assert run_loop(t) == 3
    assert [r["url"] for r in t.requests] == [GH.format("seeded-gh")]
    assert board_result(summary(wd), "greenhouse:seeded-gh")["reason"] == "redirect_refused"


def test_retries_count_against_max_requests(wd):
    checks.check_retries_counted(wd)


def test_same_host_spacing_is_kept(wd):
    checks.write_boards(wd, [board("greenhouse", "seeded-a", "boards-api.greenhouse.io"),
                             board("greenhouse", "seeded-b", "boards-api.greenhouse.io")])
    body = ok(seeded("SEEDED_greenhouse_two_jobs.json"))
    clock = FakeClock()
    assert run_loop(SeededTransport({GH.format("seeded-a"): body, GH.format("seeded-b"): body}), clock=clock) == 0
    assert clock.sleeps == [1]


# --- config (GATE.md section 0) ------------------------------------------------------------
def test_duplicate_board_is_error(wd):
    checks.check_duplicate_board_is_error(wd)


def test_host_system_mismatch_is_error(wd):
    checks.check_host_system_mismatch_is_error(wd)


def test_deliberate_failure_label_changes_nothing(wd):
    def run(label, now):
        boards = [board("greenhouse", "seeded-gh", "boards-api.greenhouse.io"),
                  board("greenhouse", "seeded-bad", "boards-api.greenhouse.io", **label)]
        checks.write_boards(wd, boards)
        routes = {GH.format("seeded-gh"): ok(seeded("SEEDED_greenhouse_two_jobs.json")),
                  GH.format("seeded-bad"): (404, seeded("SEEDED_greenhouse_404.json"), JSON)}
        t = SeededTransport(routes)
        code = run_loop(t, now=now)
        s = summary(wd, now)
        return code, [r["url"] for r in t.requests], [{k: v for k, v in b.items()} for b in s["boards"]], s["exit"]

    a = run({}, NOW)
    (wd / "state" / "seen.json").unlink()  # test cleanup between the two runs
    b = run({"deliberate_failure": True}, NOW + timedelta(minutes=1))
    assert a == b


def test_identity_ignores_host(wd):
    checks.check_identity_ignores_host(wd)


def test_no_command_line_flag_for_any_budget():
    parser = cli.build_js2_parser()
    loop_parser = parser._subparsers._group_actions[0].choices["loop"]
    flags = {o for a in loop_parser._actions for o in a.option_strings}
    assert flags == {"-h", "--help", "--config", "--interactive"}


# --- repeat rule (GATE.md section 3) -------------------------------------------------------
def test_repeat_identical_fetch_refused(wd):
    url = GH.format("seeded-gh")
    tools = Tools(Policy(wd, run_id="20261110T200000Z"),
                  transport=SeededTransport({url: (404, b"{}", JSON)}))
    tools.fetch_json(url)
    with pytest.raises(RepeatRefused):
        tools.fetch_json(url.replace("boards-api.greenhouse.io", "BOARDS-API.greenhouse.io:443"))


def test_repeat_third_fetch_refused_even_when_retryable(wd):
    url = GH.format("seeded-gh")
    tools = Tools(Policy(wd, run_id="20261110T200000Z"), transport=SeededTransport({url: (503, b"", {})}))
    tools.fetch_json(url)
    tools.fetch_json(url)
    with pytest.raises(RepeatRefused):
        tools.fetch_json(url)


def test_repeat_second_write_same_path_refused(wd):
    tools = Tools(Policy(wd, run_id="20261110T200000Z"), transport=SeededTransport({}))
    tools.write_file("runs/20261110T200000Z/raw/a.body", b"1")
    with pytest.raises(RepeatRefused):
        tools.write_file("runs/20261110T200000Z/raw/a.body", b"2")


def test_append_mode_only_for_trace(wd):
    tools = Tools(Policy(wd, run_id="20261110T200000Z"), transport=SeededTransport({}))
    with pytest.raises(PolicyDenied):
        tools.write_file("runs/20261110T200000Z/summary.json", b"x", mode="append")


def test_run_dir_already_holding_a_run_is_not_overwritten(wd):
    assert run_loop(SeededTransport(three_ok_routes())) == 0
    before = (run_dir(wd) / "summary.json").read_bytes()
    assert run_loop(SeededTransport(three_ok_routes())) == 1
    assert (run_dir(wd) / "summary.json").read_bytes() == before


# --- the record of observations ------------------------------------------------------------
def test_trace_has_one_line_per_action_with_required_fields(wd):
    checks.write_boards(wd, THREE + [board("greenhouse", "seeded-bad", "boards-api.greenhouse.io")])
    routes = three_ok_routes()
    routes[GH.format("seeded-bad")] = (404, seeded("SEEDED_greenhouse_404.json"), JSON)
    run_loop(SeededTransport(routes))
    lines = trace(wd)
    for line in lines:
        assert {"ts", "step", "tool", "args", "policy", "http_status", "bytes", "sha256", "outcome"} <= set(line)
        assert line["label"] == "SEEDED"
    assert [line["step"] for line in lines] == list(range(1, len(lines) + 1))
    fetches = [line for line in lines if line["tool"] == "fetch_json"]
    assert len(fetches) == 4 and all(f["policy"] == "ALLOW" for f in fetches)
    assert any(f["http_status"] == 404 for f in fetches)
    assert (run_dir(wd) / "trace.md").read_text(encoding="utf-8").startswith("# Trace of run")


def test_manifest_sha256_matches_raw_bytes(wd):
    import hashlib

    run_loop(SeededTransport(three_ok_routes()))
    m = json.loads((run_dir(wd) / "manifest.json").read_text(encoding="utf-8"))
    for f in m["files"]:
        assert hashlib.sha256((run_dir(wd) / f["path"]).read_bytes()).hexdigest() == f["sha256"]
    assert len(m["files"]) == 3


def test_loop_replay_matches(wd, capsys):
    checks.write_boards(wd, THREE + [board("greenhouse", "seeded-bad", "boards-api.greenhouse.io")])
    routes = three_ok_routes()
    routes[GH.format("seeded-bad")] = (404, seeded("SEEDED_greenhouse_404.json"), JSON)
    run_loop(SeededTransport(routes))
    assert cli.main(["replay", f"runs/{NOW.strftime('%Y%m%dT%H%M%SZ')}"]) == 0


def test_loop_replay_detects_tampered_summary(wd):
    run_loop(SeededTransport(three_ok_routes()))
    p = run_dir(wd) / "summary.json"
    s = json.loads(p.read_text(encoding="utf-8"))
    s["boards"][0]["count"] = 99
    p.write_text(json.dumps(s), encoding="utf-8")
    assert cli.main(["replay", f"runs/{NOW.strftime('%Y%m%dT%H%M%SZ')}"]) == 1


def test_real_capture_bodies_parse(wd):
    """The providers parse the real 2026-11-10 capture (not SEEDED) to the counts in CAPTURE.md."""
    from js2kit import CAPTURE
    from jobwatch.providers import ashby, greenhouse, lever
    from jobwatch.tools import FetchResult

    def parse(mod, name, ct):
        return mod.parse(FetchResult("u", 200, {"content-type": ct}, (CAPTURE / name).read_bytes()), "k")

    assert len(parse(greenhouse, "01-greenhouse-stripe.body", "application/json")) == 776
    assert len(parse(lever, "03-lever-us-lever.body", "application/json; charset=utf-8")) == 0
    assert len(parse(lever, "04-lever-eu-lever.body", "application/json; charset=utf-8")) == 6
    assert len(parse(lever, "05-lever-us-palantir.body", "application/json; charset=utf-8")) == 304
    assert len(parse(ashby, "06-ashby-linear.body", "application/json; charset=utf-8")) == 33
    assert len(parse(ashby, "07-ashby-notion.body", "application/json; charset=utf-8")) == 152
    bad = greenhouse.parse(FetchResult("u", 404, {"content-type": "application/json"},
                                       (CAPTURE / "02-greenhouse-stripe-js2-nonexistent.body").read_bytes()), "k")
    assert bad.kind == "http_404"
