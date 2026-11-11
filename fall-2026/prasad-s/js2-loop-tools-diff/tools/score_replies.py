"""Score a folder of saved Claude replies (experiments/scoring.md). Read-only.

For each reply listed in FOLDER/metadata.json, loads its posting from the
"source" in experiments/selected_ids.json and runs the agent's own §6
validator (agent.replies.validate_reply) with the §1 persona. One line per
reply: file, accepted or rejected (with reasons), judgment (Claude), the hand
label (with --labels), and PASS or FAIL. A reply PASSES only if the validator
accepts it AND its verdict equals the hand label; a rejected reply is a FAIL.
Then totals. For sampling keys (<posting_id>_r<N>) it also prints, per
posting, the verdicts of the repeats, how many were accepted, and whether
the RESUME_FIELD and POSTING_FIELD lines were identical across the repeats.
With --split, only the replies whose metadata "split" equals that value are
scored (sampling replies have no split, so --split is refused for them).

Usage:
    python3.13 tools/score_replies.py FOLDER [--labels FILE] [--split development|held_out]
"""

import argparse
import json
import re
import sys
from pathlib import Path

JS1 = Path(__file__).resolve().parents[1]
if str(JS1) not in sys.path:
    sys.path.insert(0, str(JS1))

from agent.errors import Refusal, RunError  # noqa: E402
from agent.persona import check_persona, load_persona  # noqa: E402
from agent.replies import CLAUDE_LABEL, METADATA_KEYS, load_metadata, validate_reply  # noqa: E402
from agent.state import parse_board_response  # noqa: E402

SELECTED_IDS = JS1 / "experiments" / "selected_ids.json"
PERSONA = JS1 / "resume_persona.json"
SAMPLING_KEY = re.compile(r"(\d+)_r(\d+)")
FIELD_LINES = ("RESUME_FIELD: ", "POSTING_FIELD: ")
SPLITS = ("development", "held_out")


class ScoreError(Exception):
    """The folder cannot be scored (bad metadata, unknown posting, missing label)."""


def load_postings(selected_ids_path):
    """posting_id -> posting, from the "source" named in selected_ids.json (relative to JS1)."""
    selected = json.loads(Path(selected_ids_path).read_text(encoding="utf-8"))
    source = selected["source"]
    raw = (Path(selected_ids_path).resolve().parents[1] / source).read_bytes()
    return source, {posting["posting_id"]: posting for posting in parse_board_response(raw)}


def load_labels(path, source):
    """posting_id -> hand verdict. The labels must come from the same source as the postings."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    labels = data.get("labels") if isinstance(data, dict) else None
    if not isinstance(labels, list):
        raise ScoreError(f"{path} is not a hand-labels file: no 'labels' list")
    if data.get("source") != source:
        raise ScoreError(f"{path} labels {data.get('source')!r}, but the postings come from {source!r}")
    return {label["id"]: label["verdict"] for label in labels}


def check_entry(key, entry, folder):
    """(reply text or None, problems). Mirrors the agent's metadata checks for one reply."""
    if not isinstance(entry, dict):
        return None, [f"metadata.json entry for {key} is not an object"]
    problems = [f"metadata.json entry for {key} has no {name}"
                for name in METADATA_KEYS if not isinstance(entry.get(name), str) or not entry.get(name)]
    # Decision 2026-10-29 (mine): the reply file is <metadata key>.txt, as the agent requires <posting_id>.txt.
    expected = f"{key}.txt"
    if isinstance(entry.get("file"), str) and entry["file"] != expected:
        problems.append(f"metadata.json lists {entry['file']!r} for {key}; the reply must be {expected}")
    if problems:
        return None, problems
    path = Path(folder) / expected
    if not path.is_file():
        return None, [f"{expected} is listed in metadata.json but was not saved"]
    try:
        return path.read_bytes().decode("utf-8"), []
    except (OSError, UnicodeDecodeError) as exc:
        return None, [f"{expected} cannot be read as UTF-8: {exc}"]


def select_split(metadata, split):
    """The metadata entries whose "split" equals split. Every entry must have a split."""
    for key, entry in sorted(metadata.items()):
        if not isinstance(entry, dict) or "split" not in entry:
            sampling = isinstance(entry, dict) and entry.get("set") == "sampling"
            raise ScoreError(f"--split needs a 'split' in every metadata entry; {key} has none"
                             + (" (sampling replies have no split)" if sampling else ""))
    return {key: entry for key, entry in metadata.items() if entry["split"] == split}


def field_lines(text, prefix):
    """The reply's lines that start with this §6 label, in order (also for rejected replies)."""
    return [] if text is None else [line for line in text.split("\n") if line.startswith(prefix)]


