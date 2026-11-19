"""JS3 filter batch run over the frozen corpus (FILTER.md v1 and v2 §1, §3; SEAL.md v1.5).

A tool outside the agent and its permission layer (CONTRACT v0.9 item 5). Run
from the JS3 folder:

    python3.13 tools/filter_run.py [--filter v1|v2]

--filter v1, the default, is the committed v1 run, unchanged. --filter v2
judges with agent/filter.py's V2_OPTIONS (FILTER.md v2: F6, F9, F10), writes
output/filter_v2_<UTC>/ with C4 and C4_reason columns added, skips the rule.py
cross-check (rule.py is v1's rule), and also writes justifications.tsv: for
each shortlisted posting, in F8 order, one row per claim the agent makes about
it (FILTER.md §2), unlabeled.

It reads the corpus where it lives (tools/seal_draw.py's CORPUS list), checks
every file's SHA-256 against vault/corpus_manifest.tsv before judging
anything, turns each body into postings with agent/adapters.py, keeps one copy
per (board key, id) from the latest file by UTC time, and judges every posting
with agent/filter.py against resume_persona.json.

Postings in the final's set or in JS3's held-out set (vault/final_heldout_ids.tsv,
vault/js3_heldout_ids_v2.tsv) are never judged and never written: only their
count appears. The exposed set and the seen postings are development data and
are judged like any other posting.

It writes one new folder, output/filter_<version>_<UTC>/, and refuses if it
exists: verdicts.tsv, shortlist.tsv, cannot_tell.tsv, closest_calls.tsv,
summary.txt, and for v2 justifications.tsv.
No file holds a posting's text. It prints summary.txt and nothing else. Any
error stops the run before anything is written; no error message names a
posting.

Standard library only.
"""

import argparse
import hashlib
import sys
from datetime import datetime, timezone
from pathlib import Path

_JS3 = Path(__file__).resolve().parent.parent
if str(_JS3) not in sys.path:
    sys.path.insert(0, str(_JS3))

from agent import adapters, rule  # noqa: E402
from agent import filter as filter_v1  # noqa: E402
from agent.errors import Refusal, RunError  # noqa: E402
from agent.persona import check_persona, load_persona  # noqa: E402
from tools import label_view, seal_draw  # noqa: E402  CORPUS, the vault file names, the sealed-set reader

PERSONA_FILE = "resume_persona.json"
MANIFEST_FILE = "corpus_manifest.tsv"
OUTPUT_DIR = "output"
RUN_PREFIX = "filter_v1_"
SEALED_FILES = (seal_draw.FINAL_FILE, seal_draw.JS3_V2_FILE)
FILTERS = {"v1": None, "v2": filter_v1.V2_OPTIONS}  # --filter: the options agent/filter.py judges with

COLUMNS = ("board_key", "id", "title", "location", "verdict", "C1", "C2", "C3", "score",
           "title_match", "location_match", "skills_found", "missing", "closest_call")
COLUMNS_V2 = COLUMNS[:8] + ("C4", "C4_reason") + COLUMNS[8:]  # C4 and its reason right after C3
JUSTIFICATION_COLUMNS = ("position", "board_key", "id", "claim_no", "claim", "field")
VERDICTS = (filter_v1.RELEVANT, filter_v1.NOT_RELEVANT, filter_v1.CANNOT_TELL)


class FilterRunError(Exception):
    """Stops the run before anything is written. Never names a posting."""


# ---------------------------------------------------------------- inputs

def load_checked_persona(root):
    try:
        persona = load_persona(Path(root) / PERSONA_FILE)
        check_persona(persona)
    except (RunError, Refusal) as exc:
        raise FilterRunError(str(exc)) from exc
    return persona


