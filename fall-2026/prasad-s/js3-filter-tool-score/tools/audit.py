"""JS3 reject audit (AUDIT.md v1; FILTER.md v1.1 §2, §5; SEAL.md v1.5).

A tool outside the agent, run from the JS3 folder, on FILTER v1's first run:

    python3.13 tools/audit.py draw
    python3.13 tools/audit.py show N
    python3.13 tools/audit.py template > PATH
    python3.13 tools/audit.py check PATH
    python3.13 tools/audit.py compare PATH
    python3.13 tools/audit.py context N

draw builds audit/audit_list.tsv from the run's verdicts.tsv and
closest_calls.tsv: (A) the 30 not_relevant postings with the lowest
SHA-256 of "js3-audit-2026-11-18:<board key>:<id>" (AUDIT.md §3), (B) every
closest call, (C) every posting whose C1 and C2 both pass (AUDIT.md §2).
Each posting appears once; positions follow the SHA-256 of
"js3-audit-2026-11-18:order:<board key>:<id>" (AUDIT.md §4). Every later
command re-derives the list and refuses if audit/audit_list.tsv differs.

show, template and check are blind (AUDIT.md §4): show prints only the
posting's own text, cleaned as tools/label_view.py does; template and check
know positions, board keys and ids only. compare is the first command that
puts the rule's details next to the hand verdicts, and context runs only
after a compare.

Writes only audit/audit_list.tsv (draw) and audit/compare_<UTC>/ (compare),
and never overwrites. No error or check message names a posting; ids appear
only in show's and context's posting lines and in template's rows.

Standard library only.
"""

import argparse
import hashlib
import math
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

_JS3 = Path(__file__).resolve().parent.parent
if str(_JS3) not in sys.path:
    sys.path.insert(0, str(_JS3))

from tools import filter_run, label_view, seal_draw  # noqa: E402

SEED = "js3-audit-2026-11-18"  # AUDIT.md §3: fixed before the draw; deliberately no seed option
RUN = "output/filter_v1_2026-11-17T210612Z"  # AUDIT.md "Rests on"
AUDIT_DIR = "audit"
LIST_FILE = "audit_list.tsv"
COMPARE_PREFIX = "compare_"
A_SIZE = 30  # AUDIT.md §2
GROUPS = (("A", "random rejects"), ("B", "closest calls"), ("C", "both gates pass"))
LIST_HEADER = ("position", "board_key", "id", "in_A", "in_B", "in_C", "in_exposed")
LABEL_HEADER = label_view.LABEL_HEADER
VERDICTS = label_view.VERDICTS
PARTS = label_view.PARTS
# title and location are the run's cleaned values, copied from verdicts.tsv; no body text is ever written.
ROWS_HEADER = ("position", "board_key", "id", "title", "location", "in_A", "in_B", "in_C", "in_exposed",
               "rule_verdict", "C1", "C2", "C3", "score", "title_match", "location_match", "skills_found",
               "hand_verdict", "hand_parts", "hand_evidence", "wrong")
CONTEXT_EACH_SIDE = 40  # "about 80 characters" around each match: 40 before and 40 after
ALPHA = 0.05  # 95% interval (AUDIT.md §5)

_DIGITS = re.compile(r"[0-9]+")


class AuditError(Exception):
    """A refusal or an error. Never names a posting."""


# ---------------------------------------------------------------- hashes (AUDIT.md §3, §4)

def a_rank(board, posting_id):
    """Group (A)'s rank: SHA-256 of "<seed>:<board key>:<id>", lowercase hex."""
    return hashlib.sha256(f"{SEED}:{board}:{posting_id}".encode("utf-8")).hexdigest()


def order_rank(board, posting_id):
    """The labeling order: SHA-256 of "<seed>:order:<board key>:<id>", lowercase hex."""
    return hashlib.sha256(f"{SEED}:order:{board}:{posting_id}".encode("utf-8")).hexdigest()


# ---------------------------------------------------------------- reading the run and the vault

def _read_tsv(path, shown, header):
    try:
        lines = Path(path).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise AuditError(f"cannot read {shown} ({type(exc).__name__})") from exc
    if not lines or tuple(lines[0].split("\t")) != tuple(header):
        raise AuditError(f"{shown}: the header is not the one expected")
    rows = {}
    for number, line in enumerate(lines[1:], start=2):
        if not line:
            continue
        cells = line.split("\t")
        if len(cells) != len(header):
            raise AuditError(f"{shown} line {number}: expected {len(header)} columns")
        row = dict(zip(header, cells))
        key = (row["board_key"], row["id"])
        if key in rows:
            raise AuditError(f"{shown} line {number}: a posting is listed twice")
        rows[key] = row
    return rows


