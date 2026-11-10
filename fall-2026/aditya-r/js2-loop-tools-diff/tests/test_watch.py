"""The watch: baseline, new-since-last by id, no duplicate reports, state safety, retries (R5)."""
import argparse
import json

from agent.watch import EXIT_INCOMPLETE, EXIT_INPUT, EXIT_OK, run
from tests.fixtures import NEAR_MISS, NOT_RELEVANT, RELEVANT, board, fake_judge_from, posting, valid_response


def write_persona(tmp_path):
    from tests.fixtures import PERSONA
    p = tmp_path / "persona.json"
    p.write_text(json.dumps(PERSONA))
    return p


def args_for(tmp_path, board_file, label):
    return argparse.Namespace(
        board="synthetic", resume=str(write_persona(tmp_path)), state=str(tmp_path / "state.json"),
        runs_dir=str(tmp_path / "runs"), label=label, from_file=str(board_file), seeded_note="SYNTHETIC test",
        resume_run=None, workers=3, prompt_version="test",
    )


def boards(tmp_path, *contents):
    paths = []
    for i, postings in enumerate(contents):
        f = tmp_path / f"board{i}.json"
        f.write_bytes(board(*postings))
        paths.append(f)
    return paths


def explode(*a):
    raise AssertionError("judge must not be called")


def report(tmp_path, label):
    run_dir = next((tmp_path / "runs").glob(f"*_{label}"))
    return json.loads((run_dir / "report.json").read_text()), run_dir


def test_baseline_reports_zero_new_and_judges_nothing(tmp_path):
    (b0,) = boards(tmp_path, [RELEVANT, NOT_RELEVANT])
    assert run(args_for(tmp_path, b0, "base"), judge_fn=explode) == EXIT_OK
    rep, run_dir = report(tmp_path, "base")
    assert rep["new_postings"] == [] and rep["run"]["new"] == 0
    state = json.loads((tmp_path / "state.json").read_text())
    assert state["ids"] == {"101": "baseline", "202": "baseline"}
    assert (run_dir / "raw_response.json").read_bytes() == b0.read_bytes()  # saved unchanged


def test_second_run_reports_only_new_ids_and_third_run_reports_none(tmp_path):
    b0, b1 = boards(tmp_path, [RELEVANT], [RELEVANT, NOT_RELEVANT, NEAR_MISS])
    run(args_for(tmp_path, b0, "base"), judge_fn=explode)
    judge = fake_judge_from({p["id"]: valid_response(p) for p in (NOT_RELEVANT, NEAR_MISS)})
    assert run(args_for(tmp_path, b1, "second"), judge_fn=judge) == EXIT_OK
    rep, _ = report(tmp_path, "second")
    assert sorted(o["posting_id"] for o in rep["new_postings"]) == [202, 303]
    for o in rep["new_postings"]:
        assert o["RECORD"]["verdict"] in ("relevant", "not_relevant")
        assert o["JUDGMENT"]["valid"] and "opinion" in o["JUDGMENT"]["label"]
    assert run(args_for(tmp_path, b1, "third"), judge_fn=explode) == EXIT_OK
    rep, _ = report(tmp_path, "third")
    assert rep["new_postings"] == []


def test_invalid_judgment_stays_pending_and_is_retried(tmp_path):
    b0, b1 = boards(tmp_path, [RELEVANT], [RELEVANT, NOT_RELEVANT])
    run(args_for(tmp_path, b0, "base"), judge_fn=explode)
    bad = fake_judge_from({202: "not json"})
    assert run(args_for(tmp_path, b1, "bad"), judge_fn=bad) == EXIT_INCOMPLETE
    state = json.loads((tmp_path / "state.json").read_text())
    assert state["ids"]["202"] == "pending"
    rep, run_dir = report(tmp_path, "bad")
    assert not rep["new_postings"][0]["JUDGMENT"]["valid"]
    assert len(list((run_dir / "judgments").glob("202.attempt*.json"))) == 3  # every attempt kept
    good = fake_judge_from({202: valid_response(NOT_RELEVANT)})
    assert run(args_for(tmp_path, b1, "retry"), judge_fn=good) == EXIT_OK
    assert json.loads((tmp_path / "state.json").read_text())["ids"]["202"] == "completed"
    rep, _ = report(tmp_path, "retry")
    assert rep["run"]["retried_pending"] == 1 and rep["run"]["new"] == 0


def test_malformed_state_is_an_error_not_a_reset(tmp_path):
    (b0,) = boards(tmp_path, [RELEVANT])
    (tmp_path / "state.json").write_text("{broken")
    assert run(args_for(tmp_path, b0, "x"), judge_fn=explode) == EXIT_INPUT
    assert (tmp_path / "state.json").read_text() == "{broken"


def test_bad_board_response_leaves_state_unchanged(tmp_path):
    (b0,) = boards(tmp_path, [RELEVANT])
    run(args_for(tmp_path, b0, "base"), judge_fn=explode)
    before = (tmp_path / "state.json").read_text()
    dup = tmp_path / "dup.json"
    dup.write_bytes(board(RELEVANT, posting(101, "dup", "<p>x</p>")))
    assert run(args_for(tmp_path, dup, "dup"), judge_fn=explode) == EXIT_INPUT
    assert (tmp_path / "state.json").read_text() == before


def test_real_looking_resume_is_refused_before_anything_runs(tmp_path):
    (b0,) = boards(tmp_path, [RELEVANT])
    a = args_for(tmp_path, b0, "x")
    from tests.fixtures import PERSONA
    real = dict(PERSONA, personal={"email": "someone@gmail.com", "phone": "(617) 555-0100"})
    (tmp_path / "real.json").write_text(json.dumps(real))
    a.resume = str(tmp_path / "real.json")
    assert run(a, judge_fn=explode) == EXIT_INPUT
    assert not (tmp_path / "state.json").exists()


def test_cli_call_is_isolated():
    """The judge invocation disables tools, MCP, settings and session persistence."""
    import inspect
    from agent import judge
    src = inspect.getsource(judge.call_claude)
    for flag in ('"--tools", ""', '"--strict-mcp-config"', '"--setting-sources", ""', '"--no-session-persistence"',
                 "tempfile.mkdtemp"):
        assert flag in src
