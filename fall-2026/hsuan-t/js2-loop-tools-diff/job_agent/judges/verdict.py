"""The one verdict shape from CONTRACT Out, shared by the rule judge and the Claude judge.

Both judges must produce the same fields (D12), and judge/kind must come from code, never from
the judge itself (Wrong version 5). Building verdicts only here keeps both promises in one place.
"""

RELEVANT = "relevant"
NOT_RELEVANT = "not_relevant"

# judge -> kind. The rule's output is a record anyone can recompute; Claude's is a judgment (R17, R18).
KINDS = {"rule": "record", "claude": "judgment"}


def line(posting_field: str, compared_to: str, result: str) -> dict:
    """One justification line: which posting field, compared with which résumé/profile field, and what came out."""
    return {"posting_field": posting_field, "compared_to": compared_to, "result": result}


def ok(judge: str, posting_id: int, verdict: str, justification: list[dict]) -> dict:
    return _make(judge, posting_id, "ok", None, verdict, justification)


def error(judge: str, posting_id: int, message: str) -> dict:
    """An error verdict is always not_relevant with an empty justification: read error_message, not the verdict."""
    return _make(judge, posting_id, "error", message, NOT_RELEVANT, [])


def _make(judge: str, posting_id: int, status: str, message: str | None, verdict: str, justification: list[dict]) -> dict:
    if judge not in KINDS:
        raise ValueError(f"unknown judge: {judge}")
    if verdict not in (RELEVANT, NOT_RELEVANT):
        raise ValueError(f"verdict must be relevant or not_relevant, got {verdict!r}")
    return {
        "posting_id": posting_id,
        "status": status,
        "error_message": message,
        "verdict": verdict,
        "judge": judge,
        "kind": KINDS[judge],
        "justification": justification,
    }
