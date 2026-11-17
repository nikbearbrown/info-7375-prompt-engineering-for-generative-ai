"""JS3 labeling viewer: JS3's held-out postings, one at a time, for hand labels.

FILTER.md v1 §2 (the posting's own text) and §5 (hand verdicts); SEAL.md v1.3
§§1, 6, 7, 8. Run from the JS3 folder:

    python3.13 tools/label_view.py list
    python3.13 tools/label_view.py show N
    python3.13 tools/label_view.py template > PATH
    python3.13 tools/label_view.py check PATH

show prints a posting's board key and id, then its title, location and text,
cleaned as FILTER.md F1 says, and nothing else: no rule verdict, score,
condition, skill match, highlight, group, rank, URL, date, department or
compensation. Only JS3's held-out set can be shown: since SEAL.md §8 that is
vault/js3_heldout_ids_v2.tsv. The final's set never is (SEAL.md §1, §7), and
neither is the exposed set, vault/js3_heldout_ids.tsv (the first JS3 set,
retired by §8). Every command reads all three files and refuses if any two
share a posting. The tool never writes a file.

No message contains a posting id, a board key next to a position, or a
repeated argument: error and check messages get pasted into chats, and
SEAL.md v1.5 §8 keeps the v2 set out of them. Ids appear only in list's
output, in show's posting lines, and in template's rows (the labels file
itself, which stays in ~/js3-vault/).

Standard library only.
"""

import argparse
import html
import json
import re
import sys
import textwrap
from pathlib import Path

_JS3 = Path(__file__).resolve().parent.parent
if str(_JS3) not in sys.path:
    sys.path.insert(0, str(_JS3))

from tools import seal_draw  # noqa: E402  CORPUS, its file reader, the rank and F1's title cleanup

SET_SIZE = 30  # SEAL.md v1.3 §4, §8: JS3's held-out set (v2) is 22 product + 8 other
SEAL_HEADER = ("board_key", "id", "group", "rank")
LABEL_HEADER = ("position", "board_key", "id", "verdict", "parts", "evidence")
VERDICTS = ("worth", "not_worth", "unclear")  # FILTER.md §5
PARTS = ("role", "level", "location")  # FILTER.md §5, "How the three parts combine"
MISSING = "(missing)"
WRAP = 100

_TAG = re.compile(r"<[^>]*>")
_WHITESPACE = re.compile(r"\s+")
_DIGITS = re.compile(r"[0-9]+")


class ViewError(Exception):
    """A refusal or an error. Nothing from any posting is printed."""


# ---------------------------------------------------------------- the three sets

def read_seal_file(path, name):
    """[(rank, board, id)] from a draw output. Any doubt about the file refuses."""
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise ViewError(f"cannot read {name} ({type(exc).__name__})") from exc
    if not lines or tuple(lines[0].split("\t")) != SEAL_HEADER:
        raise ViewError(f"{name}: the header is not {', '.join(SEAL_HEADER)}")
    rows = []
    for number, line in enumerate(lines[1:], start=2):
        if not line:
            continue
        cells = line.split("\t")
        if len(cells) != len(SEAL_HEADER):
            raise ViewError(f"{name} line {number}: expected {len(SEAL_HEADER)} columns")
        board, posting_id, _group, rank = cells
        # SEAL.md §5: recomputed, so an edited rank (and so an edited order) is caught.
        if rank != seal_draw.rank(board, posting_id):
            raise ViewError(f"{name} line {number}: rank is not SEAL.md §5's hash of this posting")
        rows.append((rank, board, posting_id))
    if len({(b, i) for _, b, i in rows}) != len(rows):
        raise ViewError(f"{name}: a posting is listed twice")
    return rows


def load_sets(root):
    """(JS3's set as [(board, id)] in position order, the final's set, the exposed set), the last two as {(board, id)}.

    JS3's set is the v2 file (SEAL.md §8). Positions follow the rank column,
    lowest first, across both groups. A posting in any two of the three sets
    refuses every command (SEAL.md §1, §8).
    """
    vault = Path(root) / seal_draw.VAULT

    def read(file_name):
        return read_seal_file(vault / file_name, f"{seal_draw.VAULT}/{file_name}")

    js3_rows = read(seal_draw.JS3_V2_FILE)
    final_rows = read(seal_draw.FINAL_FILE)
    exposed_rows = read(seal_draw.JS3_FILE)
    if len(js3_rows) != SET_SIZE:
        raise ViewError(f"{seal_draw.VAULT}/{seal_draw.JS3_V2_FILE} holds {len(js3_rows)} postings; "
                        f"SEAL.md §4 says {SET_SIZE}")
    js3 = [(b, i) for _, b, i in sorted(js3_rows)]
    final = {(b, i) for _, b, i in final_rows}
    exposed = {(b, i) for _, b, i in exposed_rows}
    named = (("JS3's set", set(js3)), ("the final's set", final), ("the exposed set", exposed))
    for index, (a_name, a) in enumerate(named):
        for b_name, b in named[index + 1:]:
            if a & b:
                raise ViewError(f"a posting is in both {a_name} and {b_name}; refusing (SEAL.md §1, §8)")
    return js3, final, exposed


