"""The three plausible-but-wrong filters named in FILTER.md section 4. Each takes the same arguments as
rule.judge and is built from the real rule's pieces, with one mistake. test_filter.py proves the CASES catch each."""
import re

from earlybird import rule


def _with(posting, verdict, check=None):
    return {"posting_id": posting["id"], "title": posting["title"], "verdict": verdict, "failed_check": check}


def no_seniority_rule(posting, resume):
    """W1: the seniority rule is missing, so 'Senior' and 'Staff' titles are kept."""
    out = rule.judge(posting, resume)
    if out["failed_check"] == "R2" and not re.search(r"years", posting.get("descriptionPlain", ""), re.I):
        return _with(posting, "relevant")
    return out


def training_is_a_topic_word(posting, resume):
    """W2: 'training' anywhere in the description counts as a role signal, so non-AI postings are kept."""
    out = rule.judge(posting, resume)
    if out["failed_check"] == "R1" and re.search(r"\btraining\b", posting.get("descriptionPlain", ""), re.I):
        return _with(posting, "relevant")
    return out


def ignores_clearance(posting, resume):
    """W3: the clearance rule is missing, so 'security clearance required' postings are kept."""
    out = rule.judge(posting, resume)
    if out["failed_check"] == "R5":
        return _with(posting, "relevant")
    return out


WRONG = {"W1 no seniority rule": no_seniority_rule, "W2 training as topic word": training_is_a_topic_word,
         "W3 ignores clearance": ignores_clearance}