def _seal_keys(root, file_name):
    try:
        rows = label_view.read_seal_file(Path(root) / seal_draw.VAULT / file_name, f"{seal_draw.VAULT}/{file_name}")
    except label_view.ViewError as exc:
        raise AuditError(str(exc)) from exc
    return {(board, posting_id) for _, board, posting_id in rows}


def derive(root):
    """Everything the audit list follows from: the run, the vault, the seed. Refuses before anything is written."""
    run = Path(root) / RUN
    verdicts = _read_tsv(run / "verdicts.tsv", f"{RUN}/verdicts.tsv", filter_run.COLUMNS)
    closest_rows = _read_tsv(run / "closest_calls.tsv", f"{RUN}/closest_calls.tsv", filter_run.COLUMNS)
    final = _seal_keys(root, seal_draw.FINAL_FILE)
    v2 = _seal_keys(root, seal_draw.JS3_V2_FILE)
    exposed = _seal_keys(root, seal_draw.JS3_FILE)
    if set(verdicts) & (final | v2):
        raise AuditError(f"{RUN}/verdicts.tsv holds a posting in the final's set or JS3's held-out set; "
                         f"refusing (SEAL.md)")
    flagged = {key for key, row in verdicts.items() if row["closest_call"] == "yes"}
    if set(closest_rows) != flagged or any(closest_rows[key] != verdicts[key] for key in closest_rows):
        raise AuditError(f"{RUN}/closest_calls.tsv does not match the closest_call column of verdicts.tsv")
    rejects = [key for key, row in verdicts.items() if row["verdict"] == "not_relevant"]
    if len(rejects) < A_SIZE:
        raise AuditError(f"the run has {len(rejects)} not_relevant postings; group (A) needs {A_SIZE}")
    groups = {
        "A": set(sorted(rejects, key=lambda key: (a_rank(*key), key))[:A_SIZE]),
        "B": set(closest_rows),
        "C": {key for key, row in verdicts.items() if row["C1"] == "pass" and row["C2"] == "pass"},
    }
    keys = sorted(groups["A"] | groups["B"] | groups["C"], key=lambda key: (order_rank(*key), key))
    return {"verdicts": verdicts, "groups": groups, "exposed": exposed, "final": final, "v2": v2, "keys": keys,
            "rejects": len(rejects)}


def _yes(flag):
    return "yes" if flag else "no"


def _flags(state, key):
    """in_A, in_B, in_C, in_exposed for one posting."""
    return [_yes(key in state["groups"][g]) for g, _ in GROUPS] + [_yes(key in state["exposed"])]


def list_text(state):
    rows = [[str(p), key[0], key[1]] + _flags(state, key) for p, key in enumerate(state["keys"], start=1)]
    return "\n".join("\t".join(cells) for cells in [list(LIST_HEADER)] + rows) + "\n"


def load_list(root):
    """The derived state, once audit/audit_list.tsv is checked to be exactly what draw wrote."""
    state = derive(root)
    path = Path(root) / AUDIT_DIR / LIST_FILE
    try:
        actual = path.read_bytes()
    except OSError as exc:
        raise AuditError(f"cannot read {AUDIT_DIR}/{LIST_FILE} ({type(exc).__name__}); run draw first") from exc
    if actual != list_text(state).encode("utf-8"):
        raise AuditError(f"{AUDIT_DIR}/{LIST_FILE} does not match the list re-derived from the run, the vault and "
                         f"the seed; refusing")
    return state


# ---------------------------------------------------------------- positions and postings

def position_of(arg, state):
    """show and context take a position 1-N and nothing else. A refusal never repeats the argument."""
    n = len(state["keys"])
    if _DIGITS.fullmatch(arg) and 1 <= int(arg) <= n:
        return int(arg)
    if any(arg == posting_id for _, posting_id in state["final"]):
        raise AuditError(f"refused: the argument is an id in the final's set, which is never shown in JS3 "
                         f"(SEAL.md §1, §7); this command takes a position 1-{n}")
    if any(arg == posting_id for _, posting_id in state["v2"]):
        raise AuditError(f"refused: the argument is an id in JS3's held-out set (SEAL.md §8); "
                         f"this command takes a position 1-{n}")
    if any(arg == posting_id for _, posting_id in state["keys"]):
        raise AuditError(f"refused: the argument is an id on the audit list; this command takes a position 1-{n}, "
                         f"not an id")
    raise AuditError(f"refused: the argument is not a position 1-{n}")


