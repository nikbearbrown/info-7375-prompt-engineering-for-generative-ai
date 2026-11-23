"""Offline fixture mode, the deliberately wrong seeded demo, and the independent checker
(GATE "Finished with the wrong answer", F17, F18, Wrong versions row 7).

Uses copies of Tushar's fixtures in tmp_path; the originals in fixtures/ are only read.
"""

import ast
import json
import shutil
import subprocess
import sys

import pytest

from agent import PROJECT_DIR
from agent.__main__ import main

FIXTURE = PROJECT_DIR / "fixtures" / "greenhouse-stripe-2026-10-28-from-js1.json"
SEED_STATE = PROJECT_DIR / "fixtures" / "seed-state-2026-10-27.json"
SEED_CONFIG = PROJECT_DIR / "config" / "seed-demo.json"
FOUR_BOARD_CONFIG = PROJECT_DIR / "config" / "boards.json"
CHECKER = PROJECT_DIR / "checks" / "independent_count.py"
SEEDED_LABEL = "SEEDED-WRONG-EMPTY (deliberately wrong)"


@pytest.fixture
def copies(tmp_path):
    folder = tmp_path / "fixture-copies"
    folder.mkdir()
    return shutil.copy(FIXTURE, folder), shutil.copy(SEED_STATE, folder)


def expected_new_ids(fixture_copy, seed_copy) -> set:
    """The answer computed straight from the fixture files, without the agent."""
    jobs = json.loads(open(fixture_copy, "rb").read())["jobs"]
    seen = set(json.loads(open(seed_copy, "rb").read())["greenhouse/stripe"])
    return {job["id"] for job in jobs} - seen


def run_cli(tmp_path, out_name, seed_copy, run_id, *flags, config=SEED_CONFIG):
    out = tmp_path / out_name
    out.mkdir()
    shutil.copy(seed_copy, out / "state.json")
    code = main(["--config", str(config), "--out", str(out), *flags], run_id=run_id)
    return code, out, out / "runs" / run_id


def read(run_dir, name):
    return json.loads((run_dir / name).read_text())


def trace(run_dir):
    return [json.loads(line) for line in (run_dir / "trace.jsonl").read_text().splitlines()]


def check(run_dir):
    return subprocess.run([sys.executable, "-I", str(CHECKER), str(run_dir)], capture_output=True, text=True)


def test_a_fixture_run_finds_the_set_difference(tmp_path, copies, capsys):
    """F18 + "Finished with the wrong answer": a normal --fixture run with the seed state is
    finished, and new equals the set difference computed from the fixture files directly."""
    fixture_copy, seed_copy = copies
    expected = expected_new_ids(fixture_copy, seed_copy)
    assert len(expected) == 16  # F18: the October 28 response has 16 IDs absent from October 27
    code, out, run_dir = run_cli(tmp_path, "out-fixture", seed_copy, "run-fixture", "--fixture", str(fixture_copy))
    assert code == 0
    summary = read(run_dir, "summary.json")
    assert summary["exit"] == "finished" and summary["mode"] == "fixture"
    board = summary["boards"][0]
    assert board["new"] == len(expected) and set(board["new_ids"]) == expected
    assert board["baseline"] is False and summary["attempts_used"] == 1  # went through the attempt counter
    assert (out / board["raw_paths"][-1]).read_bytes() == open(fixture_copy, "rb").read()
    assert any(e["operation"] == "permission-check" and e["status"] == "allowed" for e in trace(run_dir))


def test_b_seeded_wrong_run_finishes_with_zero_new(tmp_path, copies):
    """"Finished with the wrong answer": the demo saves the original response, feeds an empty
    jobs list to counting, reports zero new jobs, and exits finished, labeled as seeded."""
    fixture_copy, seed_copy = copies
    code, out, run_dir = run_cli(tmp_path, "out-seed", seed_copy, "run-seed",
                                 "--fixture", str(fixture_copy), "--seed-wrong-empty")
    assert code == 0
    summary = read(run_dir, "summary.json")
    assert summary["exit"] == "finished"
    assert summary["mode"] == SEEDED_LABEL
    board = summary["boards"][0]
    assert board["new"] == 0 and board["new_ids"] == []
    assert (out / board["raw_paths"][-1]).read_bytes() == open(fixture_copy, "rb").read()
    events = [e for e in trace(run_dir) if e["operation"] == "seed-wrong-empty"]
    assert len(events) == 1 and events[0]["status"] == "SUBSTITUTED"
    assert events[0]["substituted"] == '{"jobs": []}'
    assert trace(run_dir)[0]["mode"] == SEEDED_LABEL