def read_manifest(root):
    """{path: sha256} from vault/corpus_manifest.tsv."""
    name = f"{seal_draw.VAULT}/{MANIFEST_FILE}"
    try:
        lines = (Path(root) / seal_draw.VAULT / MANIFEST_FILE).read_text(encoding="utf-8").splitlines()
    except OSError as exc:
        raise FilterRunError(f"cannot read {name} ({type(exc).__name__})") from exc
    header = lines[0].split("\t") if lines else []
    if "path" not in header or "sha256" not in header:
        raise FilterRunError(f"{name}: the header has no path and sha256 columns")
    path_at, sha_at = header.index("path"), header.index("sha256")
    listed = {}
    for number, line in enumerate(lines[1:], start=2):
        if not line:
            continue
        cells = line.split("\t")
        if len(cells) != len(header):
            raise FilterRunError(f"{name} line {number}: expected {len(header)} columns")
        if cells[path_at] in listed:
            raise FilterRunError(f"{name} line {number}: a file is listed twice")
        listed[cells[path_at]] = cells[sha_at].lower()
    return listed


def read_checked_corpus(root, corpus):
    """[(board, rel, utc, bytes)] once every file's SHA-256 matches the manifest. Any doubt stops the run."""
    listed = read_manifest(root)
    files, problems = [], []
    for board, rel, utc in corpus:
        try:
            raw = (Path(root) / rel).read_bytes()
        except OSError as exc:
            raise FilterRunError(f"corpus file missing or unreadable: {rel} ({type(exc).__name__})") from exc
        expected = listed.get(rel)
        if expected is None:
            problems.append(f"{rel}: not listed in {seal_draw.VAULT}/{MANIFEST_FILE}")
        elif hashlib.sha256(raw).hexdigest() != expected:
            problems.append(f"{rel}: SHA-256 does not match {seal_draw.VAULT}/{MANIFEST_FILE}")
        files.append((board, rel, utc, raw))
    extra = sorted(set(listed) - {rel for _, rel, _ in corpus})
    problems += [f"{rel}: listed in {seal_draw.VAULT}/{MANIFEST_FILE} but not in the corpus" for rel in extra]
    if problems:
        raise FilterRunError("corpus check failed, nothing judged: " + "; ".join(problems))
    return files


def latest_postings(files):
    """{(board, id): posting} through agent/adapters.py; the copy from the latest file wins (FILTER.md §3)."""
    latest = {}
    # Sorted by UTC time, stable on CORPUS order, so a later file overwrites (as in seal_draw.load_corpus).
    for board, rel, _utc, raw in sorted(files, key=lambda entry: entry[2]):
        ats = board.split(":", 1)[0]
        if ats not in adapters.ADAPTERS:
            raise FilterRunError(f"unknown ATS in a board key: {rel}")
        try:
            postings = adapters.ADAPTERS[ats](raw)
        except adapters.UnexpectedShape as exc:
            raise FilterRunError(f"corpus file is not the board's job list: {rel}") from exc
        for posting in postings:
            latest[(board, posting["posting_id"])] = posting
    return latest


def read_sealed(root):
    """{(board, id)} in the final's set and JS3's held-out set; every rank is recomputed (label_view)."""
    sealed = set()
    for file_name in SEALED_FILES:
        try:
            rows = label_view.read_seal_file(Path(root) / seal_draw.VAULT / file_name,
                                             f"{seal_draw.VAULT}/{file_name}")
        except label_view.ViewError as exc:
            raise FilterRunError(str(exc)) from exc
        sealed |= {(board, posting_id) for _, board, posting_id in rows}
    return sealed


# ---------------------------------------------------------------- judging

def judge_all(latest, sealed, persona, options=None):
    """(records, cross-check counts). Sealed postings are skipped before judge sees them.

    With options (v2), there is no rule.py cross-check and the counts are None.
    """
    records = []
    compared = disagree = 0
    for (board, posting_id), posting in sorted(latest.items()):
        if (board, posting_id) in sealed:
            continue
        if options is None:  # v1, called exactly as before
            record = {"board_key": board, **filter_v1.judge(posting, persona)}
            if not record["missing"]:
                compared += 1
                rule_verdict, _ = rule.judge(posting, persona)
                disagree += rule_verdict != record["verdict"]
        else:
            record = {"board_key": board, **filter_v1.judge(posting, persona, options)}
        records.append(record)
    return records, ({"compared": compared, "disagree": disagree} if options is None else None)