_NOT_IN_CORPUS = "a posting in JS3's set is not in the corpus"  # label_view.find_job's wording


def find_job(root, corpus, board, posting_id):
    """label_view's corpus reading: the latest copy, every file checked."""
    try:
        return label_view.find_job(root, corpus, board, posting_id)
    except label_view.ViewError as exc:
        message = "an audited posting is not in the corpus" if str(exc) == _NOT_IN_CORPUS else str(exc)
        raise AuditError(message) from exc


# ---------------------------------------------------------------- hand verdicts (FILTER.md §5)

def check_hand(text, state):
    """Every problem in a filled hand-verdict file: label_view's check, for the N audit rows. Never quotes a cell."""
    keys, n = state["keys"], len(state["keys"])
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
        if not (_DIGITS.fullmatch(position) and 1 <= int(position) <= n):
            problems.append(f"{where}: position is not a whole number 1-{n}")
        else:
            p = int(position)
            where = f"line {number} (position {p})"
            if p in first_line:
                problems.append(f"{where}: position {p} is already on line {first_line[p]}")
            else:
                first_line[p] = number
            if (board, posting_id) != keys[p - 1]:
                if (board, posting_id) in state["final"]:
                    problems.append(f"{where}: names an id in the final's set")
                elif (board, posting_id) in state["v2"]:
                    problems.append(f"{where}: names an id in JS3's held-out set (SEAL.md §8)")
                else:
                    problems.append(f"{where}: board_key and id do not match the audit list at this position")
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
    for p in range(1, n + 1):
        if p not in first_line:
            problems.append(f"position {p}: no row")
    return problems


def read_hand(path):
    try:
        return Path(path).read_text(encoding="utf-8-sig")  # read only; a spreadsheet's BOM is allowed
    except (OSError, UnicodeDecodeError) as exc:
        raise AuditError(f"cannot read the hand-verdict file ({type(exc).__name__})") from exc  # PATH not repeated


def parse_hand(text):
    """{position: (verdict, parts, evidence)} from a file that passed check_hand."""
    hand = {}
    for line in text.split("\n")[1:]:
        line = line.rstrip("\r")
        if line:
            position, _, _, verdict, parts, evidence = line.split("\t")
            hand[int(position)] = (verdict, parts, evidence)
    return hand


# ---------------------------------------------------------------- Clopper-Pearson (AUDIT.md §5)

def binomial_cdf(k, n, p):
    """P(X <= k) for X ~ Binomial(n, p), summed exactly term by term."""
    if k < 0:
        return 0.0
    if k >= n:
        return 1.0
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def _bisect(f, increasing):
    """The root of a monotone f on [0, 1]."""
    lo, hi = 0.0, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if (f(mid) < 0) == increasing:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-15:
            break
    return (lo + hi) / 2


def clopper_pearson(k, n, alpha=ALPHA):
    """Exact two-sided interval for k successes in n: each tail holds alpha/2."""
    if not 0 <= k <= n or n < 1:
        raise ValueError("need 0 <= k <= n and n >= 1")
    lower = 0.0 if k == 0 else _bisect(lambda p: (1 - binomial_cdf(k - 1, n, p)) - alpha / 2, increasing=True)
    upper = 1.0 if k == n else _bisect(lambda p: binomial_cdf(k, n, p) - alpha / 2, increasing=False)
    return lower, upper


# ---------------------------------------------------------------- commands

def cmd_draw(root, out):
    path = Path(root) / AUDIT_DIR / LIST_FILE
    if path.exists():
        raise AuditError(f"refusing to overwrite: {AUDIT_DIR}/{LIST_FILE}")
    state = derive(root)
    groups = state["groups"]
    a, b, c = groups["A"], groups["B"], groups["C"]
    (Path(root) / AUDIT_DIR).mkdir(exist_ok=True)
    with open(path, "x", encoding="utf-8") as handle:  # "x": never overwrite
        handle.write(list_text(state))
    exposed = sum(1 for key in state["keys"] if key in state["exposed"])
    out.write(f"JS3 reject audit list (AUDIT.md v1), from {RUN}/. Counts only: no ids.\n"
              f"group A (random rejects): {len(a)} of {state['rejects']} not_relevant postings\n"
              f"group B (closest calls): {len(b)}\n"
              f"group C (both gates pass): {len(c)}\n"
              f"overlaps: A and B {len(a & b)}, A and C {len(a & c)}, B and C {len(b & c)}, "
              f"all three {len(a & b & c)}\n"
              f"audit list: {len(state['keys'])} postings, each once\n"
              f"exposed postings on the list (SEAL.md §8): {exposed}\n"
              f"written to: {AUDIT_DIR}/{LIST_FILE}\n")


