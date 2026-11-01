"""Plant each CONTRACT wrong version into the code and show the test suite fails on it.

Usage: python3 tests/wrong_versions.py
Each wrong version is a monkeypatch applied only for that run; the real code is unchanged.
"""
import pathlib
import sys
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from jobwatch import claude_judge, rule  # noqa: E402

real_judge, real_check_title, real_check_location = rule.judge, rule.check_title, rule.check_location
real_judge_all, real_validate = rule.judge_all, claude_judge.validate


def wv1_labels_by_position():
    """Verdicts computed on a sorted copy, then attached to the input list by position."""
    def judge_all(postings, resume):
        verdicts = [real_judge(p, resume)["verdict"] for p in sorted(postings, key=lambda p: p["title"])]
        out = []
        for p, v in zip(postings, verdicts):
            j = real_judge(p, resume)
            j["verdict"] = v
            out.append(j)
        return out
    rule.judge_all = judge_all

    def validate(text, posting, resume):
        """Validator that ignores a posting_id mismatch, so a reply for another posting attaches here."""
        v = real_validate(text, posting, resume)
        if v["status"] == "invalid" and all(e.startswith("posting_id") for e in v["errors"]):
            import json
            d = json.loads(text)
            return {"status": "valid", "verdict": d["verdict"], "resume_fields": d["resume_fields"],
                    "posting_fields": d["posting_fields"], "reason": d["reason"], "raw": text}
        return v
    claude_judge.validate = validate


def wv2_cites_nothing():
    """Correct verdict, empty justification; validator accepts empty citations."""
    def judge(p, r):
        j = real_judge(p, r)
        j.update(resume_fields={}, posting_fields={}, reason="good fit")
        return j
    rule.judge = judge
    rule.judge_all = lambda ps, r: [judge(p, r) for p in ps]

    def validate(text, posting, resume):
        v = real_validate(text, posting, resume)
        if v["status"] == "invalid" and all(("non-empty" in e or "does not exist" in e) for e in v["errors"]):
            return {"status": "valid", "verdict": "relevant", "resume_fields": [], "posting_fields": [],
                    "reason": "", "raw": text}
        return v
    claude_judge.validate = validate


def wv3_loose_substrings():
    """'product' and 'manager' anywhere in the title; 'us' anywhere in the location."""
    def check_title(p):
        t = (p.get("title") or "").lower()
        ok = "product" in t and ("manager" in t or "analyst" in t or "strategy" in t or "owner" in t
                                 or "operations" in t)
        return {"pass": ok, "matched": "product" if ok else None, "reason": "loose"}

    def check_location(p):
        r = real_check_location(p)
        if not r["pass"] and "us" in ((p.get("location") or {}).get("name") or "").lower():
            return {"pass": True, "via": "location", "field": "location.name",
                    "value": p["location"]["name"], "reason": "loose"}
        return r
    rule.check_title, rule.check_location = check_title, check_location


def run_suite():
    suite = unittest.defaultTestLoader.discover(str(ROOT / "tests"), top_level_dir=str(ROOT / "tests"))
    res = unittest.TextTestRunner(stream=open("/dev/null", "w"), verbosity=0).run(suite)
    return res.testsRun, len(res.failures) + len(res.errors), [t.id().split(".", 1)[1] for t, _ in res.failures + res.errors]


def reset():
    rule.judge, rule.check_title, rule.check_location = real_judge, real_check_title, real_check_location
    rule.judge_all, claude_judge.validate = real_judge_all, real_validate


if __name__ == "__main__":
    reset()
    n, bad, _ = run_suite()
    print(f"correct code: {n} tests, {bad} failing")
    caught_all = bad == 0
    for name, plant in (("wrong version 1 (labels by position)", wv1_labels_by_position),
                        ("wrong version 2 (justification cites nothing)", wv2_cites_nothing),
                        ("wrong version 3 (loose substring match)", wv3_loose_substrings)):
        reset()
        plant()
        n, bad, which = run_suite()
        caught_all &= bad > 0
        print(f"{name}: {bad} of {n} tests fail -> {'CAUGHT' if bad else 'NOT CAUGHT'}")
        for t in which:
            print(f"    {t}")
    reset()
    sys.exit(0 if caught_all else 1)
