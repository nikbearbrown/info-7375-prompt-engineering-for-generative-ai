"""Grade one question against its frozen gold record.

What the reader sees (`shown`):
  ANSWERED  the checker passed an answer, so it reaches the reader
  REFUSED   the answerer said "not in the documents"
  REJECTED  the answerer gave an answer but the checker blocked it
  BROKEN    the reply broke the contract (not JSON, missing fields, ...)

Grade against gold:
  WRONG    the reader saw an answer that is not the gold answer (worst outcome)
  MISSED   the gold answer exists but the reader got nothing
  CAUGHT   gold says "not in the documents"; the answerer answered anyway and the checker blocked it
  CORRECT  answered with the gold text in the quote, or correctly refused
"""

GRADE_ORDER = {"WRONG": 0, "MISSED": 1, "CAUGHT": 2, "CORRECT": 3}


def shown(answer, check_result) -> str:
    if answer is None:
        return "BROKEN"
    if answer.status == "not_in_documents":
        return "REFUSED"
    return "ANSWERED" if check_result.passed else "REJECTED"


def grade(gold: dict, answer, shown_as: str) -> str:
    if gold["gold_status"] == "not_in_documents":
        if shown_as == "ANSWERED":
            return "WRONG"
        if shown_as == "REJECTED":
            return "CAUGHT"
        return "CORRECT"
    if shown_as != "ANSWERED":
        return "MISSED"
    quote = " ".join(answer.quote.split()).lower()
    hits = all(" ".join(term.split()).lower() in quote for term in gold["gold_must_contain"])
    return "CORRECT" if hits else "WRONG"
