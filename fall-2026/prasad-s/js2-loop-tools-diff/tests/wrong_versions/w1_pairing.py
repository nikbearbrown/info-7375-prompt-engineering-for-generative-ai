"""DELIBERATELY WRONG — CONTRACT.md §5 W1 (mismatched pairing). NEVER USED BY THE AGENT.

Both functions compute every verdict correctly with the real agent code,
then attach verdicts to the wrong posting_id. Each one is wrong in one leg
only, so a §5 check has to look at both legs to catch both.

Interface: build_records(postings, persona, outputs_dir) -> list of §2
records, where postings come from agent.state.parse_board_response.
"""

from pathlib import Path

from agent.replies import CLAUDE_LABEL, claude_judgment, load_metadata, validate_reply
from agent.rule import judge


def _record(posting, rule_verdict, rule_justification, claude_verdict, claude_justification):
    location = posting.get("location")
    name = location.get("name") if isinstance(location, dict) else None
    return {
        "posting_id": posting["posting_id"],
        "title": posting.get("title"),
        "absolute_url": posting.get("absolute_url"),
        "location.name": name if isinstance(name, str) else "not stated",
        "rule_verdict": rule_verdict,
        "rule_justification": rule_justification,
        "claude_verdict_label": CLAUDE_LABEL,
        "claude_verdict": claude_verdict,
        "claude_justification": claude_justification,
    }


def build_records_sorted_independently(postings, persona, outputs_dir):
    """Rule leg wrong: postings sorted by id, verdicts sorted by label, then zipped.

    Claude's replies are still matched by posting_id, correctly.
    """
    metadata, metadata_error = load_metadata(outputs_dir)
    judged = [judge(posting, persona) for posting in postings]  # correct verdicts
    postings_sorted = sorted(postings, key=lambda posting: posting["posting_id"])
    judged_sorted = sorted(judged, key=lambda pair: pair[0])  # WRONG: sorted on its own
    records = []
    for posting, (verdict, justification) in zip(postings_sorted, judged_sorted):
        claude_verdict, claude_justification = claude_judgment(
            posting["posting_id"], posting, persona, outputs_dir, metadata, metadata_error
        )
        records.append(_record(posting, verdict, justification, claude_verdict, claude_justification))
    return records


def build_records_claude_by_file_order(postings, persona, outputs_dir):
    """Claude leg wrong: saved replies zipped with postings in file-name order.

    The rule leg is paired correctly. Each reply is validated against the
    posting it was zipped with, as a careless implementation would.
    """
    reply_files = sorted(Path(outputs_dir).glob("*.txt"))  # WRONG: file order, not posting_id
    records = []
    for posting, reply_path in zip(postings, reply_files):
        verdict, justification = judge(posting, persona)
        text = reply_path.read_text(encoding="utf-8")
        result = validate_reply(text, persona, posting)
        if result.ok:
            claude_verdict, claude_justification = result.parsed["verdict"], {"reply": text, "parsed": result.parsed}
        else:
            claude_verdict, claude_justification = "rejected", {"reply": text, "reasons": result.reasons}
        records.append(_record(posting, verdict, justification, claude_verdict, claude_justification))
    return records


VARIANTS = {
    "W1 rule leg: sorted independently": build_records_sorted_independently,
    "W1 Claude leg: replies by file order": build_records_claude_by_file_order,
}
