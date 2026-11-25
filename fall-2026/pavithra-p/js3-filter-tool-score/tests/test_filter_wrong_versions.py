"""FILTER.md section 5: each check passes on the real code and catches its wrong version. CONSTRUCTED postings."""
import unittest

from agent import evidence, filter as filt, filter_wrong_versions as wrong, shortlist
from tests.jobs import PERSONA, SKILLS, SPEC, job


def no_substring_match(decide):
    """A posting whose only "skills" are inside other words must not be kept."""
    j = job(content="<p>We use JavaScript and PostgreSQL. Focus on maintaining services.</p>")
    return decide(j, "constructed:board", PERSONA, SPEC).verdict != filt.KEEP


def no_gate_failure_on_shortlist(rank):
    senior = filt.decide(job(title="Senior Staff Backend Engineer",
                             content="<p>Python Java SQL Kafka Redis AWS Docker Kubernetes</p>", id="s1"),
                         "constructed:board", PERSONA, SPEC).to_dict()
    fine = filt.decide(job(id="k1"), "constructed:board", PERSONA, SPEC).to_dict()
    return all(not any(not g["passed"] for g in d["gates"].values()) for d in rank([senior, fine]))


def quote_must_be_in_posting(label):
    claim = {"about": "skills", "claim": "The role uses Kafka every day", "quote": "Kafka is used every day by the team"}
    j = job(content="<p>Python, Kafka and Redis</p>")  # Kafka is named, but the quote is not in the posting
    return label(claim, j, SPEC, SKILLS)[0] != evidence.SUPPORTED


class WrongVersions(unittest.TestCase):
    def test_wrong_1_substring_matching_is_caught(self):
        self.assertTrue(no_substring_match(filt.decide))
        self.assertFalse(no_substring_match(wrong.decide_substring))

    def test_wrong_2_ranking_by_skill_count_is_caught(self):
        self.assertTrue(no_gate_failure_on_shortlist(shortlist.rank))
        self.assertFalse(no_gate_failure_on_shortlist(wrong.rank_by_skill_count))

    def test_wrong_3_keyword_equals_support_is_caught(self):
        self.assertTrue(quote_must_be_in_posting(evidence.label_claim))
        self.assertFalse(quote_must_be_in_posting(wrong.label_keyword))


if __name__ == "__main__":
    unittest.main()
