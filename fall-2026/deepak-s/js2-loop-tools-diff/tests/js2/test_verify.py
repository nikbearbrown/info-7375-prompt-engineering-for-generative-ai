"""verify, the independent check: GATE.md section 7. Written by Claude Code (Claude Opus 5.5), 2026-11-10.
SEEDED runs only (fake transport, fixtures/seeded/)."""
import json

import checks
from js2kit import GH, JSON, LEVER_EU, SeededTransport, board, ok, run_dir, run_loop, seeded, three_ok_routes, wd  # noqa: F401
from jobwatch import cli


def rel(workdir, path):
    return str(path.relative_to(workdir))


def test_verify_clean_run_exits_0(wd, capsys):
    run_loop(SeededTransport(three_ok_routes()))
    assert cli.main(["verify", rel(wd, run_dir(wd))]) == 0
    assert "result: CLEAN" in capsys.readouterr().out


def test_verify_flags_suspect_after_6_then_0(wd, capsys):
    checks.check_verify_flags_suspect(wd, capsys)


def test_verify_flags_unconfirmed_first_observation_empty(wd, capsys):
    checks.write_boards(wd, [board("lever", "seeded-lv", "api.eu.lever.co")])
    assert run_loop(SeededTransport({LEVER_EU.format("seeded-lv"): ok(seeded("SEEDED_lever_empty.json"))})) == 0
    capsys.readouterr()
    assert cli.main(["verify", rel(wd, run_dir(wd))]) == 2
    assert "UNCONFIRMED" in capsys.readouterr().out


def test_verify_flags_mismatch_when_summary_count_edited(wd, capsys):
    run_loop(SeededTransport(three_ok_routes()))
    p = run_dir(wd) / "summary.json"
    s = json.loads(p.read_text(encoding="utf-8"))
    s["boards"][0]["count"] = 0
    p.write_text(json.dumps(s), encoding="utf-8")
    capsys.readouterr()
    assert cli.main(["verify", rel(wd, run_dir(wd))]) == 2
    assert "MISMATCH" in capsys.readouterr().out


def test_verify_flags_mismatch_when_raw_bytes_changed(wd, capsys):
    run_loop(SeededTransport(three_ok_routes()))
    raw = next((run_dir(wd) / "raw").iterdir())
    raw.write_bytes(raw.read_bytes() + b" ")
    capsys.readouterr()
    assert cli.main(["verify", rel(wd, run_dir(wd))]) == 2
    assert "sha256" in capsys.readouterr().out


def test_verify_flags_mismatch_when_failed_board_reported_with_count(wd, capsys):
    checks.write_boards(wd, [board("greenhouse", "seeded-bad", "boards-api.greenhouse.io")])
    run_loop(SeededTransport({GH.format("seeded-bad"): (404, seeded("SEEDED_greenhouse_404.json"), JSON)}))
    p = run_dir(wd) / "summary.json"
    s = json.loads(p.read_text(encoding="utf-8"))
    s["boards"][0]["count"] = 0
    p.write_text(json.dumps(s), encoding="utf-8")
    capsys.readouterr()
    assert cli.main(["verify", rel(wd, run_dir(wd))]) == 2
    assert "reports a count" in capsys.readouterr().out


def test_verify_flags_invalid_for_saved_html(wd, capsys):
    checks.write_boards(wd, [board("lever", "seeded-lv", "api.eu.lever.co")])
    run_loop(SeededTransport({LEVER_EU.format("seeded-lv"): (200, seeded("SEEDED_lever_html_200.html"),
                                                             {"Content-Type": "text/html"})}))
    capsys.readouterr()
    assert cli.main(["verify", rel(wd, run_dir(wd))]) == 2
    assert "INVALID" in capsys.readouterr().out


def test_verify_refuses_a_path_outside_runs(wd, capsys):
    (wd / "elsewhere").mkdir()
    assert cli.main(["verify", "elsewhere"]) == 2
    assert "outside runs/" in capsys.readouterr().out
