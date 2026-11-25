"""JS2 Step 3: the board list and the second applicant-tracking system (Ashby).

Why these tests exist: the loop (Step 5) trusts that data/boards.json names real adapters and safe
names, and that an Ashby board flows through the same watch, state and judges as Greenhouse.
Everything runs on fake responses; no test touches the network or the repo's state/ runs/.
"""

import json

import pytest
from fakes import FakeFetcher, GOOD, START, ashby_board, ashby_job, board, board_row, by_id, job, one_board, run_once

from job_agent.common.errors import InputError, WatchError
from job_agent.judges.validator import Rejected, validate
from job_agent.pipeline import run
from job_agent.watch import board_list
from job_agent.watch.boards import ashby, greenhouse

ID_A, ID_B, ID_C = "8fb1615c-0000-0000-0000-00000000000a", "8fb1615c-0000-0000-0000-00000000000b", "8fb1615c-0000-0000-0000-00000000000c"


# ---- The shipped board list (R13, R14, R18; D2) ------------------------------------------------

def test_shipped_list_has_three_real_boards_on_two_systems_and_one_misspelled(paths):
    boards = board_list.load(paths.boards)
    by_name = {b.name: b for b in boards}
    assert len(boards) >= 3                                   # R13: at least three boards
    assert len({b.ats for b in boards}) >= 2                  # R14: at least two systems
    assert by_name["openai"].adapter is ashby
    assert by_name["stripe"].adapter is greenhouse
    assert "striqe" in by_name                                # R18: the board that fails on purpose


# ---- The list is checked before any board is touched (GATE code 001) ---------------------------

def _write(tmp_path, doc) -> "Path":
    p = tmp_path / "boards.json"
    p.write_text(doc if isinstance(doc, str) else json.dumps(doc))
    return p


OK = {"name": "stripe", "ats": "greenhouse", "slug": "stripe"}


@pytest.mark.parametrize("doc, reason", [
    ("{not json", "not valid JSON"),
    ({"boards": []}, "at least one board"),
    ([OK], "at least one board"),
    ({"boards": [{"name": "stripe", "ats": "greenhouse"}]}, "must have the keys"),
    ({"boards": [{**OK, "url": "https://evil.com"}]}, "must have the keys"),        # unknown key, not ignored
    ({"boards": [{**OK, "ats": "lever"}]}, "not supported"),
    ({"boards": [{**OK, "name": "../stripe"}]}, "name"),                             # would escape state/
    ({"boards": [{**OK, "name": "Stripe"}]}, "name"),
    ({"boards": [{**OK, "slug": "stripe/../evil"}]}, "slug"),                         # would change the URL path
    ({"boards": [{**OK, "slug": "stripe?x=1"}]}, "slug"),
    ({"boards": [OK, {**OK, "slug": "other"}]}, "same name twice"),
    ({"boards": [OK, {**OK, "name": "stripe-2"}]}, "same board"),                    # GATE §3: same board twice
])
def test_a_bad_board_list_is_an_input_error(tmp_path, doc, reason):
    with pytest.raises(InputError, match=reason):
        board_list.load(_write(tmp_path, doc))


def test_missing_board_list_is_an_input_error(tmp_path):
    with pytest.raises(InputError, match="not found"):
        board_list.load(tmp_path / "nope.json")


def test_unknown_board_name_stops_before_fetching(paths):
    fetcher = FakeFetcher(board(job(1)))
    with pytest.raises(InputError, match="not in the board list"):
        run("airbnb", paths.default_resume, paths.default_profile, paths, now=START, fetcher=fetcher)
    assert fetcher.urls == []


# ---- Ashby adapter ---------------------------------------------------------------------------

def test_ashby_job_maps_onto_the_same_posting_fields():
    [p] = ashby.parse(ashby_board(ashby_job(ID_A, title="  Backend Engineer ", location="London, UK",
                                            secondary=("San Francisco",))))
    assert p.id == ID_A                                       # original string id kept (GATE §3)
    assert p.title == "Backend Engineer"
    assert p.location == "London, UK; San Francisco"          # secondary locations count for check 2
    assert p.content == GOOD["content"]


@pytest.mark.parametrize("body, reason", [
    (b"<html>rate limited</html>", "not JSON"),
    (b'{"apiVersion": "1"}', "no 'jobs' list"),
    (json.dumps({"jobs": [{"id": 123, "title": "x"}]}).encode(), "string 'id'"),
    (json.dumps({"jobs": [{"id": "", "title": "x"}]}).encode(), "string 'id'"),
])
def test_ashby_response_of_the_wrong_shape_is_an_error_not_zero_jobs(body, reason):
    with pytest.raises(WatchError, match=reason):
        ashby.parse(body)