def position_of(arg, js3, final, exposed):
    """show takes a position 1-30 and nothing else.

    A refusal says which kind of argument it was and never repeats it: the
    argument may be a posting id, and refusals get pasted (SEAL.md §8).
    """
    if _DIGITS.fullmatch(arg) and 1 <= int(arg) <= SET_SIZE:
        return int(arg)
    if any(arg == posting_id for _, posting_id in final):
        raise ViewError(f"refused: the argument is an id in the final's set, which is never shown in JS3 "
                        f"(SEAL.md §1, §7); show takes a position 1-{SET_SIZE} (see list)")
    if any(arg == posting_id for _, posting_id in exposed):
        raise ViewError(f"refused: the argument is an id in the exposed set, the first JS3 set, retired by "
                        f"SEAL.md §8; show takes a position 1-{SET_SIZE} (see list)")
    if any(arg == posting_id for _, posting_id in js3):
        raise ViewError(f"refused: the argument is an id in JS3's set; show takes a position 1-{SET_SIZE} "
                        f"(see list), not an id")
    raise ViewError(f"refused: the argument is not a position 1-{SET_SIZE}, and not an id in JS3's set, "
                    f"the final's set or the exposed set")


# ---------------------------------------------------------------- the posting's own text (FILTER.md §2, F1)

def _ats(board):
    ats = board.split(":", 1)[0]
    if ats not in ("greenhouse", "ashby"):
        raise ViewError("unknown ATS in a posting's board key")
    return ats


def _collapse(value):
    """Collapse every whitespace run and trim. Not text, or empty after that, is missing (None)."""
    if not isinstance(value, str):
        return None
    return _WHITESPACE.sub(" ", value).strip() or None


def clean_title(board, job):
    _ats(board)
    return seal_draw.clean_title(job.get("title"))  # F1: the same cleanup the draw's groups used


def clean_location(board, job):
    if _ats(board) == "greenhouse":
        location = job.get("location")
        return _collapse(location.get("name")) if isinstance(location, dict) else None
    # CONTRACT v0.5 item 3, as JS2's adapters.ashby_location runs it: location, then each
    # secondaryLocations[].location, each trimmed, joined with "; ". A part that is not
    # text, or is empty after trimming, is left out (JS2 decision 2026-11-06).
    parts = [job.get("location")]
    secondaries = job.get("secondaryLocations")
    if isinstance(secondaries, list):
        parts += [entry.get("location") for entry in secondaries if isinstance(entry, dict)]
    parts = [part.strip() for part in parts if isinstance(part, str) and part.strip()]
    return _collapse("; ".join(parts)) if parts else None


def clean_text(board, job):
    if _ats(board) == "greenhouse":
        content = job.get("content")
        if not isinstance(content, str):
            return None
        # §4 steps 2-4, as JS2's rule.clean_content runs them: unescape once, every tag
        # becomes a space, whitespace collapsed.
        return _collapse(_TAG.sub(" ", html.unescape(content)))
    return _collapse(job.get("descriptionPlain"))  # §4 step 4 only


def find_job(root, corpus, board, posting_id):
    """The copy of (board, id) from the latest corpus file that has it (FILTER.md §3).

    Files are taken in UTC order, stable on CORPUS order, and a later copy
    replaces an earlier one, as in seal_draw.load_corpus. Every corpus file is
    read and checked with seal_draw.read_corpus_file, so a missing or
    unparseable file stops the run and is named (FILTER.md §3).
    """
    latest = None
    for entry_board, rel, _utc in sorted(corpus, key=lambda entry: entry[2]):
        try:
            raw, rows = seal_draw.read_corpus_file(root, entry_board, rel)
        except seal_draw.SealError as exc:
            raise ViewError(str(exc)) from exc
        if entry_board != board or posting_id not in {job_id for job_id, _ in rows}:
            continue
        for (job_id, _), job in zip(rows, json.loads(raw)["jobs"]):
            if job_id == posting_id:
                latest = job
    if latest is None:
        raise ViewError("a posting in JS3's set is not in the corpus")
    return latest


def show_lines(board, posting_id, job):
    """The board key, the id and the three fields. Wrapping changes no words."""
    title = clean_title(board, job)
    location = clean_location(board, job)
    text = clean_text(board, job)
    lines = [
        f"board_key: {board}",
        f"id: {posting_id}",
        f"title: {title or MISSING}",
        f"location: {location or MISSING}",
    ]
    if text is None:
        lines.append(f"text: {MISSING}")
    else:
        lines.append("text:")
        lines += textwrap.wrap(text, width=WRAP, break_long_words=False, break_on_hyphens=False)
    return lines


# ---------------------------------------------------------------- labels file (FILTER.md §5)

