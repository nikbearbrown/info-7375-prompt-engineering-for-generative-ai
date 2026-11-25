"""Each FILTER.md wrong version is caught: the same check passes on the real code and fails on the mutant."""
import unittest

from tests import js3_mutants
from tests.js3_helpers import body, claim, gh, skills, sl, verdict


def check_no_substring_role_or_skill():
    for title in ("HTML Email Developer", "Metadata Platform Engineer"):
        v = verdict(gh(title, content=body("SQL")))
        assert v["verdict"] == "reject" and v["rule"] == "F1", (title, v)
    v = verdict(gh("Data Scientist", content=body("We use PostgreSQL and MySQL.")))
    assert v["verdict"] == "reject" and v["rule"] == "F4", v


def check_silence_is_not_sponsorship():
    p = gh(content=body("SQL"))
    assert claim(p, 3)["label"] == "insufficient"


def check_rank_by_supported_claims():
    repeats = gh("Data Analyst", content=body(" ".join(["data"] * 10) + " SQL."))
    repeats["posting_id"] = "greenhouse:faire:repeats"
    fewer = gh("Data Analyst", location="Remote - US",
               content=body("We use SQL and Python on data. We sponsor H-1B visas."))
    fewer["posting_id"] = "greenhouse:faire:fewer"
    order = [e["posting_id"] for e in sl().build_shortlist([repeats, fewer], skills())]
    assert order == ["greenhouse:faire:fewer", "greenhouse:faire:repeats"], order


def check_missing_location_not_defaulted():
    p = gh(content=body("SQL"), drop=("location",))
    v = verdict(p)
    assert v["verdict"] == "reject" and v["rule"] == "F3", v
    assert "missing: location.name" in v["reason"], v
    assert claim(p, 1)["label"] == "insufficient"


CASES = [
    ("substring matching", js3_mutants.substring_matching, check_no_substring_role_or_skill),
    ("silence as sponsorship", js3_mutants.silence_as_sponsorship, check_silence_is_not_sponsorship),
    ("ranking by keyword count", js3_mutants.rank_by_keyword_count, check_rank_by_supported_claims),
    ("missing field defaulted", js3_mutants.missing_location_defaulted, check_missing_location_not_defaulted),
]


class WrongVersionsAreCaught(unittest.TestCase):
    def test_each_check_passes_on_the_real_code(self):
        for name, _, check in CASES:
            with self.subTest(name=name):
                check()

    def test_each_mutant_fails_its_check(self):
        for name, mutant, check in CASES:
            with self.subTest(name=name):
                with mutant():
                    with self.assertRaises(AssertionError, msg=f"wrong version survived: {name}"):
                        check()


if __name__ == "__main__":
    unittest.main()