def cmd_show(root, corpus, arg, out):
    state = load_list(root)
    board, posting_id = state["keys"][position_of(arg, state) - 1]
    job = find_job(root, corpus, board, posting_id)
    out.write("\n".join(label_view.show_lines(board, posting_id, job)) + "\n")


def cmd_template(root, out):
    state = load_list(root)
    rows = [f"{p}\t{board}\t{posting_id}\t\t\t" for p, (board, posting_id) in enumerate(state["keys"], start=1)]
    out.write("\n".join(["\t".join(LABEL_HEADER)] + rows) + "\n")


def cmd_check(root, path, out):
    state = load_list(root)
    problems = check_hand(read_hand(path), state)
    out.write("ok\n" if not problems else "\n".join(problems) + "\n")
    return 1 if problems else 0


def _parts(parts):
    return set() if parts == "-" else {name.strip() for name in parts.split(",")}


def _tsv(header, rows):
    return "\n".join("\t".join(cells) for cells in [list(header)] + rows) + "\n"


def _pct(p):
    return f"{100 * p:.1f}%"


def compare_texts(state, hand, folder):
    rows, candidates = [], []
    groups = state["groups"]
    position = {key: p for p, key in enumerate(state["keys"], start=1)}
    for key, p in position.items():
        rule = state["verdicts"][key]
        verdict, parts, evidence = hand[p]
        cells = [str(p), key[0], key[1], rule["title"], rule["location"]] + _flags(state, key)
        cells += [rule["verdict"], rule["C1"], rule["C2"], rule["C3"], rule["score"], rule["title_match"],
                  rule["location_match"], rule["skills_found"], verdict, parts, evidence, _yes(verdict == "worth")]
        rows.append(cells)
        # AUDIT.md §6: a condition passed but the hand verdict failed that part; only not_worth fails a part.
        failed = _parts(parts) if verdict == "not_worth" else set()
        reasons = []
        if rule["C1"] == "pass" and failed & {"role", "level"}:
            reasons.append("C1 passed; hand failed " + ", ".join(sorted(failed & {"role", "level"})))
        if rule["C2"] == "pass" and "location" in failed:
            reasons.append("C2 passed; hand failed location")
        if reasons:
            candidates.append(cells + ["; ".join(reasons)])

    def counts(keys):
        verdicts = [hand[position[key]][0] for key in keys]
        return len(verdicts), verdicts.count("worth"), verdicts.count("unclear"), verdicts.count("not_worth")

    lines = [f"JS3 reject audit (AUDIT.md v1) of {RUN}/. Counts only: no ids.",
             f"audited postings: {len(state['keys'])}, each labeled once and counted in every group it is in"]
    for g, name in GROUPS:
        n, wrong, unclear, confirmed = counts(groups[g])
        lines.append(f"group {g} ({name}): n {n}, wrong (worth) {wrong}, unclear {unclear}, "
                     f"confirmed (not_worth) {confirmed}")
        if g == "A":
            lower, upper = clopper_pearson(wrong, n)
            lines.append(f"  rate of wrong rejects: {wrong}/{n} = {_pct(wrong / n)}; exact Clopper-Pearson 95% "
                         f"interval {_pct(lower)} to {_pct(upper)}")
        else:
            lines.append("  chosen, not random: counts only, no rate (AUDIT.md §5)")
    n, wrong, unclear, confirmed = counts(state["keys"])
    lines += [f"all audited: n {n}, wrong (worth) {wrong}, unclear {unclear}, confirmed (not_worth) {confirmed}",
              f"exposed postings audited (SEAL.md §8): {sum(1 for key in state['keys'] if key in state['exposed'])}",
              f"false-friend candidates: {len(candidates)}",
              f"written to: {AUDIT_DIR}/{folder}/"]
    return {
        "rows.tsv": _tsv(ROWS_HEADER, rows),
        "false_friend_candidates.tsv": _tsv(ROWS_HEADER + ("candidate_because",), candidates),
        "summary.txt": "\n".join(lines) + "\n",
    }


