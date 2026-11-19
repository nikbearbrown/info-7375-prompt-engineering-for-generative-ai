"""JS3 measurement of candidate FILTER changes (FILTER.md v1.1; AUDIT.md v1.1 §7, §8; SEAL.md).

A tool outside the agent, run from the JS3 folder:

    python3.13 tools/measure.py [--hand PATH]

It loads the corpus, the persona and the sealed sets exactly as
tools/filter_run.py does (its own functions: the SHA-256 check against
vault/corpus_manifest.tsv, agent/adapters.py, the latest copy per posting),
and judges the development postings, the corpus minus the final's set and
JS3's held-out set, under each variant in VARIANTS. Sealed postings are
never judged and never written.

The hand labels are the file given with --hand, by default
audit/hand_verdicts_r3.tsv (pass 3, AUDIT.md §7), so the committed run can be
reproduced. A relative PATH is read from the JS3 folder. The file is matched
to postings through audit/audit_list.tsv and validated by tools/audit.py's
own checks, and table.tsv names it on its first line. For each variant, on
the audited postings, it counts kept (relevant), rejected (not_relevant) and
cannot_tell, each against worth, not_worth and unclear; F7 makes cannot_tell
neither kept nor rejected, so it has its own columns (decision 2026-11-19).
Over every judged development posting it counts how many the variant keeps.

Writes one new folder, output/measure_<UTC>/, and refuses if it exists:
table.tsv (one row per variant) and kept_<variant>.tsv for each variant
(board key, id, title, location, the reasons it was kept). Prints table.tsv
and nothing else. No file holds a posting's text, and no message names a
posting.

Standard library only.
"""

import argparse
import sys
from datetime import datetime, timezone
from pathlib import Path

_JS3 = Path(__file__).resolve().parent.parent
if str(_JS3) not in sys.path:
    sys.path.insert(0, str(_JS3))

from agent import filter as filter_v1  # noqa: E402
from tools import audit, filter_run, seal_draw  # noqa: E402

HAND_FILE = "audit/hand_verdicts_r3.tsv"  # the --hand default: pass 3 (AUDIT.md §7), the committed measurement's
MAX_YEARS = 3  # FILTER.md §5: level is read against a maximum of 3 years (resume_persona.json max_years_required)
SENIORITY = {"seniority_words": filter_v1.SENIORITY_WORDS}
VARIANTS = (
    ("v1", {}),
    ("T1", {"skills_needed": 1}),
    ("T0", {"skills_needed": 0}),
    ("S", dict(SENIORITY)),
    ("Y", {"max_years": MAX_YEARS}),
    ("T0+S", {"skills_needed": 0, **SENIORITY}),
    ("T0+Y", {"skills_needed": 0, "max_years": MAX_YEARS}),
    ("T0+S+Y", {"skills_needed": 0, **SENIORITY, "max_years": MAX_YEARS}),
    ("T1+S+Y", {"skills_needed": 1, **SENIORITY, "max_years": MAX_YEARS}),
)
OUTCOMES = (("kept", filter_v1.RELEVANT), ("rejected", filter_v1.NOT_RELEVANT),
            ("cannot_tell", filter_v1.CANNOT_TELL))
HAND = ("worth", "not_worth", "unclear")
TABLE_HEADER = (("variant", "options", "audited")
                + tuple(f"{outcome}_{hand}" for outcome, _ in OUTCOMES for hand in HAND)
                + ("judged", "kept", "cannot_tell"))
KEPT_HEADER = ("board_key", "id", "title", "location", "reasons")


class MeasureError(Exception):
    """Stops the run before anything is written. Never names a posting."""


def describe(options):
    settings = filter_v1.resolve_options(options)
    parts = [f"skills_needed={settings['skills_needed']}"]
    if settings["seniority_words"]:
        parts.append("seniority_words=FILTER.md §5 (" + ", ".join(settings["seniority_words"]) + ")")
    if settings["max_years"] is not None:
        parts.append(f"max_years={settings['max_years']}")
    return "; ".join(parts)


def development_postings(root, corpus):
    """(persona, {(board, id): posting}) for the corpus minus the sealed sets, through filter_run's own functions."""
    try:
        persona = filter_run.load_checked_persona(root)
        latest = filter_run.latest_postings(filter_run.read_checked_corpus(root, corpus))
        sealed = filter_run.read_sealed(root)
    except filter_run.FilterRunError as exc:
        raise MeasureError(str(exc)) from exc
    if not sealed <= set(latest):
        raise MeasureError("a sealed posting is not in the corpus; nothing judged")
    return persona, {key: posting for key, posting in latest.items() if key not in sealed}


