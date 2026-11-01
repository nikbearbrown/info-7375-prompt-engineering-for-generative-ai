"""Shared test data and the two contract checks. All postings here are CONSTRUCTED, not real Klaviyo data."""
from __future__ import annotations

import json
import re
from pathlib import Path

from jobwatch.persona import load_resume
from jobwatch.rule import NOT_RELEVANT, RELEVANT
from jobwatch.text import find_phrase, normalize

ROOT = Path(__file__).resolve().parent.parent
RESUME = load_resume(ROOT / "data" / "supriya-sharma.resume.json")


def make_posting(pid, title, content="", location="Boston, MA", offices=("Boston",)):
    return {"id": pid, "title": title, "content": content,
            "location": {"name": location} if location is not None else None,
            "offices": [{"name": o} for o in offices],
            "absolute_url": f"https://example.com/jobs/{pid}"}


def board_bytes(postings) -> bytes:
    return json.dumps({"jobs": list(postings), "meta": {"total": len(postings)}}).encode()


SKILL_LINE = re.compile(r'^resume\.skills\[(\d+)\]="([^"]+)" matched posting\.content="(.*)"$')


def assert_verdict_stays_with_posting_id(tc, classify_all):
    """CONTRACT wrong version 1. Two postings with different verdicts, in both input orders."""
    good = make_posting(101, "Software Engineer, Payments", "<p>We use Python and Redis daily.</p>")
    senior = make_posting(202, "Senior Software Engineer, Data", "<p>We use Python and Redis daily.</p>")
    for order in ([good, senior], [senior, good]):
        results = classify_all(order, RESUME)
        tc.assertEqual(set(results), {"101", "202"})
        for pid, title, verdict in (("101", good["title"], RELEVANT), ("202", senior["title"], NOT_RELEVANT)):
            r = results[pid]
            tc.assertEqual(r["posting_id"], pid)
            tc.assertEqual(r["title"], title)
            tc.assertEqual(r["verdict"], verdict, f"posting {pid} got the other posting's verdict")
            tc.assertIn(f'posting.title="{title}"', r["justification"][0])
        tc.assertFalse(results["202"]["checks"]["seniority"])
        tc.assertTrue(results["101"]["checks"]["seniority"])


def assert_justification_is_supported(tc, posting, result):
    """Every cited skill must be a whole-word match, quoted from the normalized posting text."""
    content = normalize(posting["content"])
    for line in result["justification"]:
        m = SKILL_LINE.match(line)
        if not m:
            continue
        index, skill, quoted = int(m.group(1)), m.group(2), m.group(3)
        tc.assertEqual(RESUME["skills"][index], skill)
        tc.assertIn(quoted, content, f"cited text for {skill} is not in the posting")
        tc.assertIsNotNone(find_phrase(skill, content), f"{skill} cited but not a whole-word match")


def assert_skill_matches_require_posting_evidence(tc, classify):
    """CONTRACT wrong version 2. 'JavaScript' must not count as Java; one real skill is not enough."""
    posting = make_posting(303, "Software Engineer", "<p>Our UI is JavaScript. Services are in Python.</p>")
    result = classify(posting, RESUME)
    matched = [m["skill"] for m in result["details"]["skills"]["matched"]]
    tc.assertEqual(matched, ["Python"], "Java was counted from 'JavaScript'")
    tc.assertFalse(result["checks"]["skills"])
    tc.assertEqual(result["verdict"], NOT_RELEVANT)
    tc.assertFalse(any('"Java"' in line for line in result["justification"]))
    assert_justification_is_supported(tc, posting, result)
