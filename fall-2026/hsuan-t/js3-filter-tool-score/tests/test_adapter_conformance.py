"""JS2 Step 3c: one test set every board adapter must pass, fed by a saved real response per system.

Why: test_boards.py checks each adapter against fakes that we wrote from our own reading of the API,
so a wrong reading passes there. These tests run each adapter on a response the board really sent
(tests/adapter_samples/<ats>.json) and on broken copies of it. Every test is parametrized over
boards.ADAPTERS, so supporting a new system means adding its adapter plus two sample files; an
adapter with no sample fails here instead of being skipped.

Hand-written expectations (which places each sample posting lists) live in <ats>.expect.json, read
off the raw JSON by a person, not produced by the adapter.
"""

import copy
import json
from pathlib import Path
from urllib.parse import urlparse

import pytest

from job_agent.common.paths import Paths
from job_agent.common.policy import Policy
from job_agent.common.errors import WatchError
from job_agent.watch import state
from job_agent.watch.boards import ADAPTERS

SAMPLES = Path(__file__).parent / "adapter_samples"
SYSTEMS = sorted(ADAPTERS)


def _sample(ats: str) -> dict:
    return json.loads((SAMPLES / f"{ats}.json").read_text())


def _expect(ats: str) -> dict:
    return json.loads((SAMPLES / f"{ats}.expect.json").read_text())


def _encode(doc) -> bytes:
    return json.dumps(doc).encode()


# ---- Interface and samples exist -------------------------------------------------------------

@pytest.mark.parametrize("ats", SYSTEMS)
def test_every_adapter_has_a_real_sample_and_its_expectations(ats):
    assert (SAMPLES / f"{ats}.json").is_file(), f"add a saved real response: {SAMPLES / ats}.json"
    assert (SAMPLES / f"{ats}.expect.json").is_file(), f"add {SAMPLES / ats}.expect.json"


@pytest.mark.parametrize("ats", SYSTEMS)
def test_adapter_offers_the_four_names_and_registers_under_its_own_ats(ats):
    adapter = ADAPTERS[ats]
    assert adapter.ATS == ats                 # boards.json "ats" picks this module, so they must agree
    assert adapter.ID_TYPE in (int, str)      # state.load and the validator only know these two
    assert callable(adapter.board_url) and callable(adapter.parse)


# ---- Host on the allow-list --------------------------------------------------------------------

@pytest.mark.parametrize("ats", SYSTEMS)
def test_adapter_url_is_on_the_allow_list_and_carries_the_slug(ats):
    url = ADAPTERS[ats].board_url("acme")
    Policy.for_run(Paths()).check_url(url)    # Claude off: only board hosts; raises if refused
    assert "/acme" in urlparse(url).path


@pytest.mark.parametrize("ats", SYSTEMS)
def test_the_sample_came_from_the_url_the_adapter_builds(ats):
    """Ties the sample to the adapter: if board_url() changes endpoint (e.g. drops ?content=true,
    which removes the JD), the saved sample no longer describes what the agent fetches."""
    expect = _expect(ats)
    assert ADAPTERS[ats].board_url(expect["slug"]) == expect["source"]


# ---- The real sample parses ---------------------------------------------------------------------

@pytest.mark.parametrize("ats", SYSTEMS)
def test_real_sample_gives_one_posting_per_job_with_ids_of_the_adapters_type(ats):
    adapter, raw = ADAPTERS[ats], _sample(ats)
    postings = adapter.parse(_encode(raw))
    assert len(postings) == len(raw["jobs"]) > 0
    # type() is, not isinstance: True must not count as an int id.
    assert all(type(p.id) is adapter.ID_TYPE for p in postings)
    assert len({p.id for p in postings}) == len(postings)
    assert [p.id for p in postings] == [e["id"] for e in _expect(ats)["postings"]]
    for p in postings:
        assert p.title and p.title == p.title.strip()
        assert p.content                      # checks 3-6 read the JD; an empty one means the wrong field
        assert isinstance(p.location, str)


@pytest.mark.parametrize("ats", SYSTEMS)
def test_real_sample_ids_survive_a_state_file_round_trip(ats, tmp_path):
    """A posting is "new" when its id is not in the state file; if the ids come back changed (type
    or value), every posting looks new on the next run (JS1 Wrong version 3)."""
    adapter = ADAPTERS[ats]
    ids = frozenset(p.id for p in adapter.parse(_encode(_sample(ats))))
    path = tmp_path / "x.state.json"
    state.save(path, state.State("x", ids, "t"))
    assert state.load(path, "x", id_type=adapter.ID_TYPE).seen_ids == ids


@pytest.mark.parametrize("ats", SYSTEMS)
def test_every_place_the_board_lists_is_read_once(ats):
    """Rule check 2 looks for a US place anywhere in Posting.location (JS2 D7)."""
    postings = {p.id: p for p in ADAPTERS[ats].parse(_encode(_sample(ats)))}
    for e in _expect(ats)["postings"]:
        parts = postings[e["id"]].location.split("; ")
        assert sorted(parts) == sorted(e["places"]), e["why"]


# ---- Broken copies of the real sample are errors, never "0 jobs" -------------------------------

def _other_type_id(adapter):
    return "8097321" if adapter.ID_TYPE is int else 8097321


BREAKS = {
    "cut off mid-body": lambda raw, a: _encode(raw)[:200],
    "a list, not an object": lambda raw, a: _encode(raw["jobs"]),
    "no jobs key": lambda raw, a: _encode({k: v for k, v in raw.items() if k != "jobs"}),
    "jobs is not a list": lambda raw, a: _encode({**raw, "jobs": {"0": raw["jobs"][0]}}),
    "a job is not an object": lambda raw, a: _encode({**raw, "jobs": [raw["jobs"][0], "x"]}),
    "a job has no id": lambda raw, a: _encode(_set_id(raw, None)),
    "id of the other system's type": lambda raw, a: _encode(_set_id(raw, _other_type_id(a))),
    "id is a boolean": lambda raw, a: _encode(_set_id(raw, True)),
}


def _set_id(raw: dict, value) -> dict:
    """The real sample with its second job's id replaced (None removes it), so the break sits
    after a good job: an adapter must not return the jobs it read before the bad one."""
    broken = copy.deepcopy(raw)
    job = broken["jobs"][1]
    job.pop("id")
    if value is not None:
        job["id"] = value
    return broken


@pytest.mark.parametrize("ats", SYSTEMS)
@pytest.mark.parametrize("break_name", BREAKS)
def test_a_broken_copy_of_the_real_sample_is_a_watch_error(ats, break_name):
    adapter = ADAPTERS[ats]
    body = BREAKS[break_name](_sample(ats), adapter)
    with pytest.raises(WatchError):
        adapter.parse(body)
