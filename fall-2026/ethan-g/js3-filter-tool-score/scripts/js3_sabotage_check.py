"""Plant each wrong version from FILTER.md section 4 into the code and check that its test turns red (like JS2's sabotage check).

    python3 scripts/js3_sabotage_check.py

W8 (tuning on the held-out labels) is checked by tests/test_js3_measure.py instead.
"""
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jsagent import filter as flt, rule, shortlist  # noqa: E402
from tests import test_js3_filter as T  # noqa: E402

NEVER = re.compile(r"(?!x)x")
real_evaluate = flt.evaluate


def w4_evaluate(p):
    r = real_evaluate(p)
    if r["bucket"] == "cannot_tell" and "description" in r["missing"]:
        r["bucket"] = "rejected"
    return r


def w5_first_years(content):
    ms = list(rule.YEARS_RE.finditer(content))
    return (ms[-1].group(0), int(ms[-1].group(1))) if ms else ("", None)


def w10_evaluate(p):
    r = real_evaluate(p)
    if r["location_kind"] == "boston" and "remote" in r["location"].lower():
        r["score_parts"]["location"] += flt.POINTS["remote_us"]
        r["score"] += flt.POINTS["remote_us"]
    return r


SABOTAGE = {
    "W1 role by single word": ("test_W1_role_needs_whole_phrase",
                               [(flt, "_ROLE", [("data", flt._word("data", re.I)), ("analyst", flt._word("analyst", re.I))] + flt._ROLE)]),
    "W2 case-insensitive topic words": ("test_W2_topic_words_case_sensitive_whole_word",
                                        [(flt, "_TOPIC", [(w, re.compile(re.escape(w), re.I)) for w in flt.TOPIC_WORDS])]),
    "W3 counting repeats": ("test_W3_repeats_count_once",
                            [(flt, "topic_words", lambda c: sorted(m for w, rx in flt._TOPIC for m in rx.findall(c)))]),
    "W4 missing description = reject": ("test_W4_missing_description_is_cannot_tell", [(flt, "evaluate", w4_evaluate)]),
    "W5 years from the wrong phrase": ("test_W5_years_from_first_experience_phrase", [(rule, "first_years_phrase", w5_first_years)]),
    "W6 a word counts as support": ("test_W6_a_mention_is_not_support",
                                    [(shortlist, "_PREFERRED", NEVER), (shortlist, "_REQUIRED", re.compile("."))]),
    "W7 abstention never fires": ("test_W7_bare_remote_is_cannot_tell",
                                  [(flt, "_location_part", lambda part: "remote_us" if "remote" in part.lower() else real_part(part))]),
    "W9 'sponsor' counts as an offer": ("test_W9_sponsor_word_is_not_an_offer",
                                        [(flt, "visa", lambda c: ("offered", c) if "sponsor" in c.lower() else ("silent", ""))]),
    "W10 two location bonuses": ("test_W10_one_location_bonus", [(flt, "evaluate", w10_evaluate)]),
}
real_part = flt._location_part


def run(test_name):
    suite = unittest.defaultTestLoader.loadTestsFromName(f"WrongVersions.{test_name}", T)
    return unittest.TextTestRunner(stream=open("/dev/null", "w"), verbosity=0).run(suite).wasSuccessful()


def main():
    caught = 0
    for name, (test_name, patches) in SABOTAGE.items():
        if not run(test_name):
            sys.exit(f"{test_name} is red before sabotage; fix the code first")
        saved = [(mod, attr, getattr(mod, attr)) for mod, attr, _ in patches]
        for mod, attr, value in patches:
            setattr(mod, attr, value)
        try:
            green = run(test_name)
        finally:
            for mod, attr, value in saved:
                setattr(mod, attr, value)
        caught += not green
        print(f"{'RED (caught)' if not green else 'GREEN (MISSED)':15} {name:34} {test_name}")
    print(f"\n{caught}/{len(SABOTAGE)} wrong versions caught")
    sys.exit(0 if caught == len(SABOTAGE) else 1)


if __name__ == "__main__":
    main()