def _cell(value):
    """None is blank, a bool is yes/no, a list of résumé terms is joined with "; "."""
    if value is None:
        return ""
    if isinstance(value, bool):
        return "yes" if value else "no"
    if isinstance(value, list):
        return "; ".join(value)
    return str(value)


def _checked(cells):
    if any("\t" in cell or "\n" in cell or "\r" in cell for cell in cells):
        raise FilterRunError("a posting's cleaned field holds a tab or a line break; nothing written")
    return cells


def row(record):
    """One posting's cells under COLUMNS, or under COLUMNS_V2 when the record has C4."""
    cells = [_cell(record["board_key"]), _cell(record["posting_id"]), _cell(record["title"]),
             _cell(record["location"]), record["verdict"], record["C1"], record["C2"], record["C3"],
             _cell(record["score"]), _cell(record["title_match"]), _cell(record["location_match"]),
             _cell(record["skills_found"]), ", ".join(record["missing"]), _cell(record["closest_call"])]
    if "C4" in record:
        cells[8:8] = [record["C4"], record["C4_reason"]]
    return _checked(cells)


def claims(record, max_years):
    """The agent's reasons for keeping one posting, as plain sentences: [(claim, field)].

    One claim per matched term, so each is one checkable statement (FILTER.md §2;
    decision 2026-11-19). The years claim is made for every kept posting, as
    written (decision 2026-11-19): C4 also passes when the text states no years.
    """
    made = [(f"The title names a target role: {term}.", "title") for term in record["title_match"]]
    made += [(f"The location is workable: {term}.", "location") for term in record["location_match"]]
    made.append(("The title has no seniority word.", "title"))
    made.append((f"The posting asks for no more than {max_years} years of experience.", "text"))
    made += [(f"The role calls for {skill}.", "text") for skill in record["skills_found"]]
    return made


def tsv(header, rows):
    return "\n".join("\t".join(cells) for cells in [list(header)] + rows) + "\n"


def output_files(records, options=None):
    """{file name: text} for the TSV files: four for v1, and justifications.tsv as well for v2."""
    def f8_keys(record):  # F8's keys, applied to any record that has a score
        return (-(record["score"] or 0), record["board_key"], record["posting_id"])

    columns = COLUMNS if options is None else COLUMNS_V2
    shortlist = filter_v1.rank(records)
    texts = {
        "verdicts.tsv": tsv(columns, [row(r) for r in records]),
        "shortlist.tsv": tsv(("position",) + columns, [[str(p)] + row(r) for p, r in enumerate(shortlist, start=1)]),
        "cannot_tell.tsv": tsv(columns, [row(r) for r in records if r["verdict"] == filter_v1.CANNOT_TELL]),
        "closest_calls.tsv": tsv(columns, [row(r) for r in sorted((r for r in records if r["closest_call"]),
                                                                    key=f8_keys)]),
    }
    if options is not None:
        texts["justifications.tsv"] = tsv(JUSTIFICATION_COLUMNS, [
            _checked([str(p), r["board_key"], r["posting_id"], str(n), claim, field])
            for p, r in enumerate(shortlist, start=1)
            for n, (claim, field) in enumerate(claims(r, options["max_years"]), start=1)])
    return texts