def hand_verdicts(root, development, hand=HAND_FILE):
    """{(board, id): hand verdict} from the hand-verdict file, checked by tools/audit.py."""
    try:
        state = audit.load_list(root)  # audit_list.tsv, re-derived from the run and the seed, byte for byte
        text = audit.read_hand(Path(root) / hand)  # an absolute PATH stays absolute
    except audit.AuditError as exc:
        raise MeasureError(str(exc)) from exc
    problems = audit.check_hand(text, state)
    if problems:
        raise MeasureError(f"{hand} does not pass the audit check ({len(problems)} problems; "
                           f"run tools/audit.py check on it)")
    labels = {state["keys"][position - 1]: verdict for position, (verdict, _, _) in audit.parse_hand(text).items()}
    if not set(labels) <= set(development):
        raise MeasureError("an audited posting is not among the development postings")
    return labels


def reasons(record):
    """Why a posting was kept: the terms each condition matched."""
    parts = [f"C1: {', '.join(record['title_match'])}", f"C2: {', '.join(record['location_match'])}",
             f"C3: score {record['score']}" + (f" ({', '.join(record['skills_found'])})" if record["skills_found"] else "")]
    if "C4" in record:
        years = f" (years matched: {', '.join(record['years_matched'])})" if record["years_matched"] else ""
        parts.append(f"C4: {record['C4']}{years}")
    return "; ".join(parts)


def measure(development, persona, labels):
    """(table rows, {variant: kept records in F8 order})."""
    rows, kept = [], {}
    for name, options in VARIANTS:
        records = [{"board_key": key[0], **filter_v1.judge(posting, persona, options)}
                   for key, posting in sorted(development.items())]
        by_key = {(r["board_key"], r["posting_id"]): r for r in records}
        cells = {(outcome, hand): 0 for outcome, _ in OUTCOMES for hand in HAND}
        for key, hand in labels.items():
            outcome = next(o for o, verdict in OUTCOMES if verdict == by_key[key]["verdict"])
            cells[(outcome, hand)] += 1
        kept[name] = filter_v1.rank(records)
        rows.append([name, describe(options), str(len(labels))]
                    + [str(cells[(outcome, hand)]) for outcome, _ in OUTCOMES for hand in HAND]
                    + [str(len(records)), str(len(kept[name])),
                       str(sum(1 for r in records if r["verdict"] == filter_v1.CANNOT_TELL))])
    return rows, kept


def _cell(value):
    text = "" if value is None else str(value)
    if "\t" in text or "\n" in text or "\r" in text:
        raise MeasureError("a posting's cleaned field holds a tab or a line break; nothing written")
    return text


def _tsv(header, rows):
    return "\n".join("\t".join(cells) for cells in [list(header)] + rows) + "\n"


def run(root, corpus, now, out, hand=HAND_FILE):
    folder = "measure_" + now.astimezone(timezone.utc).strftime("%Y-%m-%dT%H%M%SZ")
    target = Path(root) / filter_run.OUTPUT_DIR / folder
    if target.exists():
        raise MeasureError(f"refusing to overwrite: {filter_run.OUTPUT_DIR}/{folder}/")
    persona, development = development_postings(root, corpus)
    labels = hand_verdicts(root, development, hand)
    rows, kept = measure(development, persona, labels)
    texts = {"table.tsv": f"hand labels: {hand}\n" + _tsv(TABLE_HEADER, rows)}
    for name, _ in VARIANTS:
        texts[f"kept_{name}.tsv"] = _tsv(KEPT_HEADER, [[_cell(r["board_key"]), _cell(r["posting_id"]), _cell(r["title"]),
                                                        _cell(r["location"]), _cell(reasons(r))] for r in kept[name]])
    (Path(root) / filter_run.OUTPUT_DIR).mkdir(exist_ok=True)
    try:
        target.mkdir()
    except FileExistsError as exc:
        raise MeasureError(f"refusing to overwrite: {filter_run.OUTPUT_DIR}/{folder}/") from exc
    for name, text in texts.items():
        with open(target / name, "x", encoding="utf-8") as handle:
            handle.write(text)
    out.write(texts["table.tsv"])


def main(argv=None, root=_JS3, corpus=seal_draw.CORPUS, now=None, out=None, err=None):
    out = out or sys.stdout
    err = err or sys.stderr
    parser = argparse.ArgumentParser(prog="measure.py", description="Candidate FILTER changes on the JS3 corpus.")
    parser.add_argument("--hand", default=HAND_FILE, metavar="PATH",
                        help=f"the hand-verdict file to measure against (default: {HAND_FILE})")
    args = parser.parse_args(argv)
    try:
        run(root, corpus, now or datetime.now(timezone.utc), out, hand=args.hand)
    except MeasureError as exc:
        err.write(f"error: {exc}\n")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