def score(folder, metadata, persona, postings, labels=None):
    """(output lines, totals). labels is posting_id -> hand verdict, or None."""
    rows = []
    for key in sorted(metadata):
        entry = metadata[key]
        posting_id = entry.get("posting_id", key) if isinstance(entry, dict) else key
        if posting_id not in postings:
            raise ScoreError(f"{key}: posting_id {posting_id} is not in the source board response")
        if labels is not None and posting_id not in labels:
            raise ScoreError(f"{key}: posting_id {posting_id} has no hand label")
        text, reasons = check_entry(key, entry, folder)
        if text is not None:
            result = validate_reply(text, persona, postings[posting_id])
            reasons = result.reasons
            verdict = result.parsed["verdict"] if result.ok else "rejected"
        else:
            verdict = "rejected"
        rows.append({"key": key, "posting_id": posting_id, "text": text, "verdict": verdict, "reasons": reasons})

    totals = {"replies": len(rows), "accepted": 0, "rejected": 0, "pass": 0 if labels is not None else None}
    lines = []
    for row in rows:
        accepted = row["verdict"] != "rejected"
        totals["accepted" if accepted else "rejected"] += 1
        parts = [f"{row['key']}.txt", "accepted" if accepted else "rejected", f"{CLAUDE_LABEL}: {row['verdict']}"]
        if labels is not None:
            hand = labels[row["posting_id"]]
            passed = accepted and row["verdict"] == hand
            totals["pass"] += passed
            parts += [f"hand: {hand}", "PASS" if passed else "FAIL"]
        lines.append("  ".join(parts))
        if not accepted:
            lines.extend(f"    - {reason}" for reason in row["reasons"])

    if labels is None:
        score_text = "PASS: n/a (no --labels)"
    else:
        rate = 100 * totals["pass"] / totals["replies"] if totals["replies"] else 0
        score_text = f"PASS: {totals['pass']}  pass rate: {totals['pass']}/{totals['replies']} = {rate:.0f}%"
    lines.append(f"replies: {totals['replies']}  accepted: {totals['accepted']}  "
                 f"rejected: {totals['rejected']}  {score_text}")
    lines.extend(sampling_lines(rows))
    return lines, totals


def sampling_lines(rows):
    """Per-posting repeat summary for keys like 6348471_r2; empty when there are none."""
    groups = {}
    for row in rows:
        match = SAMPLING_KEY.fullmatch(row["key"])
        if match:
            groups.setdefault(row["posting_id"], []).append((int(match.group(2)), row))
    if not groups:
        return []
    lines = ["", "per posting (sampling repeats):"]
    for posting_id in sorted(groups, key=int):
        repeats = [row for _, row in sorted(groups[posting_id], key=lambda pair: pair[0])]
        accepted = sum(row["verdict"] != "rejected" for row in repeats)
        same = {prefix: all(field_lines(row["text"], prefix) == field_lines(repeats[0]["text"], prefix)
                            for row in repeats)
                for prefix in FIELD_LINES}
        lines.append(f"{posting_id}  verdicts: {', '.join(row['verdict'] for row in repeats)}  "
                     f"accepted: {accepted}/{len(repeats)}  "
                     f"RESUME_FIELD lines identical: {'yes' if same['RESUME_FIELD: '] else 'no'}  "
                     f"POSTING_FIELD lines identical: {'yes' if same['POSTING_FIELD: '] else 'no'}")
    return lines


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3.13 tools/score_replies.py",
                                     description="Score saved Claude replies against experiments/scoring.md.")
    parser.add_argument("folder", help="folder with the reply .txt files and their metadata.json")
    parser.add_argument("--labels", metavar="FILE", help="hand-labels file (for PASS/FAIL)")
    parser.add_argument("--split", choices=SPLITS, help="score only the replies with this metadata split")
    args = parser.parse_args(argv)
    try:
        metadata, error = load_metadata(args.folder)
        if error:
            raise ScoreError(error)
        persona = load_persona(PERSONA)
        check_persona(persona)  # the same résumé check the agent runs before judging
        source, postings = load_postings(SELECTED_IDS)
        labels = load_labels(args.labels, source) if args.labels else None
        header = []
        if args.split:
            selected = select_split(metadata, args.split)
            header = [f"split: {args.split} ({len(selected)} of {len(metadata)} replies in metadata.json)"]
            metadata = selected
        lines, _ = score(args.folder, metadata, persona, postings, labels)
        lines = header + lines
    except (OSError, ValueError, KeyError, TypeError, RunError, Refusal, ScoreError) as exc:
        print(f"error: cannot score {args.folder}: {exc}", file=sys.stderr)
        return 1
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
