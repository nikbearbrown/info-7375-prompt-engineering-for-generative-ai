"""Exits, budgets and the error policy from GATE.md, with fake fetches (CONSTRUCTED responses)."""
import shutil

import pytest

from conftest import ROOT, ashby_board, greenhouse_board
from jsagent import loop, net
from jsagent.policy import Policy

GH = {"system": "greenhouse", "board": "anthropic"}
NO = {"system": "ashby", "board": "notion"}
PX = {"system": "ashby", "board": "perplexity"}


@pytest.fixture
def where(tmp_path):
    run_dir = ROOT / "runs" / f"pytest-{tmp_path.name}"
    state = ROOT / "runs" / f"pytest-state-{tmp_path.name}" / "seen.json"
    yield run_dir, state
    for d in (ROOT / "runs").glob(f"pytest-*{tmp_path.name}*"):
        shutil.rmtree(d, ignore_errors=True)


def fetcher(responses, calls=None):
    """responses: url-substring -> bytes, or an exception to raise (or a list, one per call)."""
    def fetch(policy, url, timeout):
        policy.check_request("GET", url)
        if calls is not None:
            calls.append(url)
        for k, v in responses.items():
            if k in url:
                v = v.pop(0) if isinstance(v, list) else v
                if isinstance(v, Exception):
                    raise v
                return v
        raise AssertionError(f"unexpected url {url}")
    return fetch


def go(where, resume, boards, responses, calls=None, **kw):
    run_dir, state = where
    n = kw.pop("n", "")
    return loop.run(boards, resume, Policy(ROOT), state, run_dir.with_name(run_dir.name + n), use_claude=False,
                    fetch=fetcher(responses, calls), sleep=lambda s: None, **kw)


OK = {"anthropic": greenhouse_board((1, "AI Engineer", "<p>Python</p>")),
      "notion": ashby_board(("n1", "Data Engineer", "SQL")),
      "perplexity": ashby_board(("p1", "Recruiter", "people"))}


def test_finished_when_every_board_ok(where, resume):
    out = go(where, resume, [GH, NO, PX], dict(OK))
    assert out["status"] == loop.FINISHED
    assert [b["status"] for b in out["boards"]] == ["ok", "ok", "ok"]


def test_incomplete_and_no_result_when_one_board_fails(where, resume):
    out = go(where, resume, [GH, NO, PX], dict(OK, notion=net.Permanent("HTTP 404")))
    assert out["status"] == loop.INCOMPLETE
    failed = out["boards"][1]
    assert failed["status"] == "failed" and failed["new"] == [] and "postings" not in failed


def test_404_is_not_retried(where, resume):
    calls = []
    go(where, resume, [NO], {"notion": net.Permanent("HTTP 404")}, calls)
    assert len(calls) == 1


def test_timeout_is_retried_once_then_fails(where, resume):
    calls = []
    out = go(where, resume, [NO], {"notion": [net.Transient("timeout"), net.Transient("timeout")]}, calls)
    assert len(calls) == 2 and out["boards"][0]["status"] == "failed"
    assert [e["event"] for e in out["trace"]].count("retry") == 1


def test_timeout_then_success_is_ok(where, resume):
    out = go(where, resume, [NO], {"notion": [net.Transient("timeout"), OK["notion"]]})
    assert out["status"] == loop.FINISHED


def test_bad_json_fails_and_raw_is_saved(where, resume):
    out = go(where, resume, [NO], {"notion": b"<html>maintenance</html>"})
    b = out["boards"][0]
    assert b["status"] == "failed" and b["raw"]["bytes"] == len(b"<html>maintenance</html>")


def test_board_budget(where, resume):
    out = go(where, resume, [GH, NO, PX], dict(OK), budgets=loop.Budgets(max_boards=2))
    assert out["status"] == loop.BUDGET
    ev = [e for e in out["trace"] if e["event"] == "budget-exhausted"][0]
    assert ev["budget"] == "boards" and ev["untried"] == ["ashby:perplexity"]


def test_request_budget(where, resume):
    out = go(where, resume, [GH, NO, PX], dict(OK), budgets=loop.Budgets(max_requests=2))
    assert out["status"] == loop.BUDGET


def test_seconds_budget(where, resume):
    ticks = iter([0, 0, 200, 200, 200, 200])
    out = go(where, resume, [GH, NO], dict(OK), budgets=loop.Budgets(max_seconds=120), clock=lambda: next(ticks))
    assert out["status"] == loop.BUDGET


def test_baseline_then_new_by_board_key(where, resume):
    go(where, resume, [GH, NO], dict(OK))
    out = go(where, resume, [GH, NO], dict(OK, notion=ashby_board(("n1", "Data Engineer", "SQL"), ("n2", "AI Engineer", "Python"))), n="-2")
    assert [len(b["new"]) for b in out["boards"]] == [0, 1]
    assert out["boards"][1]["new"][0]["record"]["verdict"] == "relevant"


def test_unreadable_state_is_an_error(where, resume):
    run_dir, state = where
    state.parent.mkdir(parents=True, exist_ok=True)
    state.write_text("not json")
    out = go(where, resume, [GH], dict(OK))
    assert out["status"] == loop.ERROR


# ---- Wrong versions 2-4 from GATE.md (1 is the review packet) ------------------------------

def test_wrong_version_2_retrying_a_404_is_caught(where, resume):
    """A loop that retried 404s would send 2 requests here; ours sends 1."""
    calls = []
    go(where, resume, [NO], {"notion": [net.Permanent("HTTP 404"), OK["notion"]]}, calls)
    assert len(calls) == 1


def test_wrong_version_3_string_prefix_path_check_is_caught():
    """WRONG VERSION 3: `str(path).startswith(root/'runs')` accepts runs-evil/. Ours refuses it."""
    def prefix_check(path):
        return str((ROOT / path)).startswith(str(ROOT / "runs"))
    assert prefix_check("runs-evil/x.txt") is True               # the wrong version lets it through
    with pytest.raises(Exception):
        Policy(ROOT).check_write("runs-evil/x.txt")              # ours refuses


def new_by_id_only(postings, seen_ids):
    """WRONG VERSION 4: one set of ids for all boards."""
    return [p for p in postings if p["id"] not in seen_ids]


def test_wrong_version_4_id_only_keys_are_caught(where, resume):
    """Notion already has posting id 'same-id'. Perplexity later adds its own 'same-id'.
    Keyed by (system, board, id) it is new; keyed by id alone it vanishes."""
    notion = ashby_board(("same-id", "AI Engineer", "Python"))
    px1 = ashby_board(("x", "AI Engineer", "Python"))
    px2 = ashby_board(("x", "AI Engineer", "Python"), ("same-id", "AI Engineer", "Python"))
    go(where, resume, [NO, PX], {"notion": notion, "perplexity": px1})                 # baselines
    out = go(where, resume, [NO, PX], {"notion": notion, "perplexity": px2}, n="-2")
    assert [row["record"]["key"] for row in out["boards"][1]["new"]] == ["ashby:perplexity:same-id"]

    from jsagent.providers import Ashby
    wrong = new_by_id_only(Ashby.parse("perplexity", px2), {"same-id", "x"})          # ids seen on any board
    assert wrong == []                                                                  # the new posting is lost
