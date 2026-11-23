"""Interactive blind labeler for the hand-label sheets (stdlib only).

Usage:
    .venv/bin/python tools/label.py audit/audit-sheet.csv
    .venv/bin/python tools/label.py labels/heldout-sheet.csv
    .venv/bin/python tools/label.py labels/heldout-sheet.csv --correct 7

BLIND: this tool reads only the sheet and each row's text_file. It refuses to open anything
under out*/ (where the filter results and the stratum key live), refuses a text_file that
points outside the sheet's folder, and shows only board, title, locations, date and the
posting text. It never imports the filter code.

WRITE-ONCE: a non-blank my_verdict is never overwritten in the normal mode. --correct ROW is
the only way to change one, and it keeps the old verdict (and old note and time) in the note
with the correction date. Every write re-reads the sheet, checks the rule again, and replaces
the file atomically (temp file in the same folder + os.replace).
"""

import argparse
import csv
import os
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
VERDICT_KEYS = {"k": "keep", "r": "reject", "c": "cannot_tell"}
KEYWORDS = ("year", "sponsor", "visa", "authoriz", "remote", "located", "intern")
PREVIEW_CHARS = 800
PAGE_LINES = 40
SENTENCE_CAP = 400
TEXT_MARKER = "--- posting text ---"


class LabelError(Exception):
    """A refused or impossible labeling action. The sheet is left unchanged."""


# ---------------------------------------------------------------- path guard

def _is_out_dir(name: str) -> bool:
    return name == "out" or name.startswith("out-") or name.startswith("out_") or name.startswith("out.")


def guard_path(path: Path, sheet: Path) -> Path:
    """Resolve path and refuse it if it lies under an out*/ folder of the project (or of the
    folder that holds the sheet's folder, as in tests)."""
    resolved = Path(path).resolve()
    roots = {PROJECT_DIR, Path(sheet).resolve().parent.parent}
    for root in roots:
        try:
            rel = resolved.relative_to(root)
        except ValueError:
            continue
        if rel.parts and _is_out_dir(rel.parts[0]):
            raise LabelError(f"refusing to open {path}: it is under {root / rel.parts[0]} (blind labeling)")
    return resolved


def text_path(sheet: Path, text_file: str) -> Path:
    """The row's text file, which must lie inside the sheet's own folder."""
    if not text_file:
        raise LabelError("row has no text_file")
    sheet_dir = Path(sheet).resolve().parent
    candidate = guard_path(sheet_dir / text_file, sheet)
    try:
        candidate.relative_to(sheet_dir)
    except ValueError:
        raise LabelError(f"refusing text_file {text_file!r}: it points outside {sheet_dir}") from None
    return candidate


# ---------------------------------------------------------------- sheet I/O

def read_sheet(sheet: Path) -> tuple[list[str], list[dict]]:
    guard_path(sheet, sheet)
    with open(sheet, newline="", encoding="utf-8") as fh:
        reader = csv.reader(fh)
        try:
            header = next(reader)
        except StopIteration:
            raise LabelError(f"{sheet} is empty") from None
        rows = [dict(zip(header, values)) for values in reader if values]
    for needed in ("row", "my_verdict", "note", "text_file"):
        if needed not in header:
            raise LabelError(f"{sheet} has no {needed!r} column")
    return header, rows


