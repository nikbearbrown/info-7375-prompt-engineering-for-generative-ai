"""The human gate. A person sees the exact view and approves, refuses, or defers.

The decision is bound to a SHA-256 of the view text. An approval recorded for a
different view (a stale decision file, or a changed result) becomes a deferral,
and nothing is written. Only an approval matching the view exports a report.
"""

import hashlib
import json
from dataclasses import dataclass
from pathlib import Path

from .config import SOURCE_SHA256

DECISIONS = ("approve", "refuse", "defer")


@dataclass
class Decision:
    decision: str          # approve | refuse | defer | not_requested
    approver: str
    note: str
    bound_hash: str        # the view hash the decision was made for
    reason: str = ""


def _cell(value):
    text = "" if value is None else str(value)
    return text.replace("|", "\\|").replace("\n", " ").replace("\r", " ")


def _model_text(value):
    """Model-written text on one line, so it can't imitate a system line (review finding 5)."""
    flat = " ".join(str(value or "").split())
    return flat.replace("**", "").replace("#", "")


def result_digest(result):
    """SHA-256 of every kept row, so rows past the display limit still bind the view (finding 6)."""
    payload = json.dumps({"columns": list(result.columns), "rows": [list(r) for r in result.rows],
                          "total_rows": result.total_rows}, default=str, ensure_ascii=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def table(columns, rows, limit):
    lines = ["| " + " | ".join(columns) + " |", "|" + "---|" * len(columns)]
    for row in rows[:limit]:
        lines.append("| " + " | ".join(_cell(v) for v in row) + " |")
    return "\n".join(lines)


def build_view(question, proposal, answer, evidence, check, source_sha=SOURCE_SHA256,
               answer_limit=25, evidence_limit=20):
    """The exact text a person sees at the gate. Deterministic for the same inputs.

    Lines starting with a bold label are written by SponsorSQL. Text the model
    wrote is flattened to one line and introduced as model-written.
    """
    parts = [
        "# SponsorSQL answer for review",
        "",
        f"**Question:** {_model_text(question)}",
        f"**Source checksum recorded in this database:** {source_sha}",
        f"**Full answer SHA-256 (all rows):** {result_digest(answer)}",
        f"**Full evidence SHA-256 (rows kept):** {result_digest(evidence)}",
        "",
        "Model-written interpretation (not checked by SponsorSQL): " + _model_text(proposal.interpretation),
    ]
    if proposal.limits:
        parts.append("Model-written limits: " + _model_text("; ".join(proposal.limits)))
    parts += ["", "## Answer", f"{answer.total_rows} row(s)"
              + (f", first {answer_limit} shown" if answer.total_rows > answer_limit else ""),
              "", table(answer.columns, answer.rows, answer_limit),
              "", "## SQL that produced the answer", "```sql", proposal.sql, "```",
              "", "## Matching rows (evidence)",
              f"{evidence.total_rows} matching row(s)"
              + (f", first {evidence_limit} shown" if evidence.total_rows > evidence_limit else ""),
              "", table(evidence.columns, evidence.rows, evidence_limit),
              "", "```sql", proposal.rows_sql, "```"]
    if check:
        parts += ["", f"**SponsorSQL count-versus-rows check:** {check}"]
    parts += ["", "An LCA filing is not a job offer, a visa approval, or a promise of sponsorship."]
    return "\n".join(parts) + "\n"


def view_hash(view_text):
    return hashlib.sha256(view_text.encode("utf-8")).hexdigest()


def decide(view_text, mode, decision_file=None, input_fn=input, output_fn=print) -> Decision:
    current = view_hash(view_text)
    if mode == "none":
        return Decision("not_requested", "", "evaluation run: answer not released", current)
    if mode == "file":
        try:
            data = json.loads(Path(decision_file).read_text(encoding="utf-8"))
        except (OSError, TypeError, json.JSONDecodeError) as exc:
            return Decision("defer", "", "", current, f"no readable decision file ({exc})")
        if not isinstance(data, dict):
            return Decision("defer", "", "", current, "decision file is not a JSON object")
        if data.get("view_hash") != current:
            return Decision("defer", data.get("approver", ""), data.get("note", ""),
                            data.get("view_hash", ""), "decision was made for a different view")
        choice = data.get("decision")
        if choice not in DECISIONS:
            return Decision("defer", data.get("approver", ""), "", current, "unknown decision")
        return Decision(choice, data.get("approver", ""), data.get("note", ""), current)
    if mode == "interactive":
        output_fn(view_text)
        output_fn(f"View SHA-256: {current}")
        while True:
            answer = input_fn("Approve, refuse, or defer this answer? [a/r/d]: ").strip().lower()
            choice = {"a": "approve", "r": "refuse", "d": "defer"}.get(answer[:1])
            if choice:
                note = input_fn("Optional note (Enter to skip): ").strip()
                return Decision(choice, "interactive terminal user", note, current)
            output_fn("Please type a, r, or d.")
    raise ValueError(f"unknown gate mode {mode}")


def export_report(outputs_dir, run_id, view_text, decision):
    """The only write action. Called only after a matching approval."""
    if decision.decision != "approve" or decision.bound_hash != view_hash(view_text):
        raise PermissionError("export requires an approval bound to this exact view")
    folder = Path(outputs_dir) / "answers"
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{run_id}.md"
    path.write_text(view_text + "\n---\n"
                    + f"Approved by: {decision.approver}\n"
                    + f"Note: {decision.note or '(none)'}\n"
                    + f"View SHA-256: {decision.bound_hash}\n", encoding="utf-8")
    return path
