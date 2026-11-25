"""Checks that guard FILTER.md section 6's wrong versions. Each asserts the right behavior; the
F tests in test_js3_filter.py patch a wrong implementation in and show the check then fails.

Written by Claude Code (claude-opus-5-5), 2026-11-25. All postings are SEEDED (hand-built).
"""
import random

from jobwatch import filter as flt
from jobwatch.text import join_fields


def line(title="Machine Learning Engineer", location="Boston", body=("<p>SEEDED role text.</p>",),
         boilerplate=(), key="seeded:board:1", board="seeded:board", **extra):
    """A SEEDED dataset line. `body` items become one text field each; any sentence whose text is
    in `boilerplate` is flagged boilerplate."""
    text, sents, spans = join_fields(tuple((f"f{i}", b) for i, b in enumerate(body)))
    sentences = [{"field": s["field"], "start": s["start"], "end": s["end"], "boilerplate": s["text"] in boilerplate}
                 for s in sents]
    return {"key": key, "board": board, "posting_id": key.rsplit(":", 1)[1], "url": None, "title": title,
            "location": location, "text": text, "fields": spans, "sentences": sentences, **extra}


def ev(ln):
    return flt.evaluate(ln, flt.VERSIONS["v1"])


def rules_hit(out):
    return {m["rule"] for m in out["matched"]}


def check_F01_whole_words():
    assert ev(line(title="Thai Engineer"))["reasons"] == ["no role word R01-R10 in the title"]
    o = ev(line(title="Machine Learning Engineer, Leadership Programs", body=("<p>We use Python.</p>",)))
    assert o["decision"] == "keep" and "X07" not in rules_hit(o)
    o = ev(line(title="ML Engineer, Headquarters", body=("<p>We train llms and maintain HTML pages in Python.</p>",)))
    assert o["decision"] == "keep" and rules_hit(o) & {"X08", "T08"} == set()


def check_F02_boilerplate_not_counted():
    about = "About us: we do Machine Learning and Python."
    o = ev(line(body=(f"<p>{about}</p><p>SEEDED role text.</p>",), boilerplate=(about,)))
    assert o["topics"] == 0 and o["decision"] == "reject" and o["score"] == 7


def check_F03_topic_counted_once():
    o = ev(line(body=("<p>Python Python Python.</p><p>More Python.</p>",)))
    assert o["topics"] == 1 and o["score"] == 8 and o["decision"] == "keep"


def check_F04_missing_location_not_a_match():
    o = ev(line(location=None, body=("<p>We use PyTorch and Python.</p>",)))
    assert o["decision"] == "abstain" and o["score"] is None and "location missing or empty" in o["reasons"][0]
    o = ev(line(location="", body=("<p>SEEDED role text.</p>",)))
    assert o["decision"] == "reject" and o["score"] is None


def check_F06_ties_not_by_fetch_order():
    outs = [{"key": f"b{b}:{i}", "board": f"seeded:{b}", "posting_id": str(i), "score": s}
            for b, i, s in [("z", 2, 9), ("a", 10, 9), ("a", 9, 9), ("m", 1, 12), ("a", 1, None)]]
    expected = ["seeded:m:1", "seeded:a:10", "seeded:a:9", "seeded:z:2", "seeded:a:1"]
    for seed in range(5):
        shuffled = list(outs)
        random.Random(seed).shuffle(shuffled)
        assert [f"{o['board']}:{o['posting_id']}" for o in flt.rank(shuffled)] == expected


def check_F07_preferred_years_skipped():
    body = ("<li>3+ years of experience with Python.</li><li>8+ years of experience preferred.</li>"
            "<li>Ideally 10 years of experience.</li>",)
    o = ev(line(body=body))
    assert o["years"] == 3 and o["decision"] == "keep"


def check_F08_bare_remote_is_not_us():
    o = ev(line(location="Remote", body=("<p>We use Python.</p>",)))
    assert o["decision"] == "abstain" and "Remote without a US token" in o["reasons"][0]
    assert ev(line(location="Remote - Canada", body=("<p>We use Python.</p>",)))["decision"] == "abstain"
    assert ev(line(location="Remote - US", body=("<p>We use Python.</p>",)))["decision"] == "keep"


def check_F09_primary_location_only():
    o = ev(line(location="San Francisco, California", secondary_locations=["New York, New York"],
                all_locations=["San Francisco", "New York"], body=("<p>We use Python.</p>",)))
    assert o["decision"] == "reject" and o["reasons"] == ["known nonmatching location (no L01-L05)"]