def write_sheet_atomic(sheet: Path, header: list[str], rows: list[dict]) -> None:
    sheet = Path(sheet)
    guard_path(sheet, sheet)
    tmp = sheet.with_name(f".{sheet.name}.tmp-{os.getpid()}")
    try:
        with open(tmp, "w", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            writer.writerow(header)
            for r in rows:
                writer.writerow([r.get(col, "") for col in header])
            fh.flush()
            os.fsync(fh.fileno())
        os.replace(tmp, sheet)
    finally:
        if tmp.exists():
            tmp.unlink()


def _find(rows: list[dict], row_no: str) -> dict:
    matches = [r for r in rows if r["row"] == str(row_no)]
    if len(matches) != 1:
        raise LabelError(f"row {row_no} not found exactly once in the sheet")
    return matches[0]


def _with_labeled_at(header: list[str], rows: list[dict]) -> list[str]:
    if "labeled_at" in header:
        return header
    for r in rows:
        r["labeled_at"] = ""
    return header + ["labeled_at"]


def write_label(sheet: Path, row_no: str, verdict: str, note: str, labeled_at: str) -> None:
    """Write one first-time label. Refuses if the row already has a verdict on disk."""
    if verdict not in VERDICT_KEYS.values():
        raise LabelError(f"invalid verdict {verdict!r}")
    header, rows = read_sheet(sheet)
    target = _find(rows, row_no)
    if target["my_verdict"].strip():
        raise LabelError(f"row {row_no} already labeled {target['my_verdict']!r}; "
                         f"labels are written once (use --correct {row_no})")
    header = _with_labeled_at(header, rows)
    target.update(my_verdict=verdict, note=note, labeled_at=labeled_at)
    write_sheet_atomic(sheet, header, rows)


def correct_label(sheet: Path, row_no: str, verdict: str, note: str, labeled_at: str) -> str:
    """Replace an existing verdict, keeping the old one in the note. Returns the new note."""
    if verdict not in VERDICT_KEYS.values():
        raise LabelError(f"invalid verdict {verdict!r}")
    header, rows = read_sheet(sheet)
    target = _find(rows, row_no)
    old = target["my_verdict"].strip()
    if not old:
        raise LabelError(f"row {row_no} has no verdict yet; label it in the normal mode")
    if old == verdict:
        raise LabelError(f"row {row_no} is already {old!r}; nothing to correct")
    header = _with_labeled_at(header, rows)
    history = f"was {old}"
    if target.get("labeled_at"):
        history += f" (labeled {target['labeled_at']})"
    if target["note"]:
        history += f", old note: {target['note']}"
    new_note = f"[corrected {labeled_at[:10]}: {history}]"
    if note:
        new_note += f" {note}"
    target.update(my_verdict=verdict, note=new_note, labeled_at=labeled_at)
    write_sheet_atomic(sheet, header, rows)
    return new_note


# ---------------------------------------------------------------- display

def read_text(sheet: Path, row: dict) -> tuple[str, str]:
    """(full file text, posting body). Body is the part after the posting-text marker."""
    path = text_path(sheet, row.get("text_file", ""))
    try:
        with open(path, encoding="utf-8") as fh:
            full = fh.read()
    except FileNotFoundError:
        return "", ""
    body = full.split(TEXT_MARKER, 1)[1].strip() if TEXT_MARKER in full else full.strip()
    return full, body


def keyword_sentences(body: str) -> list[str]:
    seen, out = set(), []
    for piece in re.split(r"(?<=[.!?])\s+|\n+", body):
        sentence = " ".join(piece.split())
        if not sentence or sentence in seen:
            continue
        if any(k in sentence.lower() for k in KEYWORDS):
            seen.add(sentence)
            out.append(sentence if len(sentence) <= SENTENCE_CAP else sentence[:SENTENCE_CAP] + "…")
    return out


def show_row(row: dict, position: int, total: int, body: str, missing: bool, say) -> None:
    say("")
    say("=" * 72)
    say(f"row {row['row']}   ({position}/{total})")
    say(f"board:     {row.get('board', '')}")
    say(f"title:     {row.get('title', '')}")
    say(f"locations: {row.get('locations', '')}")
    say(f"date:      {row.get('date', '')}")
    say("-" * 72)
    if missing:
        say("(text file missing)")
    else:
        preview = body[:PREVIEW_CHARS]
        say(preview + ("…" if len(body) > PREVIEW_CHARS else ""))
    say("-" * 72)
    hits = keyword_sentences(body)
    say(f"sentences with {', '.join(KEYWORDS)}: {len(hits)}")
    for s in hits:
        say(f"  • {s}")
    say("-" * 72)


def page_text(full: str, ask, say) -> None:
    lines = full.splitlines() or ["(empty)"]
    for start in range(0, len(lines), PAGE_LINES):
        for line in lines[start:start + PAGE_LINES]:
            say(line)
        end = min(start + PAGE_LINES, len(lines))
        if end < len(lines):
            reply = ask(f"-- lines {start + 1}-{end} of {len(lines)}: Enter for more, q to stop -- ")
            if reply.strip().lower() == "q":
                return
    say("-- end of text --")


# ---------------------------------------------------------------- sessions

def _now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def _ask_verdict(row, position, total, sheet, ask, say, extra_keys="s"):
    """Loop until k/r/c, or one of extra_keys / q. Returns the key."""
    full, body = read_text(sheet, row)
    show_row(row, position, total, body, missing=not full, say=say)
    prompt = "keep / reject / cannot_tell (k/r/c), f full text"
    prompt += ", s skip, q quit > " if "s" in extra_keys else ", q cancel > "
    while True:
        key = ask(prompt).strip().lower()
        if key in VERDICT_KEYS or key == "q" or (key and key in extra_keys):
            return key
        if key == "f":
            page_text(full, ask, say)
            show_row(row, position, total, body, missing=not full, say=say)
        else:
            say("please type k, r, c, f" + (", s" if "s" in extra_keys else "") + " or q")


def label_session(sheet: Path, ask=input, say=print, now=_now) -> dict:
    header, rows = read_sheet(sheet)
    total = len(rows)
    skipped, labeled_now = 0, 0
    try:
        for position, row in enumerate(rows, start=1):
            if row["my_verdict"].strip():
                continue
            key = _ask_verdict(row, position, total, sheet, ask, say)
            if key == "q":
                break
            if key == "s":
                skipped += 1
                continue
            note = ask("note (Enter for none) > ").strip()
            write_label(sheet, row["row"], VERDICT_KEYS[key], note, now())
            row["my_verdict"] = VERDICT_KEYS[key]
            labeled_now += 1
            say(f"saved row {row['row']}: {VERDICT_KEYS[key]}")
    except (EOFError, KeyboardInterrupt):
        say("\nstopped; the row on screen was not saved")
    _, rows = read_sheet(sheet)
    labeled = sum(1 for r in rows if r["my_verdict"].strip())
    summary = {"labeled": labeled, "labeled_now": labeled_now, "skipped": skipped,
               "left": len(rows) - labeled - skipped, "total": len(rows)}
    say(f"\n{sheet}: labeled {summary['labeled']}/{summary['total']} "
        f"({labeled_now} this session), skipped {skipped}, left {summary['left']}")
    return summary


def correct_session(sheet: Path, row_no: str, ask=input, say=print, now=_now) -> bool:
    _, rows = read_sheet(sheet)
    row = _find(rows, row_no)
    if not row["my_verdict"].strip():
        raise LabelError(f"row {row_no} has no verdict yet; label it in the normal mode")
    position = rows.index(row) + 1
    try:
        say(f"correcting row {row_no}: your current label is {row['my_verdict']!r}"
            + (f" with note {row['note']!r}" if row["note"] else ""))
        key = _ask_verdict(row, position, len(rows), sheet, ask, say, extra_keys="")
        if key == "q":
            say("correction cancelled; sheet unchanged")
            return False
        note = ask("note (Enter for none) > ").strip()
    except (EOFError, KeyboardInterrupt):
        say("\ncorrection cancelled; sheet unchanged")
        return False
    new_note = correct_label(sheet, row_no, VERDICT_KEYS[key], note, now())
    say(f"corrected row {row_no}: {VERDICT_KEYS[key]}; note: {new_note}")
    return True


def main(argv=None, ask=input, say=print, now=_now) -> int:
    parser = argparse.ArgumentParser(prog="tools/label.py", description="Blind hand labeler.")
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
