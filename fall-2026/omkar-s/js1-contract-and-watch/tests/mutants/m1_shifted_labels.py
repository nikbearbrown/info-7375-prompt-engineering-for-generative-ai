"""WRONG VERSION 1 (CONTRACT.md): verdicts computed correctly but paired with the
neighbouring posting (off-by-one). Plausible bug: zip(postings, verdicts[1:] + verdicts[:1])."""
from jsagent import rule, watch


def apply():
    def attach_verdicts(new_postings, resume):
        verdicts = [rule.judge(p, resume) for p in new_postings]
        verdicts = verdicts[1:] + verdicts[:1]
        return [{"posting_id": p["id"], "title": p.get("title"), "absolute_url": p.get("absolute_url"),
                 "rule": v} for p, v in zip(new_postings, verdicts)]
    watch.attach_verdicts = attach_verdicts