def check_labels(text, js3, final, exposed):
    """Every problem in a filled labels file. A problem never quotes a cell."""
    problems = []
    lines = [line.rstrip("\r") for line in text.split("\n")]
    if lines[0] != "\t".join(LABEL_HEADER):
        problems.append("line 1: the header is not " + ", ".join(LABEL_HEADER))
    first_line = {}
    for number, line in enumerate(lines[1:], start=2):
        if line == "":
            continue
        cells = line.split("\t")
        where = f"line {number}"
        if len(cells) != len(LABEL_HEADER):
            problems.append(f"{where}: {len(cells)} columns, expected {len(LABEL_HEADER)} "
                            f"(a tab inside evidence makes extra columns)")
            continue
        position, board, posting_id, verdict, parts, evidence = cells
        if not (_DIGITS.fullmatch(position) and 1 <= int(position) <= SET_SIZE):
            problems.append(f"{where}: position is not a whole number 1-{SET_SIZE}")
        else:
            p = int(position)
            where = f"line {number} (position {p})"
            if p in first_line:
                problems.append(f"{where}: position {p} is already on line {first_line[p]}")
            else:
                first_line[p] = number
            if (board, posting_id) != js3[p - 1]:
                if (board, posting_id) in final:
                    problems.append(f"{where}: names an id in the final's set")
                elif (board, posting_id) in exposed:
                    problems.append(f"{where}: names an id in the exposed set (the first JS3 set, SEAL.md §8)")
                else:
                    problems.append(f"{where}: board_key and id do not match JS3's set at this position")
        if verdict not in VERDICTS:
            problems.append(f"{where}: verdict is not one of {', '.join(VERDICTS)}")
        elif verdict == "worth":
            if parts != "-":
                problems.append(f"{where}: parts must be - for worth")
        else:
            names = [name.strip() for name in parts.split(",")]
            if any(name not in PARTS for name in names):
                problems.append(f"{where}: parts must list one or more of {', '.join(PARTS)}, "
                                f"comma-separated, for {verdict}")
            elif len(set(names)) != len(names):
                problems.append(f"{where}: parts lists a part twice")
        if not evidence.strip():
            problems.append(f"{where}: evidence is empty")
    for p in range(1, len(js3) + 1):
        if p not in first_line:
            problems.append(f"position {p}: no row")
    return problems


# ---------------------------------------------------------------- commands

def cmd_list(root, out):
    js3, _, _ = load_sets(root)
    out.write("".join(f"{p}\t{board}\t{posting_id}\n" for p, (board, posting_id) in enumerate(js3, start=1)))


def cmd_show(root, corpus, arg, out):
    js3, final, exposed = load_sets(root)
    board, posting_id = js3[position_of(arg, js3, final, exposed) - 1]
    job = find_job(root, corpus, board, posting_id)
    out.write("\n".join(show_lines(board, posting_id, job)) + "\n")


def cmd_template(root, out):
    js3, _, _ = load_sets(root)
    rows = [f"{p}\t{board}\t{posting_id}\t\t\t" for p, (board, posting_id) in enumerate(js3, start=1)]
    out.write("\n".join(["\t".join(LABEL_HEADER)] + rows) + "\n")


def cmd_check(root, path, out):
    js3, final, exposed = load_sets(root)
    try:
        text = Path(path).read_text(encoding="utf-8-sig")  # read only; a spreadsheet's BOM is allowed
    except (OSError, UnicodeDecodeError) as exc:
        raise ViewError(f"cannot read the labels file ({type(exc).__name__})") from exc  # PATH is not repeated
    problems = check_labels(text, js3, final, exposed)
    out.write("ok\n" if not problems else "\n".join(problems) + "\n")
    return 1 if problems else 0


class _UsageError(Exception):
    pass


class _Parser(argparse.ArgumentParser):
    """argparse's own errors repeat the argument they reject ("invalid choice: ...",
    "unrecognized arguments: ..."), and an argument may be a posting id. This
    parser's errors repeat nothing; main prints one fixed usage line instead.
    Subparsers are made from the same class."""

    def error(self, message):
        raise _UsageError()


USAGE = "label_view.py list | show N | template | check PATH"


def main(argv=None, root=seal_draw.JS3_ROOT, corpus=seal_draw.CORPUS, out=None, err=None):
    out = out or sys.stdout
    err = err or sys.stderr
    parser = _Parser(prog="label_view.py",
                     description="Show JS3's held-out postings for hand labels (FILTER.md §5).")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list", help="positions 1-30 with board key and id, in rank order")
    show = sub.add_parser("show", help="one posting's board key, id, title, location and text")
    show.add_argument("position", metavar="N", help="a position 1-30 from list")
    sub.add_parser("template", help="print an empty labels TSV to stdout; never writes a file")
    check = sub.add_parser("check", help="validate a filled labels file; never changes it")
    check.add_argument("path", metavar="PATH")
    try:
        args = parser.parse_args(argv)
    except _UsageError:
        err.write(f"error: not a valid command line; usage: {USAGE}\n")
        return 2
    try:
        if args.command == "list":
            cmd_list(root, out)
        elif args.command == "show":
            cmd_show(root, corpus, args.position, out)
        elif args.command == "template":
            cmd_template(root, out)
        else:
            return cmd_check(root, args.path, out)
    except ViewError as exc:
        err.write(f"error: {exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
