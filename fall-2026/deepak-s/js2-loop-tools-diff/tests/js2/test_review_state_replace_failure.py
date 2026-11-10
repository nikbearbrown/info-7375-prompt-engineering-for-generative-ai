"""Review packet, the second half of patch 3a4c1fb: the state replace itself fails (GATE.md Amendments A-3).

Written by Claude Code (Claude Opus 5.5), 2026-11-10, after the patch, during review, from
evidence/review/SEEDED_check_state_replace_failure.py. Not written before the patch, and not part of
Deepak's red-before-patch test (tests/js2/test_review_state_on_error.py).

SEEDED fault injection: the state/seen.json write raises OSError; every other write passes through.
Fake transport, temporary folder.
"""
import json

import jobwatch.tools
from js2kit import SeededTransport, run_dir, run_loop, three_ok_routes, wd  # noqa: F401 (wd is a fixture)


def test_state_replace_failure_exits_error_with_no_state_and_error_summary(wd, monkeypatch):
    original = jobwatch.tools.Tools.write_file

    def failing(self, path, *args, **kwargs):
        if str(path).endswith("state/seen.json"):
            raise OSError("SEEDED: state disk full")
        return original(self, path, *args, **kwargs)

    monkeypatch.setattr(jobwatch.tools.Tools, "write_file", failing)
    code = run_loop(SeededTransport(three_ok_routes()))

    assert code == 1
    assert not (wd / "state" / "seen.json").exists()
    summary = json.loads((run_dir(wd) / "summary.json").read_text(encoding="utf-8"))
    assert summary["exit"] == "ERROR"
