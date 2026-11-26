"""The plausible-but-wrong versions from FILTER.md §5, written out so the tests can show they fail.
Never imported by the agent itself."""
from js3.text import norm, words


def substring_score(posting, flt):
    """WV1: `phrase in title` instead of whole-word matching."""
    t = (posting.get("title") or "").lower()
    role = any(p in t for p in flt["role_title"]["phrases"])
    veto = any(f" {p} " in f" {t} " for p in flt["seniority_veto_title"])
    s = flt["role_title"]["weight"] if role else 0
    return {"score": s, "decision": "keep" if s >= flt["threshold"] and not veto else "reject"}


def count_rank(postings, flt):
    """WV2: rank by how many times topic words appear; no cap, no veto."""
    def hits(p):
        w = words(p.get("title", "") + " " + p.get("text", ""))
        return sum(w.count(x) for x in flt["topic_text"]["phrases"] if " " not in x)
    return sorted(postings, key=lambda p: -hits(p))


def absence_as_support_label(claim, posting):
    """WV3: an experience/degree claim is 'supported' when the text shows nothing against it."""
    if claim["kind"] in ("experience", "degree") and "5+" not in (posting.get("text") or "") \
            and "phd" not in norm(posting.get("text")):
        return "supported"
    return "insufficient"
