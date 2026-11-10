
import json
from pathlib import Path

from agent.rule import judge_rule, judge_all_rule
from agent.judge import judge_claude

PERSONA = Path(__file__).parent.parent / "data" / "persona_alex.json"
RESUME = json.loads(PERSONA.read_text())


def make_posting(pid, title, location, content):
    return {
        "id": pid,
        "title": title,
        "location": {"name": location},
        "content": content,
    }


# Relevant for Alex: title, location, and 3 skills (Java, Python, Docker),
# escaped like Glean's
GOOD = make_posting(
    10,
    "Senior Software Engineer",
    "Remote",
    "&lt;p&gt;We use Java, Python and Docker.&lt;/p&gt;",
)

# Not relevant: wrong title, no skills
BAD = make_posting(
    20,
    "Account Executive",
    "Remote",
    "&lt;p&gt;Sell to enterprise customers.&lt;/p&gt;",
)


def test_verdicts_remain_associated_with_correct_posting_ids():
    results = judge_all_rule([GOOD, BAD], RESUME)
    by_id = {r["posting_id"]: r["verdict"] for r in results}

    # Posting 10 is relevant; posting 20 is not relevant
    assert by_id[10] == "relevant"
    assert by_id[20] == "not_relevant"

    # Reversing the input order must not change verdicts per posting ID
    reversed_results = judge_all_rule([BAD, GOOD], RESUME)
    reversed_by_id = {
        r["posting_id"]: r["verdict"] for r in reversed_results
    }
    assert reversed_by_id == by_id


def test_every_verdict_has_resume_and_posting_field_evidence():
    allowed_resume = {"target_titles", "skills", "locations"}
    allowed_posting = {"title", "content", "location.name"}

    for r in judge_all_rule([GOOD, BAD], RESUME):
        assert r["source"] == "record"

        # Resume and posting evidence must not be empty
        assert r["resume_fields"]
        assert r["posting_fields"]

        # All cited fields must be allowed
        assert set(r["resume_fields"]) <= allowed_resume
        assert set(r["posting_fields"]) <= allowed_posting


def test_skills_require_three_distinct_whole_word_matches():
    def verdict(content):
        posting = make_posting(
            1, "Software Engineer", "Remote", content
        )
        return judge_rule(posting, RESUME)

    # JavaScript must not count as Java: only Python + Docker = 2 skills
    r1 = verdict("We use JavaScript, Python and Docker.")
    assert r1["verdict"] == "not_relevant"
    assert "Java" not in r1["checks"]["skills"]["matched"]

    # Repeating the same skill counts only once: Java + Python = 2
    r2 = verdict("Java, Java, Java and Python.")
    assert r2["verdict"] == "not_relevant"

    # Docker appears only in the link URL and must not count after HTML
    # entities are decoded and tags are stripped
    r3 = verdict(
        "&lt;p&gt;Java and Python&lt;/p&gt;"
        "&lt;a href=&quot;https://example.com/docker&quot;&gt;"
        "link&lt;/a&gt;"
    )
    assert r3["verdict"] == "not_relevant"

    # Three distinct skills, case-insensitive, in escaped HTML
    r4 = verdict(
        "&lt;li&gt;JAVA&lt;/li&gt;"
        "&lt;li&gt;python&lt;/li&gt;"
        "&lt;li&gt;AWS&lt;/li&gt;"
    )
    assert r4["verdict"] == "relevant"


def test_invalid_judgment_retries_once_then_marks_invalid():
    valid = json.dumps({
        "verdict": "relevant",
        "justification": "Title and skills match.",
        "resume_fields": ["target_titles", "skills"],
        "posting_fields": ["title", "content"],
    })

    cites_email = json.dumps({
        "verdict": "relevant",
        "justification": "Good candidate.",
        "resume_fields": ["email"],
        "posting_fields": ["title"],
    })

    def fake_model(replies):
        """Return a fake model function and record its calls."""
        calls = []

        def call_model(prompt):
            calls.append(prompt)
            return replies[len(calls) - 1]

        return call_model, calls

    # Case A: extra prose twice -> invalid after exactly 2 attempts
    model, calls = fake_model([
        "Sure! " + valid,
        "Here you go: " + valid,
    ])
    a = judge_claude(GOOD, RESUME, model)
    assert a["verdict"] == "invalid"
    assert len(calls) == 2

    # Case B: invalid first reply, valid second reply -> accepted on retry
    model, calls = fake_model([
        "not json at all",
        valid,
    ])
    b = judge_claude(GOOD, RESUME, model)
    assert b["verdict"] == "relevant"
    assert b["source"] == "judgment"
    assert len(calls) == 2

    # Case C: citing "email" is forbidden, even after retry
    model, calls = fake_model([
        cites_email,
        cites_email,
    ])
    c = judge_claude(GOOD, RESUME, model)
    assert c["verdict"] == "invalid"
    assert len(calls) == 2
