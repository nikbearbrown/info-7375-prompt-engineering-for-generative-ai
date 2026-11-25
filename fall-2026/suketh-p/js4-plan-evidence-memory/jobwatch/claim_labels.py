"""The student's claim labels (2026-11-25), read from the summary they pasted in chat.

The paste gives one label per claim suffix and says the same labels apply to every rank, R1 through
R8. A table of notes follows, by claim ID. A note row may name IDs ("R1-C3, R5-C3") or a suffix at
every rank ("C7 at all eight ranks"). parse() changes no word: labels and notes are copied, and the
text around the tables is kept as written. FILTER.md asks that an insufficient or contradicted
claim record what decides it or what is missing, so each one needs a note."""

import re

LABELS = ("supported", "contradicted", "insufficient")
RANK_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8,
              "nine": 9, "ten": 10}
_SUFFIX = re.compile(r"C\d+")
_EVERY_RANK = re.compile(r"(C\d+) at all (\w+) ranks", re.I)


def _cells(line):
    return [cell.strip() for cell in line.split("\t")]


def _rows_after(lines, header_at):
    rows, n = [], header_at + 1
    while n < len(lines) and lines[n].strip():
        rows.append(_cells(lines[n]))
        n += 1
    return rows, n


def _note_header(line):
    cells = _cells(line)
    if len(cells) == 2 and cells[1] == "Note" and cells[0].lower().endswith(" claim ids"):
        label = cells[0][: -len(" claim ids")].strip().lower()
        if label in LABELS:
            return label
    return None


def parse(text, claim_ids):
    lines = text.splitlines()
    wanted = list(claim_ids)
    ranks = sorted({i.split("-")[0] for i in wanted}, key=lambda r: int(r[1:]))
    suffix_headers = [n for n, line in enumerate(lines) if _cells(line)[:2] == ["Claim suffix", "Label"]]
    if len(suffix_headers) != 1:
        raise ValueError("expected exactly one 'Claim suffix<TAB>Label' table")
    suffix_rows, last = _rows_after(lines, suffix_headers[0])
    labels = {}
    for cells in suffix_rows:
        if len(cells) != 2:
            raise ValueError(f"expected suffixes and a label separated by a tab: {cells!r}")
        label = cells[1].lower()
        if label not in LABELS:
            raise ValueError(f"unknown label {cells[1]!r}")
        for suffix in (s.strip() for s in cells[0].split(",")):
            if not _SUFFIX.fullmatch(suffix):
                raise ValueError(f"not a claim suffix: {suffix!r}")
            for rank in ranks:
                claim_id = f"{rank}-{suffix}"
                if claim_id not in wanted:
                    raise ValueError(f"{claim_id} is not one of the claims")
                if claim_id in labels:
                    raise ValueError(f"{claim_id} is labelled twice")
                labels[claim_id] = {"label": label, "label_as_written": cells[1], "note": None}
    missing = [i for i in wanted if i not in labels]
    if missing:
        raise ValueError(f"no label for {missing}")

    first = suffix_headers[0]
    for header_at, line in enumerate(lines):
        note_label = _note_header(line)
        if note_label is None:
            continue
        first = min(first, header_at)
        rows, end = _rows_after(lines, header_at)
        last = max(last, end)
        for cells in rows:
            if len(cells) != 2:
                raise ValueError(f"expected claim IDs and a note separated by a tab: {cells!r}")
            targets, note = cells
            every = _EVERY_RANK.fullmatch(targets)
            if every:
                count = every.group(2).lower()
                if (int(count) if count.isdigit() else RANK_WORDS.get(count)) != len(ranks):
                    raise ValueError(f"{targets!r}: there are {len(ranks)} ranks")
                ids = [f"{rank}-{every.group(1)}" for rank in ranks]
            else:
                ids = [t.strip() for t in targets.split(",")]
            for claim_id in ids:
                if claim_id not in labels:
                    raise ValueError(f"{claim_id} is not one of the claims")
                if labels[claim_id]["label"] != note_label:
                    raise ValueError(f"{claim_id} is {labels[claim_id]['label']}, but its note is filed under {note_label}")
                if labels[claim_id]["note"] is not None:
                    raise ValueError(f"{claim_id} has two notes")
                labels[claim_id]["note"] = note
    for claim_id, entry in labels.items():
        if entry["label"] in ("insufficient", "contradicted") and not entry["note"]:
            raise ValueError(f"{claim_id} is {entry['label']} with no note saying what decides it")
    return {"labels": {i: labels[i] for i in wanted},
            "text_before": [line for line in lines[:first] if line.strip()],
            "text_after": [line for line in lines[last:] if line.strip()]}