def test_ashby_board_goes_through_the_whole_run_with_string_ids(paths):
    first = run_once(paths, ashby_board(ashby_job(ID_A), ashby_job(ID_B)), n=0, board_name="openai")
    second = run_once(paths, ashby_board(ashby_job(ID_B), ashby_job(ID_C)), n=1, board_name="openai")

    assert board_row(first, "openai")["baseline"] is True and first["verdicts"] == []
    assert sorted(by_id(second)) == [ID_C]                    # only the new one, matched as a string
    saved = json.loads(paths.state("openai").read_text())
    assert saved["board"] == "openai" and saved["seen_ids"] == [ID_A, ID_B, ID_C]


def test_ashby_run_fetches_the_ashby_url_for_its_slug(paths):
    fetcher = FakeFetcher(ashby_board(ashby_job(ID_A)))
    run("openai", paths.default_resume, paths.default_profile, paths, now=START, fetcher=fetcher)
    assert fetcher.urls == ["https://api.ashbyhq.com/posting-api/job-board/openai"]


def test_watch_fetches_by_slug_when_it_differs_from_our_name(paths, policy):
    """Our name picks the state file; the slug is what the ATS knows. Mixing them up would fetch
    a board that doesn't exist (or another company's)."""
    fetcher = FakeFetcher(board(job(1)))
    one_board(paths, policy, board_list.Board("acme-us", "greenhouse", "acme", greenhouse), fetcher)
    assert fetcher.urls == ["https://boards-api.greenhouse.io/v1/boards/acme/jobs?content=true"]


def test_ashby_state_file_with_integer_ids_is_rejected(paths):
    """With the wrong id type nothing would ever match, so every posting would look new again."""
    paths.state("openai").parent.mkdir(parents=True)
    paths.state("openai").write_text('{"board": "openai", "seen_ids": [1], "last_run_at": "x"}')
    fetcher = FakeFetcher(ashby_board(ashby_job(ID_A)))
    outcome = run("openai", paths.default_resume, paths.default_profile, paths, now=START, fetcher=fetcher)
    row = board_row(json.loads((outcome.folder / "verdicts.json").read_text()), "openai")
    assert (row["status"], row["code"]) == ("failed", "003") and "list of str ids" in row["reason"]
    assert fetcher.urls == []


# ---- Validator row 3 with string ids ------------------------------------------------------------

def _reply(pid) -> str:
    return json.dumps({"posting_id": pid, "verdict": "relevant", "justification": [
        {"posting_field": "title", "compared_to": "profile.target_roles[]", "result": "backend", "quote": "Backend Engineer"}]})


def test_validator_accepts_the_same_string_id_and_rejects_a_different_type():
    fields = {"title": "Backend Engineer", "location.name": "", "content": "x"}
    assert validate(_reply(ID_A), ID_A, fields)[0] == "relevant"
    # 6042172.0 == 6042172 in Python, so only the type check stops a float id from passing as the posting.
    with pytest.raises(Rejected, match="does not match"):
        validate(_reply(6042172.0), 6042172, fields)


# ---- Places from several fields (D7) -----------------------------------------------------------

def test_greenhouse_adds_office_places_to_a_work_mode_location():
    """Cloudflare-style: location.name is "Hybrid", the place is only in offices[]."""
    [p] = greenhouse.parse(board(job(1, location="Hybrid", offices=("Austin, TX, United States", "London, United Kingdom"))))
    assert p.location == "Hybrid; Austin, TX, United States; London, United Kingdom"


def test_greenhouse_without_offices_reads_exactly_as_in_js1():
    [p] = greenhouse.parse(board(job(1, location="US-Remote, Chicago")))
    assert p.location == "US-Remote, Chicago"


def test_a_place_listed_twice_is_kept_once():
    [p] = greenhouse.parse(board(job(1, location="Seattle, WA", offices=("Seattle, WA", "US"))))
    assert p.location == "Seattle, WA; US"


def test_a_seattle_posting_with_a_us_office_now_passes_check_2(criteria):
    """JS1 Known limit: "Seattle, WA" alone has no "us" and was cut at check 2."""
    from job_agent.judges import rule
    [old] = greenhouse.parse(board(job(1, location="Seattle, WA")))
    [new] = greenhouse.parse(board(job(1, location="Seattle, WA", offices=("US-PERM",))))
    assert rule.judge(old, criteria).failed_check == "2"
    assert rule.judge(new, criteria).failed_check is None


def test_ashby_adds_the_country_to_a_bare_city(criteria):
    """OpenAI-style: location is "San Francisco"; the country is only in address.postalAddress."""
    from job_agent.judges import rule
    [bare] = ashby.parse(ashby_board(ashby_job(ID_A, location="San Francisco")))
    [full] = ashby.parse(ashby_board(ashby_job(ID_A, location="San Francisco", country="United States")))
    assert full.location == "San Francisco; United States"
    assert rule.judge(bare, criteria).failed_check == "2"
    assert rule.judge(full, criteria).failed_check is None
