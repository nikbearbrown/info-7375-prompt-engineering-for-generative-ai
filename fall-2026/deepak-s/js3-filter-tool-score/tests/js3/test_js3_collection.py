"""Phase 2b: config/boards.json "content" and the FILTER.md section 5 text fields.

Written by Claude Code (claude-opus-5-5), 2026-11-25. Loop runs here are SEEDED (js2kit's fake
transport serving fixtures/seeded/). Provider tests parse the real bodies of the manual capture
evidence/manual-capture/20261125T182322Z/ (live, committed in 3fe5a78). The one hand-built item
is labelled SEEDED in its test name.
"""
import json
from pathlib import Path

import js3kit  # noqa: F401  (puts tests/js2 on sys.path)
import checks
from js2kit import GH, board, board_result, ok, run_loop, seeded, summary, wd, SeededTransport  # noqa: F401
from jobwatch.providers import ashby, greenhouse, lever
from jobwatch.tools import FetchResult

ROOT = Path(__file__).resolve().parents[2]
CAPTURE = ROOT / "evidence" / "manual-capture" / "20261125T182322Z"
JSON_CT = {"content-type": "application/json; charset=utf-8"}


def captured(name):
    body = (CAPTURE / name).read_bytes()
    return body, json.loads(body)


def parse(provider, body):
    return provider.parse(FetchResult("https://example.invalid/", 200, JSON_CT, body), "test:board")


# --- URLs ------------------------------------------------------------------------------------
def test_greenhouse_url_asks_for_content_only_when_flag_is_true():
    assert greenhouse.url("boards-api.greenhouse.io", "stripe", content=True) == \
        "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"
    assert greenhouse.url("boards-api.greenhouse.io", "stripe") == "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
    assert greenhouse.url("boards-api.greenhouse.io", "stripe", content=False) == greenhouse.url("boards-api.greenhouse.io", "stripe")


def test_lever_and_ashby_urls_do_not_change_with_the_flag():
    assert lever.url("api.lever.co", "palantir", content=True) == lever.url("api.lever.co", "palantir")
    assert ashby.url("api.ashbyhq.com", "notion", content=True) == ashby.url("api.ashbyhq.com", "notion")


def test_loop_requests_greenhouse_with_content_true_when_config_says_so(wd):
    checks.write_boards(wd, [board("greenhouse", "seeded-gh", "boards-api.greenhouse.io", content=True)])
    url = GH.format("seeded-gh") + "?content=true"
    t = SeededTransport({url: ok(seeded("SEEDED_greenhouse_two_jobs.json"))})
    assert run_loop(t) == 0
    assert [r["url"] for r in t.requests] == [url]
    assert board_result(summary(wd), "greenhouse:seeded-gh")["url"] == url


def test_loop_without_content_key_requests_the_plain_url(wd):
    checks.write_boards(wd, [board("greenhouse", "seeded-gh", "boards-api.greenhouse.io")])
    t = SeededTransport({GH.format("seeded-gh"): ok(seeded("SEEDED_greenhouse_two_jobs.json"))})
    assert run_loop(t) == 0 and [r["url"] for r in t.requests] == [GH.format("seeded-gh")]


def test_content_that_is_not_a_boolean_is_a_config_error(wd):
    checks.write_boards(wd, [board("greenhouse", "seeded-gh", "boards-api.greenhouse.io", content="yes")])
    t = SeededTransport({})
    assert run_loop(t) == 1 and t.requests == []
    assert "content must be true or false" in summary(wd)["error"]["error"]


# --- text fields (FILTER.md section 5) -------------------------------------------------------
def test_greenhouse_text_is_content_from_the_captured_body():
    body, data = captured("01-greenhouse-stripe.body")
    postings = parse(greenhouse, body)
    assert len(postings) == len(data["jobs"]) == 771
    first = postings[0]
    assert first.text_fields == (("content", data["jobs"][0]["content"]),)
    assert first.location == data["jobs"][0]["location"]["name"]


def test_lever_text_order_is_description_then_each_heading_and_content_then_additional():
    body, data = captured("03-lever-us-palantir.body")
    postings = parse(lever, body)
    assert len(postings) == len(data) == 305
    for p, item in zip(postings, data):
        expect = [("description", item["description"])]
        for i, entry in enumerate(item["lists"]):
            expect += [(f"lists[{i}].text", entry["text"]), (f"lists[{i}].content", entry["content"])]
        expect.append(("additional", item["additional"]))
        assert p.text_fields == tuple(expect)
        assert p.location == item["categories"]["location"]


def test_ashby_text_is_description_html_not_description_plain():
    body, data = captured("05-ashby-notion.body")
    postings = parse(ashby, body)
    assert len(postings) == len(data["jobs"]) == 172
    for p, item in zip(postings, data["jobs"]):
        assert p.text_fields == (("descriptionHtml", item["descriptionHtml"]),)
        assert p.location == item["location"]


def test_SEEDED_lever_item_missing_fields_leaves_them_out():
    item = {"id": "seeded-1", "text": "SEEDED ML Engineer", "categories": {"location": "Boston"},
            "lists": [{"text": "SEEDED heading", "content": None}], "additional": 7}
    (p,) = parse(lever, json.dumps([item]).encode())
    assert p.text_fields == (("lists[0].text", "SEEDED heading"),)
