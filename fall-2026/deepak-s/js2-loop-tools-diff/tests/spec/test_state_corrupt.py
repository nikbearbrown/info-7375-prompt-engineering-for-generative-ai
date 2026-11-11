"""Case 6 (Watch). Written by Claude Code from tests/acceptance/ACCEPTANCE_CASES.md on 2026-10-29, before any implementation. All state files are constructed."""
import json

import pytest

from conftest import BOARD_URL, FakeOpener, board_body, job, run_args, run_cli

VALID = {
    "schema_version": 1,
    "board": "acme",
    "seen_ids": ["201"],
    "updated_at": "2026-10-29T17:00:00Z",
    "last_run_id": "20261029T170000Z_acme",
}


def _state(**changes):
    return json.dumps({**VALID, **changes}).encode("utf-8")


CORRUPT = {
    "empty": b"",
    "invalid_json": b'{"schema_version": 1,',
    "not_an_object": b'["201"]',
    "unknown_schema_version": _state(schema_version=2),
    "board_mismatch": _state(board="other"),
    "seen_ids_not_a_list": _state(seen_ids="201"),
    "seen_ids_not_digit_strings": _state(seen_ids=["abc"]),
    "seen_ids_integers": _state(seen_ids=[201]),
    "seen_ids_not_unique": _state(seen_ids=["201", "201"]),
}


def _opener():
    return FakeOpener({BOARD_URL: (200, board_body([job(201, "AI Engineer")]), {})})


def test_ac06_valid_state_file_is_accepted(workdir):
    (workdir / "state").mkdir()
    (workdir / "state" / "acme.json").write_bytes(_state())
    assert run_cli(run_args(), opener=_opener()) == 0


@pytest.mark.parametrize("content", list(CORRUPT.values()), ids=list(CORRUPT))
def test_ac06_corrupt_state_stops_the_run_and_is_left_unchanged(workdir, content):
    (workdir / "state").mkdir()
    state = workdir / "state" / "acme.json"
    state.write_bytes(content)
    opener = _opener()

    assert run_cli(run_args(), opener=opener) == 4
    assert state.read_bytes() == content
    assert opener.requests == []
    assert not (workdir / "evidence").exists()
