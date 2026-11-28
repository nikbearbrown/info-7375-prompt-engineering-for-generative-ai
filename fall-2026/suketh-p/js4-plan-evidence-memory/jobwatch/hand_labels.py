"""The student's hand labels (2026-11-24), read from the table they typed outside the labelling
page and pasted in chat. The page's own download at 18:51 held no labels, so the pasted table is
the record; labels/hand-labels-as-pasted.tsv keeps it as pasted.

parse() changes no word. A row is ID, verdict and reason, separated by tabs. Lines above the
"ID / Verdict / Reason" header are the student's legend and are kept as written.

development_rows() compares the filter with the labels for the development groups only. The two
held-out groups (sample.HELD_OUT) never enter it; they are measured once, after the student has
chosen a change (reports/ONE-CHANGE.md)."""

from jobwatch import measure, sample

HEADER = ("ID", "Verdict", "Reason")
VERDICTS = {"yes": "yes", "no": "no", "can’t tell": "cannot tell", "can't tell": "cannot tell"}


def parse(text, ids):
    lines = text.splitlines()
    header_at = next((n for n, line in enumerate(lines)
                      if tuple(cell.strip() for cell in line.split("\t")) == HEADER), None)
    if header_at is None:
        raise ValueError("no 'ID<TAB>Verdict<TAB>Reason' header line")
    labels = {}
    for n, line in enumerate(lines[header_at + 1:], start=header_at + 2):
        if not line.strip():
            continue
        cells = [cell.strip() for cell in line.split("\t")]
        if len(cells) != 3:
            raise ValueError(f"line {n}: expected an ID, a verdict and a reason separated by tabs")
        label_id, verdict, reason = cells
        if verdict.lower() not in VERDICTS:
            raise ValueError(f"line {n}: unknown verdict {verdict!r}")
        if not reason:
            raise ValueError(f"line {n}: {label_id} has no reason")
        if label_id in labels:
            raise ValueError(f"line {n}: {label_id} appears twice")
        labels[label_id] = {"label": VERDICTS[verdict.lower()], "verdict_as_written": verdict, "reason": reason}
    wanted = list(ids)
    missing = [i for i in wanted if i not in labels]
    unknown = [i for i in labels if i not in set(wanted)]
    if missing or unknown:
        raise ValueError(f"labels missing for {missing}; labels for IDs not in the sample: {unknown}")
    return {"legend": [line for line in lines[:header_at] if line.strip()],
            "labels": {i: labels[i] for i in wanted}}


def development_rows(members, labels, records):
    """measure.compare rows for the development groups only, each with its label ID, group and reason."""
    rows = []
    for m in sample.development(members):
        key = (m["board"], m["key"])
        row = measure.compare({key: labels[m["label_id"]]["label"]}, {key: records[key]})[0]
        rows.append({"label_id": m["label_id"], "stratum": m["stratum"], **row,
                     "reason": labels[m["label_id"]]["reason"]})
    return rows
