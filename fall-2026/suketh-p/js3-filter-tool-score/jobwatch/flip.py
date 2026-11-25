"""Chapter 7's challenge to the student's claim labels: "Label each row yourself first. Then ask
Claude to find the sentence that would change your label, and record whether it did."

For each shortlisted posting, Claude gets the posting text and every claim with the student's label
and note. It is asked for the one sentence of the posting that would most change each label, or
none. The code checks that each proposed sentence appears in the posting word for word. Whether a
sentence changes a label is the student's decision, recorded separately. Claude is called the way
the claims were (claims.claude_code_send: `claude -p`, no tools, no settings, no MCP, no session,
from an empty folder). The prompt is prompts/flip-v1.md, written by Claude Code."""

import json
import re
from pathlib import Path

from jobwatch import claims, evidence

PROMPT_PATH = Path(__file__).resolve().parent.parent / "prompts" / "flip-v1.md"
ARGUES_FOR = ("supported", "contradicted", "insufficient")


class FlipError(Exception):
    pass


def build_prompt(item, rows, labels, path=PROMPT_PATH):
    """rows: [(claim_id, claims.jsonl row)]; labels: {claim_id: {"label", "note"}}."""
    system, user = claims.prompt_parts(path)
    listed = []
    for claim_id, row in rows:
        quote = json.dumps(row["quote"], ensure_ascii=False) if row["quote"] else "(none)"
        line = (f"- {claim_id} ({row['kind']}). Claim: {row['claim']} Quote given: {quote}. "
                f"The person's label: {labels[claim_id]['label']}.")
        if labels[claim_id]["note"]:
            line += f" Their note: {labels[claim_id]['note']}"
        listed.append(line)
    filled = (user.replace("{board}", item.board).replace("{key}", item.key)
              .replace("{captured_at}", item.captured_at).replace("{title}", item.title)
              .replace("{location}", item.location or "(blank)")
              .replace("{text}", evidence.plain(item.description)).replace("{claims}", "\n".join(listed)))
    return system, filled


def parse_reply(stdout, ids):
    try:
        out = json.loads(stdout)
    except ValueError:
        raise FlipError("claude -p did not print JSON") from None
    if not isinstance(out, dict) or out.get("is_error") or not isinstance(out.get("result"), str):
        raise FlipError("claude -p reported an error instead of a reply")
    text = out["result"].strip()
    fenced = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", text, flags=re.S)
    if fenced:
        text = fenced.group(1)
    try:
        challenges = json.loads(text)["challenges"]
    except (ValueError, KeyError, TypeError):
        raise FlipError("the reply is not the requested JSON shape") from None
    if not isinstance(challenges, list):
        raise FlipError("challenges is not a list")
    seen = {}
    for c in challenges:
        if not isinstance(c, dict) or c.get("id") not in ids or c["id"] in seen:
            raise FlipError(f"a challenge names no claim, an unknown claim or a repeated one: {c!r}")
        if c.get("argues_for") not in ARGUES_FOR + (None,):
            raise FlipError(f"argues_for must be a label or null: {c!r}")
        if c.get("sentence") is not None and not isinstance(c["sentence"], str):
            raise FlipError(f"sentence must be text or null: {c!r}")
        seen[c["id"]] = c
    if set(seen) != set(ids):
        raise FlipError(f"not every claim was challenged: missing {sorted(set(ids) - set(seen))}")
    return [seen[i] for i in ids]


def checked(text, challenges, labels):
    """labels: {claim_id: the student's label}. A challenge proposes a change only when its sentence
    is in the posting word for word and it argues for a different label."""
    rows = []
    for c in challenges:
        check = evidence.check_quote(text, c.get("sentence"))
        proposes = check == "quote found" and c.get("argues_for") is not None and c["argues_for"] != labels[c["id"]]
        rows.append({**c, "label": labels[c["id"]], "sentence_check": check, "proposes_a_change": proposes})
    return rows


def apply_decisions(labels, changes):
    """The student's decisions on the challenge, applied to their first labels (which are not touched).
    Each change names claim IDs, the label they start from and the label they end at, and a note; a
    change that does not start from the student's label is refused, and a claim changes at most once."""
    final = {claim_id: {**entry, "label_before_challenge": entry["label"], "changed_by": None}
             for claim_id, entry in labels.items()}
    for n, change in enumerate(changes):
        if change["to"] not in ARGUES_FOR:
            raise ValueError(f"unknown label {change['to']!r}")
        for claim_id in change["ids"]:
            if claim_id not in final:
                raise ValueError(f"{claim_id} is not one of the claims")
            if final[claim_id]["changed_by"] is not None:
                raise ValueError(f"{claim_id} is changed twice")
            if final[claim_id]["label"] != change["from"]:
                raise ValueError(f"{claim_id} is {final[claim_id]['label']}, not {change['from']}")
            final[claim_id] = {**final[claim_id], "label": change["to"], "note": change["note"],
                               "note_before_challenge": final[claim_id]["note"], "changed_by": n}
    return final
