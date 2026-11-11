"""Review packet, candidate 1: an ERROR exit must not change state.

SEEDED fault injection: the summary.json write raises OSError("SEEDED: disk full").
GATE.md section 1: on ERROR, "state was not updated"; state/seen.json changes
only on FINISHED or INCOMPLETE.

Drafted in claude.ai chat (Claude Opus 5.5, 2026-11-10). Read, run red and
committed by Deepak before the patch.
"""
from datetime import timedelta

import jobwatch.tools
from js2kit import GH, NOW, SeededTransport, ok, run_loop, seeded, three_ok_routes, wd  # noqa: F401 (wd is a fixture)


def _fail_summary_write(monkeypatch):
    """SEEDED: only the summary.json write fails; every other write passes through."""
    original = jobwatch.tools.Tools.write_file

    def wrapper(self, path, *args, **kwargs):
        if str(path).endswith("summary.json"):
            raise OSError("SEEDED: disk full")
        return original(self, path, *args, **kwargs)

    monkeypatch.setattr(jobwatch.tools.Tools, "write_file", wrapper)


def test_error_exit_does_not_create_state(wd, monkeypatch, capsys):
    """No prior state. A baseline run would create state/seen.json; on ERROR it must not."""
    _fail_summary_write(monkeypatch)
    code = run_loop(SeededTransport(three_ok_routes()))
    assert code == 1
    assert (wd / "state" / "seen.json").exists() is False
    assert "jobwatch: ERROR:" in capsys.readouterr().err


def test_error_exit_leaves_existing_state_byte_identical(wd, monkeypatch, capsys):
    """Prior state exists and the faulted run sees a new posting, so state would change."""
    assert run_loop(SeededTransport(three_ok_routes())) == 0
    seen = wd / "state" / "seen.json"
    before = seen.read_bytes()
    capsys.readouterr()

    routes = three_ok_routes()
    routes[GH.format("seeded-gh")] = ok(seeded("SEEDED_greenhouse_three_jobs.json"))
    _fail_summary_write(monkeypatch)
    code = run_loop(SeededTransport(routes), now=NOW + timedelta(minutes=5))

    assert code == 1
    assert seen.read_bytes() == before
    assert "jobwatch: ERROR:" in capsys.readouterr().err