def test_c_independent_count_passes_a_and_catches_b(tmp_path, copies):
    """Wrong versions row 7: an independent count from the saved response catches the
    difference. Exit 0 on the correct run, exit 1 with the mismatch shown on the seeded run."""
    fixture_copy, seed_copy = copies
    run_cli(tmp_path, "out-fixture", seed_copy, "run-fixture", "--fixture", str(fixture_copy))
    run_cli(tmp_path, "out-seed", seed_copy, "run-seed", "--fixture", str(fixture_copy), "--seed-wrong-empty")
    expected = expected_new_ids(fixture_copy, seed_copy)

    good = check(tmp_path / "out-fixture" / "runs" / "run-fixture")
    assert good.returncode == 0, good.stdout + good.stderr
    assert "greenhouse/stripe" in good.stdout and "RESULT: all comparable boards match" in good.stdout

    bad = check(tmp_path / "out-seed" / "runs" / "run-seed")
    assert bad.returncode == 1, bad.stdout + bad.stderr
    row = next(line for line in bad.stdout.splitlines() if line.startswith("greenhouse/stripe"))
    assert row.split()[:4] == ["greenhouse/stripe", "0", str(len(expected)), "MISMATCH"]
    assert SEEDED_LABEL in bad.stdout
    assert str(min(expected)) in bad.stdout  # the missing IDs are listed


def test_c_independent_count_writes_nothing(tmp_path, copies):
    """F17: the checker is read-only."""
    fixture_copy, seed_copy = copies
    _, out, run_dir = run_cli(tmp_path, "out-seed", seed_copy, "run-seed",
                              "--fixture", str(fixture_copy), "--seed-wrong-empty")
    before = {p: p.read_bytes() for p in out.rglob("*") if p.is_file()}
    check(run_dir)
    after = {p: p.read_bytes() for p in out.rglob("*") if p.is_file()}
    assert after == before


def test_d_seed_wrong_empty_without_fixture_is_error(tmp_path, capsys):
    """"Finished with the wrong answer": the seeded demo is offline only; without --fixture, exit error."""
    out = tmp_path / "out"
    code = main(["--config", str(SEED_CONFIG), "--out", str(out), "--seed-wrong-empty"], run_id="run-x")
    assert code == 2
    lines = capsys.readouterr().out.splitlines()
    assert len(lines) == 1 and lines[0].startswith("error (exit 2):")
    assert not (out / "runs").exists()


def test_fixture_mode_needs_exactly_one_board(tmp_path, copies):
    """F18 offline mode: --fixture is allowed only with a one-board config; otherwise exit
    error before any transport call."""
    fixture_copy, seed_copy = copies
    code, _, run_dir = run_cli(tmp_path, "out-fixture", seed_copy, "run-four", "--fixture", str(fixture_copy),
                               config=FOUR_BOARD_CONFIG)
    assert code == 2
    summary = read(run_dir, "summary.json")
    assert summary["error"]["stage"] == "fixture" and summary["attempts_used"] == 0
    assert not (run_dir / "raw").exists()


def test_seeded_run_leaves_seen_ids_unchanged(tmp_path, copies):
    """Consequence of the deliberate substitution: nothing new is staged, so the 16 new IDs
    stay unseen in state.json (seen ∪ ∅ = seen)."""
    fixture_copy, seed_copy = copies
    _, out, _ = run_cli(tmp_path, "out-seed", seed_copy, "run-seed", "--fixture", str(fixture_copy),
                        "--seed-wrong-empty")
    saved = json.loads((out / "state.json").read_text())["greenhouse/stripe"]
    seed = json.loads(open(seed_copy, "rb").read())["greenhouse/stripe"]
    assert set(saved) == set(seed)


def test_e_independent_count_does_not_import_agent():
    """F17: the checker is a separate program; it must not import anything from agent/."""
    source = CHECKER.read_text()
    tree = ast.parse(source)
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported |= {alias.name.split(".")[0] for alias in node.names}
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
    assert imported <= {"json", "sys", "pathlib"}
    assert "agent" not in imported
    assert "__import__" not in source and "importlib" not in source and "sys.path" not in source
