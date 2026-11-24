"""Interactive blind labeler for the claim sheet (stdlib only).

Usage (from js3-filter-tool-score/):
    .venv/bin/python tools/label_claims.py labels/claims-sheet.csv
    .venv/bin/python tools/label_claims.py labels/claims-sheet.csv --correct 7

For each claim it shows the posting, the kind, the claim, the quote and whether the quote was
found in the posting text, then the full paragraph that holds the quote (or the first 800
characters when the quote is empty or was not found). Keys: s supported, c contradicted,
i insufficient, f full text, k skip, q quit. Definitions are FILTER.md's "Evidence rules".

BLIND: reads only the sheet and labels/claims-texts/<posting_id>.txt, never anything under
out*/ (Claude's proposed labels live in out/claims-key.json). WRITE-ONCE: a non-blank my_label
is never overwritten; --correct ROW keeps the old label, note and time in the note. Writes are
atomic (tools/label.py's writer).
"""

import argparse
import csv
import sys
from pathlib import Path

if __package__ in (None, ""):
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from tools.label import (LabelError, PREVIEW_CHARS, TEXT_MARKER, _find, _now, _with_labeled_at,  # noqa: E402
                         guard_path, page_text, write_sheet_atomic)

LABEL_KEYS = {"s": "supported", "c": "contradicted", "i": "insufficient"}
TEXT_DIR = "claims-texts"
DEFINITIONS = ("supported: a span quoted verbatim from the posting asserts the claim (not just mentions the word)",
               "contradicted: a quoted span asserts the opposite of the claim",
               "insufficient: no span asserts it either way, or only a mention (nice to have, team description, boilerplate)")


# ---------------------------------------------------------------- sheet and text

