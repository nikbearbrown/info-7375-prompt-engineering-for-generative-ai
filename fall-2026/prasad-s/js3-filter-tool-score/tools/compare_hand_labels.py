"""Compare hand labels with the rule code (agent.rule.judge), condition by condition.

For each label in the labels file, loads that posting from the board response
named in the file's "source" (relative to JS1), runs the rule with the §1
persona, and prints one line: id, the hand C1/C2/C3/verdict, the rule's
C1/C2/C3/verdict, and "agree" or "DISAGREE on <which>". Each disagreement is
followed by the rule's matched terms for that condition. Ends with totals.
Read-only: writes no files.

Usage:
    python3.13 tools/compare_hand_labels.py [LABELS_FILE]
"""

import argparse
import json
import sys
from pathlib import Path

JS1 = Path(__file__).resolve().parents[1]
if str(JS1) not in sys.path:
    sys.path.insert(0, str(JS1))

from agent.errors import Refusal, RunError  # noqa: E402
from agent.persona import check_persona, load_persona  # noqa: E402
from agent.rule import judge  # noqa: E402
from agent.state import parse_board_response  # noqa: E402

DEFAULT_LABELS = JS1 / "experiments" / "hand_labels_development.json"
PERSONA = JS1 / "resume_persona.json"
CONDITIONS = ("C1", "C2", "C3")
FIELDS = CONDITIONS + ("verdict",)
VERDICTS = ("relevant", "not_relevant")
POSTING_FIELD = {"C1": "title", "C2": "location.name", "C3": "content"}


def load_postings(source):
    """posting_id -> posting, from a saved board response (§4 step 1 via the agent's parser)."""
    return {posting["posting_id"]: posting for posting in parse_board_response(Path(source).read_bytes())}


def check_label(label):
    """The label's id, or ValueError if it is not a usable hand label."""
    posting_id = label.get("id") if isinstance(label, dict) else None
    if not isinstance(posting_id, str) or not posting_id:
        raise ValueError(f"label without a string id: {label!r}")
    for name in CONDITIONS:
        if not isinstance(label.get(name), bool):
            raise ValueError(f"label {posting_id}: {name} must be true or false")
    if label.get("verdict") not in VERDICTS:
        raise ValueError(f"label {posting_id}: verdict must be one of {VERDICTS}")
    return posting_id


def rule_labels(justification, verdict):
    """The rule's C1/C2/C3/verdict in the same shape as a hand label."""
    values = {name: justification["conditions"][name]["result"] for name in CONDITIONS}
    values["verdict"] = verdict
    return values


def show(values):
    return "  ".join([*(f"{name}={str(values[name]).lower()}" for name in CONDITIONS), values["verdict"]])


def why(name, label, justification):
    """Indented lines with the rule's matched terms for one disagreeing field."""
    if name == "verdict":
        failing = justification["failing_conditions"]
        return [f"    verdict: rule failing conditions: {', '.join(failing) if failing else 'none'}"]
    condition = justification["conditions"][name]
    field = POSTING_FIELD[name]
    found = [entry["matched"] for entry in justification["posting_fields"] if entry["field"] == field]
    pairs = [f"{term!r} as {text!r}" for term, text in zip(condition["matched_resume_values"], found)]
    lines = [f"    {name}: rule matched in {field}: {', '.join(pairs) if pairs else 'nothing'}"]
    if name == "C3":
        lines.append(f"    C3: rule found {condition['distinct_skills_found']} distinct skill(s), "
                     f"needs {condition['distinct_skills_needed']}; "
                     f"content present: {str(condition['content_present']).lower()}")
        if "skills_found" in label:
            lines.append(f"    C3: hand skills_found: {label['skills_found']!r}")
    else:
        lines.append(f"    {name}: rule compared {field}: {condition['posting_value']!r}")
    return lines


def compare(labels_doc, persona, postings_for):
    """(output lines, totals). postings_for(source) returns posting_id -> posting."""
    labels = labels_doc.get("labels") if isinstance(labels_doc, dict) else None
    source = labels_doc.get("source") if isinstance(labels_doc, dict) else None
    if not isinstance(labels, list) or not isinstance(source, str) or not source:
        raise ValueError("not a hand-labels file: needs a 'source' string and a 'labels' list")
    postings = postings_for(source)
    totals = {"agree": 0, "disagree": 0, **{name: 0 for name in FIELDS}}
    lines = []
    for label in labels:
        posting_id = check_label(label)
        if posting_id not in postings:
            raise ValueError(f"posting_id {posting_id} is not in {source}")
        verdict, justification = judge(postings[posting_id], persona)
        rule = rule_labels(justification, verdict)
        differ = [name for name in FIELDS if label[name] != rule[name]]
        line = f"{posting_id}  hand: {show(label)}  rule: {show(rule)}"
        if not differ:
            totals["agree"] += 1
            lines.append(f"{line}  agree")
            continue
        totals["disagree"] += 1
        lines.append(f"{line}  DISAGREE on {', '.join(differ)}")
        for name in differ:
            totals[name] += 1
            lines.extend(why(name, label, justification))
    lines.append(f"labels: {len(labels)}  agree: {totals['agree']}  disagree: {totals['disagree']}  "
                 + "  ".join(f"{name} differs: {totals[name]}" for name in FIELDS))
    return lines, totals


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3.13 tools/compare_hand_labels.py",
                                     description="Hand labels vs the rule code, condition by condition.")
    parser.add_argument("labels", nargs="?", default=str(DEFAULT_LABELS),
                        help="hand-labels file (default: experiments/hand_labels_development.json)")
    args = parser.parse_args(argv)
    try:
        with open(args.labels, encoding="utf-8") as fh:
            labels_doc = json.load(fh)
        persona = load_persona(PERSONA)
        check_persona(persona)  # the same résumé check the agent runs before judging
        lines, _ = compare(labels_doc, persona, lambda source: load_postings(JS1 / source))
    except (OSError, ValueError, KeyError, TypeError, RunError, Refusal) as exc:
        print(f"error: cannot compare {args.labels}: {exc}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