def cmd_compare(root, path, now, out):
    folder = COMPARE_PREFIX + now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    target = Path(root) / AUDIT_DIR / folder
    if target.exists():
        raise AuditError(f"refusing to overwrite: {AUDIT_DIR}/{folder}/")
    state = load_list(root)
    text = read_hand(path)
    problems = check_hand(text, state)
    if problems:
        raise AuditError(f"compare refused: the hand-verdict file does not pass check ({len(problems)} problems; "
                         f"run check on it)")
    texts = compare_texts(state, parse_hand(text), folder)
    try:
        target.mkdir()
    except FileExistsError as exc:
        raise AuditError(f"refusing to overwrite: {AUDIT_DIR}/{folder}/") from exc
    for name, content in texts.items():
        with open(target / name, "x", encoding="utf-8") as handle:
            handle.write(content)
    out.write(texts["summary.txt"])


def compare_done(root):
    audit = Path(root) / AUDIT_DIR
    return audit.is_dir() and any(p.is_dir() and (p / "summary.txt").is_file()
                                  for p in audit.glob(COMPARE_PREFIX + "*"))


def snippets(term, text):
    """Every place term matches in text (F2: case-insensitive substring), about 80 characters around each."""
    found = []
    for match in re.finditer(re.escape(term), text or "", re.IGNORECASE):
        start, end = max(0, match.start() - CONTEXT_EACH_SIDE), min(len(text), match.end() + CONTEXT_EACH_SIDE)
        found.append(("…" if start > 0 else "") + text[start:match.start()] + "[" + match.group(0) + "]"
                     + text[match.end():end] + ("…" if end < len(text) else ""))
    return found


def cmd_context(root, corpus, arg, out):
    if not compare_done(root):
        raise AuditError(f"refused: context runs only after compare; there is no {AUDIT_DIR}/{COMPARE_PREFIX}<UTC>/ "
                         f"with a summary.txt yet (AUDIT.md §4)")
    state = load_list(root)
    board, posting_id = state["keys"][position_of(arg, state) - 1]
    rule = state["verdicts"][(board, posting_id)]
    job = find_job(root, corpus, board, posting_id)
    fields = {"title": label_view.clean_title(board, job), "location": label_view.clean_location(board, job),
              "text": label_view.clean_text(board, job)}
    lines = [f"board_key: {board}", f"id: {posting_id}"]
    for column, kind, field in (("title_match", "title term (C1)", "title"),
                                ("location_match", "location term (C2)", "location"),
                                ("skills_found", "skill (C3)", "text")):
        terms = [term for term in rule[column].split("; ") if term]
        if not terms:
            lines.append(f"{kind}: none matched")
        for term in terms:
            places = snippets(term, fields[field])
            lines.append(f'{kind} "{term}", in the {field}: {len(places)} place{"s" if len(places) != 1 else ""}')
            lines += [f"  {snippet}" for snippet in places]
    out.write("\n".join(lines) + "\n")


class _UsageError(Exception):
    pass


class _Parser(argparse.ArgumentParser):
    """argparse's own errors repeat the argument they reject; this parser's errors repeat nothing."""

    def error(self, message):
        raise _UsageError()


USAGE = "audit.py draw | show N | template | check PATH | compare PATH | context N"


def main(argv=None, root=_JS3, corpus=seal_draw.CORPUS, now=None, out=None, err=None):
    out = out or sys.stdout
    err = err or sys.stderr
    parser = _Parser(prog="audit.py", description="JS3 reject audit (AUDIT.md v1).")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("draw", help="write audit/audit_list.tsv; prints counts only")
    sub.add_parser("show", help="one audited posting's own text, blind").add_argument("position", metavar="N")
    sub.add_parser("template", help="print an empty hand-verdict TSV; never writes a file")
    sub.add_parser("check", help="validate a filled hand-verdict file").add_argument("path", metavar="PATH")
    sub.add_parser("compare", help="join hand verdicts with the run; write audit/compare_<UTC>/").add_argument(
        "path", metavar="PATH")
    sub.add_parser("context", help="matched terms in their place; only after compare").add_argument(
        "position", metavar="N")
    try:
        args = parser.parse_args(argv)
    except _UsageError:
        err.write(f"error: not a valid command line; usage: {USAGE}\n")
        return 2
    try:
        if args.command == "draw":
            cmd_draw(root, out)
        elif args.command == "show":
            cmd_show(root, corpus, args.position, out)
        elif args.command == "template":
            cmd_template(root, out)
        elif args.command == "check":
            return cmd_check(root, args.path, out)
        elif args.command == "compare":
            cmd_compare(root, args.path, now or datetime.now(timezone.utc), out)
        else:
            cmd_context(root, corpus, args.position, out)
    except AuditError as exc:
        err.write(f"error: {exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
