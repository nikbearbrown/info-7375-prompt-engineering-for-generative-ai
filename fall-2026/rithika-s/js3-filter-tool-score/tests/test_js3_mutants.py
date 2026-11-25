"""FILTER.md section 4: wrong versions W1-W5 must be caught.

Each mutant is the real js3.filter.Filter with exactly one hook overridden.
Each check passes on the real filter and fails on its mutant. Never import
these mutants from js3/.
"""

import unittest

import js3_fixtures as fx
from js3.filter import ABSTAIN, NO_BODY, REJECTED, Filter, term_pattern


class W1Substring(Filter):
    """WRONG: substring matching instead of whole words."""

    def pattern(self, term, mode, case_sensitive=False):
        return term_pattern(term, whole_word=False,
                            case_sensitive=case_sensitive)


class W2RoleInBody(Filter):
    """WRONG: role words searched in the body instead of the title."""

    def role_field(self):
        return "body_text"


class W3CaseSensitiveExclusion(Filter):
    """WRONG: exclusions matched case-sensitively."""

    exclusion_case_sensitive = True


class W4NoCap(Filter):
    """WRONG: every topic-word occurrence counted, no cap of 3."""

    def topic_score(self, r2_matches):
        return len(r2_matches)


class W5EmptyBodyRejects(Filter):
    """WRONG: empty body treated as a reject."""

    def no_body_decision(self):
        return REJECTED, NO_BODY


def _expect(condition, message):
    if not condition:
        raise AssertionError(message)


def _eval(filter_cls, title, body):
    return filter_cls(fx.CONFIG).evaluate(fx.post(title, body))


def check_w1(filter_cls):
    res = _eval(filter_cls, "HTML Engineer", "PyTorch inference training.")
    _expect("R1" not in res["fired"], "'HTML Engineer' matched a role word")
    _expect(res["decision"] == "rejected", f"HTML Engineer {res['decision']}")


def check_w2(filter_cls):
    res = _eval(filter_cls, "Account Executive, Enterprise",
                "Sell our machine learning platform: LLM model training.")
    _expect("R1" not in res["fired"], "role word counted from the body")
    _expect(res["decision"] == "rejected",
            f"sales posting {res['decision']}")


def check_w3(filter_cls):
    res = _eval(filter_cls, "ML Engineer",
                "PyTorch and LLM work. Security Clearance required.")
    _expect("R3" in res["fired"], "'Security Clearance' did not fire R3")
    res = _eval(filter_cls, "ML Engineering MANAGER", "PyTorch and LLM.")
    _expect("R4" in res["fired"], "'MANAGER' did not fire R4")


def check_w4(filter_cls):
    spam = _eval(filter_cls, "Business Analyst", " ".join(["model"] * 10))
    _expect(spam["score"] == 1, f"model x10 scored {spam['score']}")
    _expect(spam["decision"] == "rejected", "model x10 was kept")
    real = _eval(filter_cls, "ML Engineer",
                 "LLM training, inference, embedding and retrieval.")
    _expect(real["score"] == 6, f"capped role scored {real['score']}")
    _expect(real["score"] > spam["score"], "spam outranks a real ML role")


def check_w5(filter_cls):
    for body in ("", "  "):
        res = _eval(filter_cls, "ML Engineer", body)
        _expect(res["decision"] == ABSTAIN and res["reason"] == NO_BODY,
                f"empty body gave {res['decision']}")


MUTANTS = {
    "W1": (W1Substring, check_w1),
    "W2": (W2RoleInBody, check_w2),
    "W3": (W3CaseSensitiveExclusion, check_w3),
    "W4": (W4NoCap, check_w4),
    "W5": (W5EmptyBodyRejects, check_w5),
}


class MutantTests(unittest.TestCase):

    def test_real_filter_passes_every_check(self):
        for wid, (_, check) in MUTANTS.items():
            with self.subTest(wrong_version=wid):
                check(Filter)

    def test_w1_substring_matching_is_caught(self):
        with self.assertRaises(AssertionError):
            check_w1(W1Substring)

    def test_w2_role_words_in_body_is_caught(self):
        with self.assertRaises(AssertionError):
            check_w2(W2RoleInBody)

    def test_w3_case_sensitive_exclusion_is_caught(self):
        with self.assertRaises(AssertionError):
            check_w3(W3CaseSensitiveExclusion)

    def test_w4_no_cap_is_caught(self):
        with self.assertRaises(AssertionError):
            check_w4(W4NoCap)

    def test_w5_empty_body_reject_is_caught(self):
        with self.assertRaises(AssertionError):
            check_w5(W5EmptyBodyRejects)


if __name__ == "__main__":
    unittest.main()
