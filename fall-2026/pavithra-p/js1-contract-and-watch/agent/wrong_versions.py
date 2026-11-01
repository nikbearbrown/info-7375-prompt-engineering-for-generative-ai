"""The two plausible-but-wrong versions from CONTRACT.md, written as real code.

They are never used by the agent. tests/test_rule.py runs its checks against them and must catch both.
"""
from . import rule


def judge_all_wrong_pairing(jobs, resume):
    """Wrong version 1: verdicts computed in title order but paired with job IDs in the original order."""
    verdicts = [rule.judge(job, resume) for job in sorted(jobs, key=lambda j: j.get("title", ""))]
    for job, verdict in zip(jobs, verdicts):
        verdict.job_id = job["id"]
    return verdicts


def judge_without_reason(job, resume):
    """Wrong version 2: the verdict is right but the reason cites no posting field, résumé field or skill."""
    verdict = rule.judge(job, resume)
    verdict.reason = f"{verdict.verdict}. Looks like a good fit." if verdict.verdict == "Relevant" else \
        f"{verdict.verdict}. Not a good fit."
    verdict.matched_skills, verdict.resume_fields, verdict.posting_fields = [], [], []
    return verdict
