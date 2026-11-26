"""JS3 Step 6: what moves the score. One change at a time, chosen on tuning labels, measured once on the locked held-out labels.

Metrics against Ethan's hand labels (labels/labels.csv):
- kept precision / recall: does bucket == kept match human_label == relevant?
- score AUC: the chance a relevant posting outscores a not-relevant one (ties count half), over every labeled posting with a
  score. This measures the numbers in the score, not only the gates.

Wrong version W8 (tuning on the held-out labels) is blocked in code: choose() accepts tuning results only, held-out
measurement checks labels/HELDOUT_LOCK.json first, and each change may be measured on held-out once (labels/HELDOUT_LOG.jsonl).
"""
import contextlib
import csv
import hashlib
import io
import json
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from . import filter as flt

ROOT = Path(__file__).resolve().parent.parent
LABELS = ROOT / "labels" / "labels.csv"
LOCK = ROOT / "labels" / "HELDOUT_LOCK.json"
LOG = ROOT / "labels" / "HELDOUT_LOG.jsonl"


class HeldoutViolation(Exception):
    pass


# ------------------------------------------------------------------ the single changes (each one alone against v1.2)
# The measurements in HELDOUT_LOG.jsonl were made against v1.2, so "baseline" puts v1.2 back (no change A, no "internship"
# in F2) and every change is v1.2 plus that one change. v1.3 = v1.2 + A + "internship" (FILTER.md change log).
_V12 = [(flt, "F1_ENGINEER_DATA", False), (flt, "_EXCL", [(w, rx) for w, rx in flt._EXCL if w != "internship"])]

CHANGES = {
    "baseline": ("FILTER.md v1.2 as written", _V12),
    "A_f1_engineer_data": ("F1 also passes an Engineer/Developer title containing the whole word 'Data' or 'Pipeline'",
                           [_V12[1], (flt, "F1_ENGINEER_DATA", True)]),
    "B_threshold_1": ("T3 threshold 2 -> 1 distinct topic word", _V12 + [(flt, "THRESHOLD", 1)]),
    "C_threshold_3": ("T3 threshold 2 -> 3 distinct topic words", _V12 + [(flt, "THRESHOLD", 3)]),
    "D_no_years_bonus": ("Years <= 3 bonus +16 -> 0", _V12 + [(flt, "POINTS", dict(flt.POINTS, years=0))]),
    "E_no_location_bonus": ("Boston +10 / remote US +5 -> 0 / 0",
                            _V12 + [(flt, "POINTS", dict(flt.POINTS, boston=0, remote_us=0))]),
}


@contextlib.contextmanager
def applied(change):
    patches = CHANGES[change][1]
    saved = [(m, a, getattr(m, a)) for m, a, _ in patches]
    try:
        for m, a, v in patches:
            setattr(m, a, v)
        yield
    finally:
        for m, a, v in saved:
            setattr(m, a, v)


# ------------------------------------------------------------------ labels and the lock
def load_labels(path=LABELS):
    return list(csv.DictReader(Path(path).open()))


def heldout_hash(rows):
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    for r in rows:
        if r["split"] == "heldout":
            w.writerow([r["board"], r["posting_id"], r["human_label"]])
    return hashlib.sha256(buf.getvalue().encode()).hexdigest()


def check_lock(rows, lock_path=LOCK):
    lock = json.loads(Path(lock_path).read_text())
    if heldout_hash(rows) != lock["heldout_sha256"]:
        raise HeldoutViolation("held-out labels differ from the locked hash in HELDOUT_LOCK.json")


# ------------------------------------------------------------------ metrics
def evaluate_split(postings_by_key, rows, split, change="baseline"):
    sel = [r for r in rows if r["split"] == split]
    with applied(change):
        res = [(r["human_label"] == "relevant", flt.evaluate(postings_by_key[(r["board"], r["posting_id"])])) for r in sel]
    tp = sum(1 for rel, e in res if rel and e["bucket"] == "kept")
    kept = sum(1 for _, e in res if e["bucket"] == "kept")
    relevant = sum(1 for rel, _ in res if rel)
    pos = [e["score"] for rel, e in res if rel and e["score"] is not None]
    neg = [e["score"] for rel, e in res if not rel and e["score"] is not None]
    pairs = len(pos) * len(neg)
    auc = (sum((p > n) + 0.5 * (p == n) for p in pos for n in neg) / pairs) if pairs else None
    return {"change": change, "split": split, "n": len(sel), "relevant": relevant, "kept": kept, "kept_and_relevant": tp,
            "precision": tp / kept if kept else None, "recall": tp / relevant if relevant else None,
            "score_auc": auc, "missed": [e["title"] for rel, e in res if rel and e["bucket"] != "kept"],
            "wrongly_kept": [e["title"] for rel, e in res if not rel and e["bucket"] == "kept"]}


def choose(results):
    """Pick changes from TUNING results only (W8): any held-out result passed in is refused."""
    if any(r["split"] != "tuning" for r in results):
        raise HeldoutViolation("choose() only accepts tuning results; held-out labels never choose a change")
    return results


def measure_heldout(postings_by_key, change, rows=None, log_path=LOG, lock_path=LOCK):
    rows = rows if rows is not None else load_labels()
    check_lock(rows, lock_path)
    log_path = Path(log_path)
    done = [json.loads(x)["change"] for x in log_path.read_text().splitlines()] if log_path.exists() else []
    if change in done:
        raise HeldoutViolation(f"{change} was already measured on held-out; each change gets one look")
    out = evaluate_split(postings_by_key, rows, "heldout", change)
    entry = dict(out, measured_at=datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds"))
    with log_path.open("a") as f:
        f.write(json.dumps(entry) + "\n")
    return out