def summary_text(files, latest, sealed, records, cross, boards, folder, version="v1"):
    counts = {board: {verdict: 0 for verdict in VERDICTS} for board in boards}
    closest = {board: 0 for board in boards}
    for record in records:
        counts[record["board_key"]][record["verdict"]] += 1
        closest[record["board_key"]] += record["closest_call"]

    def verdict_line(label, by_verdict):
        return (f"  {label}: " + ", ".join(f"{verdict} {by_verdict[verdict]}" for verdict in VERDICTS)
                + f"; total {sum(by_verdict.values())}")

    total = {verdict: sum(counts[board][verdict] for board in boards) for verdict in VERDICTS}
    missing = sum(1 for record in records if record["missing"])
    if version == "v1":
        title = "JS3 filter v1 run (FILTER.md v1; SEAL.md v1.5). Counts only: no ids, no titles."
        checks = [f"rule.py cross-check: {cross['compared']} postings with no missing field; "
                  f"disagreements: {cross['disagree']}",
                  f"postings with a missing field: {missing} (judged under F7; not compared with rule.py)"]
    else:
        title = "JS3 filter v2 run (FILTER.md v2; SEAL.md v1.5). Counts only: no ids, no titles."
        checks = ["rule.py cross-check: not run for v2, which is not compared with rule.py: rule.py is v1's "
                  "rule, and v2 changes F6 (a skills threshold of 0) and adds C4 (F9, F10), so v2's verdicts "
                  "are meant to differ from it (FILTER.md v2)",
                  f"postings with a missing field: {missing} (judged under F7)"]
    lines = [
        title,
        f"corpus: {len(files)} files, {len(latest)} postings (one copy per board key and id)",
        f"sealed postings withheld, not judged and not written: {len(sealed)}",
        f"judged: {len(records)}",
        "verdicts:",
        *[verdict_line(board, counts[board]) for board in boards],
        verdict_line("all boards", total),
        f"closest calls: {sum(closest.values())} ("
        + ", ".join(f"{board} {closest[board]}" for board in boards) + ")",
        *checks,
        f"written to: {OUTPUT_DIR}/{folder}/",
    ]
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- command line

def run(root, corpus, now, out, version="v1"):
    options = FILTERS[version]
    folder = f"filter_{version}_" + now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    target = Path(root) / OUTPUT_DIR / folder
    if target.exists():
        raise FilterRunError(f"refusing to overwrite: {OUTPUT_DIR}/{folder}/")
    persona = load_checked_persona(root)
    files = read_checked_corpus(root, corpus)
    latest = latest_postings(files)
    sealed = read_sealed(root)
    if not sealed <= set(latest):
        raise FilterRunError("a sealed posting is not in the corpus; nothing judged")
    records, cross = judge_all(latest, sealed, persona, options)
    if cross is not None and cross["disagree"]:  # v1 only
        raise FilterRunError(f"rule.py cross-check failed: {cross['disagree']} postings with no missing field "
                             f"disagree with rule.py; nothing written")
    boards = sorted({board for board, _, _ in corpus})
    texts = output_files(records, options)
    texts["summary.txt"] = summary_text(files, latest, sealed, records, cross, boards, folder, version)
    (Path(root) / OUTPUT_DIR).mkdir(exist_ok=True)
    try:
        target.mkdir()  # never exist_ok: a second run in the same second is refused, not merged
    except FileExistsError as exc:
        raise FilterRunError(f"refusing to overwrite: {OUTPUT_DIR}/{folder}/") from exc
    for name, text in texts.items():
        with open(target / name, "x", encoding="utf-8") as handle:
            handle.write(text)
    out.write(texts["summary.txt"])


def main(argv=None, root=_JS3, corpus=seal_draw.CORPUS, now=None, out=None, err=None):
    out = out or sys.stdout
    err = err or sys.stderr
    parser = argparse.ArgumentParser(prog="filter_run.py", description="FILTER.md over the frozen JS3 corpus.")
    parser.add_argument("--filter", choices=sorted(FILTERS), default="v1",
                        help="v1 (the default, the committed run) or v2 (FILTER.md v2)")
    args = parser.parse_args(argv)
    try:
        run(root, corpus, now or datetime.now(timezone.utc), out, args.filter)
    except FilterRunError as exc:
        err.write(f"error: {exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
