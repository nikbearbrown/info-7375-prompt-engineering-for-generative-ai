
import json

import httpx

from agent.loop import run_loop
from agent.policy import make_client, state_path
from check_run import check_run

GH = "https://boards-api.greenhouse.io/v1/boards/{}/jobs?content=true"


def board(name):
    return {
        "key": f"greenhouse:{name}",
        "system": "greenhouse",
        "url": GH.format(name),
    }


def jobs(*ids):
    return {
        "jobs": [
            {
                "id": i,
                "title": f"Job {i}",
                "location": {"name": "Remote"},
                "content": "x",
            }
            for i in ids
        ],
        "meta": {"total": len(ids)},
    }


def fake_net(routes):
    """routes: board name -> a JSON body (200) or an int status code.
    Returns a policy client and a list of every URL actually sent."""
    sent = []

    def handler(request):
        sent.append(str(request.url))
        name = request.url.path.split("/")[3]
        r = routes[name]
        return (
            httpx.Response(r)
            if isinstance(r, int)
            else httpx.Response(200, json=r)
        )

    return make_client(transport=httpx.MockTransport(handler)), sent


def project(tmp_path):
    for d in ("out", "evidence", "data", "config"):
        (tmp_path / d).mkdir()
    return tmp_path


NO_SLEEP = lambda seconds: None


# ---------- Exits ----------

def test_all_boards_ok_is_finished(tmp_path):
    root = project(tmp_path)
    client, sent = fake_net({"a": jobs(1, 2), "b": jobs(3)})
    s = run_loop([board("a"), board("b")], root, client, sleep=NO_SLEEP)

    assert s["status"] == "finished"
    assert s["exit_code"] == 0


def test_failed_board_makes_run_incomplete_not_finished(tmp_path):
    root = project(tmp_path)
    client, sent = fake_net({"a": jobs(1), "bad": 404})
    s = run_loop([board("a"), board("bad")], root, client, sleep=NO_SLEEP)
    bad = s["boards"]["greenhouse:bad"]

    assert s["status"] == "incomplete"
    assert s["exit_code"] == 1
    assert bad["status"] == "failed"
    assert bad["reason"] == "bad_board"
    assert bad["postings"] is None


# ---------- Error policy ----------

def test_no_retry_on_404(tmp_path):
    root = project(tmp_path)
    client, sent = fake_net({"bad": 404})
    run_loop([board("bad")], root, client, sleep=NO_SLEEP)

    assert len(sent) == 1


def test_retry_once_on_5xx_then_fail(tmp_path):
    root = project(tmp_path)
    waits = []
    client, sent = fake_net({"flaky": 500})
    s = run_loop([board("flaky")], root, client, sleep=waits.append)

    assert len(sent) == 2
    assert waits == [2]
    assert s["boards"]["greenhouse:flaky"]["status"] == "failed"
    assert s["boards"]["greenhouse:flaky"]["reason"] == "unreachable"


# ---------- Budgets ----------

def test_request_budget_stops_before_sending(tmp_path):
    root = project(tmp_path)
    client, sent = fake_net({"a": jobs(1), "b": jobs(2)})
    s = run_loop(
        [board("a"), board("b")],
        root,
        client,
        budgets={"max_requests": 1},
        sleep=NO_SLEEP,
    )

    assert len(sent) == 1
    assert s["status"] == "budget-exhausted"
    assert s["exit_code"] == 2
    assert s["boards"]["greenhouse:b"]["status"] == "not_attempted"


def test_retry_not_sent_when_budget_runs_out(tmp_path):
    root = project(tmp_path)
    client, sent = fake_net({"flaky": 500})
    s = run_loop(
        [board("flaky")],
        root,
        client,
        budgets={"max_requests": 1},
        sleep=NO_SLEEP,
    )

    assert len(sent) == 1
    assert s["boards"]["greenhouse:flaky"]["reason"] == "retry_not_sent_budget"
    assert s["status"] == "budget-exhausted"


def test_time_budget_stops_before_sending(tmp_path):
    root = project(tmp_path)
    client, sent = fake_net({"a": jobs(1)})
    s = run_loop(
        [board("a")],
        root,
        client,
        budgets={"max_seconds": 0},
        sleep=NO_SLEEP,
    )

    assert sent == []
    assert s["status"] == "budget-exhausted"


# ---------- Repeat rule ----------

def test_duplicate_board_is_repeat_blocked(tmp_path):
    root = project(tmp_path)
    client, sent = fake_net({"a": jobs(1)})
    s = run_loop(
        [board("a"), board("a")],
        root,
        client,
        sleep=NO_SLEEP,
    )

    assert len(sent) == 1
    trace = (s["run_dir"] / "trace.jsonl").read_text()
    assert "repeat_blocked" in trace


# ---------- State ----------

def test_state_not_advanced_for_failed_board(tmp_path):
    root = project(tmp_path)
    p = state_path("greenhouse:bad", root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"seen_ids": ["greenhouse:bad:1"]}))
    before = p.read_text()

    client, sent = fake_net({"bad": 404})
    run_loop([board("bad")], root, client, sleep=NO_SLEEP)

    assert p.read_text() == before


def test_baseline_then_only_new_ids_and_no_collision_across_boards(tmp_path):
    root = project(tmp_path)

    # Run 1: both boards have id 1 -> baseline, nothing new
    client, _ = fake_net({"a": jobs(1), "b": jobs(1)})
    s1 = run_loop(
        [board("a"), board("b")],
        root,
        client,
        sleep=NO_SLEEP,
    )

    assert s1["boards"]["greenhouse:a"]["new"] == []
    assert s1["boards"]["greenhouse:b"]["new"] == []

    # Run 2: only board a gets a new id 2
    client, _ = fake_net({"a": jobs(1, 2), "b": jobs(1)})
    s2 = run_loop(
        [board("a"), board("b")],
        root,
        client,
        sleep=NO_SLEEP,
    )

    assert len(s2["boards"]["greenhouse:a"]["new"]) == 1
    assert s2["boards"]["greenhouse:b"]["new"] == []


# ---------- Evidence ----------

def test_raw_response_and_trace_are_saved(tmp_path):
    root = project(tmp_path)
    client, sent = fake_net({"a": jobs(1)})
    s = run_loop([board("a")], root, client, sleep=NO_SLEEP)
    run_dir = s["run_dir"]

    assert run_dir.resolve().is_relative_to(
        (root / "out" / "runs").resolve()
    )
    assert list((run_dir / "raw").iterdir())
    trace = run_dir / "trace.jsonl"
    assert trace.exists()
    assert trace.read_text().strip()


# ---------- Independent check (finished but wrong) ----------

def test_checker_flags_empty_board_that_loop_called_finished(tmp_path):
    root = project(tmp_path)
    client, sent = fake_net({"a": jobs()})
    s = run_loop([board("a")], root, client, sleep=NO_SLEEP)

    assert s["status"] == "finished"

    problems = check_run(s["run_dir"])
    assert len(problems) == 1
    assert "greenhouse:a" in str(problems[0])


def test_checker_finds_nothing_on_normal_board(tmp_path):
    root = project(tmp_path)
    client, sent = fake_net({"a": jobs(1, 2)})
    s = run_loop([board("a")], root, client, sleep=NO_SLEEP)

    assert check_run(s["run_dir"]) == []
