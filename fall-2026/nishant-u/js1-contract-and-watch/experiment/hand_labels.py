"""Shared loaders for the experiment scripts: my hand labels, the sealed split, the baseline postings."""
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
HERE = ROOT / "experiment"
RAW = ROOT / "runs" / "2026-10-29-1" / "raw.json"
RAW_SHA256 = "3c10b536e3805bb5a4fca46800ac5caf4c521fa84c9beec30a8ab0beb995c2b7"
HELDOUT_SHA256 = "1cc26d9d144abe6ecfd2862f17fa39ceec331d6cb3d349ec3bb486aec163b5cc"


def split():
    """(dev ids, held-out ids); refuses a held-out file that doesn't match the sealed hash."""
    heldout_bytes = (HERE / "heldout_ids.json").read_bytes()
    if hashlib.sha256(heldout_bytes).hexdigest() != HELDOUT_SHA256:
        raise SystemExit("refused: heldout_ids.json does not match the sealed sha256")
    dev = json.loads((HERE / "dev_ids.json").read_text(encoding="utf-8"))
    return dev, json.loads(heldout_bytes)


def postings():
    """The baseline postings by id; refuses a raw.json that doesn't match the baseline sha256."""
    body = RAW.read_bytes()
    if hashlib.sha256(body).hexdigest() != RAW_SHA256:
        raise SystemExit("refused: raw.json does not match the baseline sha256")
    return {job["id"]: job for job in json.loads(body.decode("utf-8"))["jobs"]}


def hand_labels():
    """My labels by posting id: {"set", "my_label", "my_failed_check"} (notes are not read)."""
    with open(HERE / "labeling" / "labels.csv", encoding="utf-8-sig", newline="") as f:
        return {int(row["posting_id"]): {"set": row["set"], "my_label": row["my_label"].strip(),
                                         "my_failed_check": row["my_failed_check"].strip() or None}
                for row in csv.DictReader(f)}