def read_sheet(sheet: Path) -> tuple[list[str], list[dict]]:
    guard_path(sheet, sheet)
    with open(sheet, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            raise LabelError(f"{sheet} is empty") from None
        rows = [dict(zip(header, values)) for values in reader if values]
    for needed in ("row", "posting_id", "claim", "quote", "my_label", "note"):
        if needed not in header:
            raise LabelError(f"{sheet} has no {needed!r} column")
    if "proposed_label" in header:
        raise LabelError(f"{sheet} shows proposed_label; refusing to label an unblind sheet")
    return header, rows


def text_blocks(sheet: Path, posting_id: str) -> list[str]:
    """The posting's paragraphs from labels/claims-texts/<posting_id>.txt (inside the sheet's folder)."""
    sheet_dir = Path(sheet).resolve().parent
    path = guard_path(sheet_dir / TEXT_DIR / f"{posting_id}.txt", sheet)
    try:
        path.relative_to(sheet_dir)
    except ValueError:
        raise LabelError(f"refusing posting_id {posting_id!r}: its text file is outside {sheet_dir}") from None
    try:
        full = path.read_text(encoding="utf-8")
    except FileNotFoundError:
        return []
    body = full.split(TEXT_MARKER, 1)[1] if TEXT_MARKER in full else full
    return [b for b in body.strip().split("\n\n") if b.strip()]


def context_for(blocks: list[str], quote: str) -> tuple[str, str]:
    """(what is shown, why): the paragraph(s) holding the quote, else the first 800 characters."""
    joined = " ".join(blocks)
    first = joined[:PREVIEW_CHARS] + ("…" if len(joined) > PREVIEW_CHARS else "")
    if not quote:
        return first, "quote is empty: first 800 characters of the posting"
    start = joined.find(quote)
    if start < 0:
        return first, "QUOTE NOT FOUND in the posting text: first 800 characters of the posting"
    end, pos, shown = start + len(quote), 0, []
    for b in blocks:
        b_start, b_end = pos, pos + len(b)
        if b_start < end and start < b_end:
            shown.append(b)
        pos = b_end + 1
    return "\n\n".join(shown), "the paragraph(s) that hold the quote"


# ---------------------------------------------------------------- writes

def write_label(sheet: Path, row_no: str, label: str, note: str, labeled_at: str) -> None:
    if label not in LABEL_KEYS.values():
        raise LabelError(f"invalid label {label!r}")
    header, rows = read_sheet(sheet)
    target = _find(rows, row_no)
    if target["my_label"].strip():
        raise LabelError(f"row {row_no} already labeled {target['my_label']!r}; "
                         f"labels are written once (use --correct {row_no})")
    header = _with_labeled_at(header, rows)
    target.update(my_label=label, note=note, labeled_at=labeled_at)
    write_sheet_atomic(sheet, header, rows)


def correct_label(sheet: Path, row_no: str, label: str, note: str, labeled_at: str) -> str:
    if label not in LABEL_KEYS.values():
        raise LabelError(f"invalid label {label!r}")
    header, rows = read_sheet(sheet)
    target = _find(rows, row_no)
    old = target["my_label"].strip()
    if not old:
        raise LabelError(f"row {row_no} has no label yet; label it in the normal mode")
    if old == label:
        raise LabelError(f"row {row_no} is already {old!r}; nothing to correct")
    header = _with_labeled_at(header, rows)
    history = f"was {old}"
    if target.get("labeled_at"):
        history += f" (labeled {target['labeled_at']})"
    if target["note"]:
        history += f", old note: {target['note']}"
    new_note = f"[corrected {labeled_at[:10]}: {history}]" + (f" {note}" if note else "")
    target.update(my_label=label, note=new_note, labeled_at=labeled_at)
    write_sheet_atomic(sheet, header, rows)
    return new_note


# ---------------------------------------------------------------- display and sessions

def show_claim(row: dict, position: int, total: int, blocks: list[str], say) -> None:
    shown, why = context_for(blocks, row["quote"])
    say("")
    say("=" * 72)
    say(f"row {row['row']}   ({position}/{total})   posting {row['posting_id']}")
    say(f"title: {row.get('title', '')}")
    say(f"kind:  {row.get('kind', '')}")
    say(f"CLAIM: {row['claim']}")
    say(f"QUOTE: {row['quote']!r}" if row["quote"] else "QUOTE: (empty)")
    say(f"quote found in posting text: {row.get('quote_found', '')}")
    say("-" * 72)
    say(f"[{why}]")
    say(shown if blocks else "(text file missing)")
    say("-" * 72)
    for d in DEFINITIONS:
        say(f"  {d}")


def _ask(row, position, total, sheet, ask, say, extra_keys="k"):
    blocks = text_blocks(sheet, row["posting_id"])
    show_claim(row, position, total, blocks, say)
    prompt = "supported / contradicted / insufficient (s/c/i), f full text"
    prompt += ", k skip, q quit > " if "k" in extra_keys else ", q cancel > "
    while True:
        key = ask(prompt).strip().lower()
        if key in LABEL_KEYS or key == "q" or (key and key in extra_keys):
            return key
        if key == "f":
            page_text("\n\n".join(blocks) or "(text file missing)", ask, say)
            show_claim(row, position, total, blocks, say)
        else:
            say("please type s, c, i, f" + (", k" if "k" in extra_keys else "") + " or q")


def label_session(sheet: Path, ask=input, say=print, now=_now) -> dict:
    _, rows = read_sheet(sheet)
    total, skipped, labeled_now = len(rows), 0, 0
    try:
        for position, row in enumerate(rows, start=1):
            if row["my_label"].strip():
                continue
            key = _ask(row, position, total, sheet, ask, say)
            if key == "q":
                break
            if key == "k":
                skipped += 1
                continue
            note = ask("note (Enter for none) > ").strip()
            write_label(sheet, row["row"], LABEL_KEYS[key], note, now())
            labeled_now += 1
            say(f"saved row {row['row']}: {LABEL_KEYS[key]}")
    except (EOFError, KeyboardInterrupt):
        say("\nstopped; the row on screen was not saved")
    _, rows = read_sheet(sheet)
    labeled = sum(1 for r in rows if r["my_label"].strip())
    say(f"\n{sheet}: labeled {labeled}/{total} ({labeled_now} this session), skipped {skipped}, "
        f"left {total - labeled - skipped}")
    return {"labeled": labeled, "labeled_now": labeled_now, "skipped": skipped, "total": total}


def correct_session(sheet: Path, row_no: str, ask=input, say=print, now=_now) -> bool:
    _, rows = read_sheet(sheet)
    row = _find(rows, row_no)
    if not row["my_label"].strip():
        raise LabelError(f"row {row_no} has no label yet; label it in the normal mode")
    try:
        say(f"correcting row {row_no}: your current label is {row['my_label']!r}"
            + (f" with note {row['note']!r}" if row["note"] else ""))
        key = _ask(row, rows.index(row) + 1, len(rows), sheet, ask, say, extra_keys="")
        if key == "q":
            say("correction cancelled; sheet unchanged")
            return False
        note = ask("note (Enter for none) > ").strip()
    except (EOFError, KeyboardInterrupt):
        say("\ncorrection cancelled; sheet unchanged")
        return False
    new_note = correct_label(sheet, row_no, LABEL_KEYS[key], note, now())
    say(f"corrected row {row_no}: {LABEL_KEYS[key]}; note: {new_note}")
    return True


def main(argv=None, ask=input, say=print, now=_now) -> int:
    parser = argparse.ArgumentParser(prog="tools/label_claims.py", description="Blind claim labeler.")
    parser.add_argument("sheet", type=Path)
    parser.add_argument("--correct", metavar="ROW", help="change an existing label (keeps the old one in the note)")
    args = parser.parse_args(argv)
    try:
        if args.correct is not None:
            correct_session(args.sheet, args.correct, ask, say, now)
        else:
            label_session(args.sheet, ask, say, now)
    except (LabelError, OSError) as err:
        say(f"error: {err}")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
