"""Shared pieces for the Prompt Experiment (Chapter 2) scripts."""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPLIT = ROOT / "logs" / "experiment_split.json"
LABELS = {"dev": ROOT / "logs" / "experiment_dev_labels.md",
          "heldout": ROOT / "logs" / "experiment_heldout_labels.md"}
RAW_ROOT = ROOT / "logs" / "experiment_raw"

_LABEL_LINE = re.compile(
    r"^\s*\d+\.\s+(\d+)\s+\(.*?\):\s+(Relevant|Not relevant)\s+[—-]+\s+(.+)$")


def split_ids(name):
    return json.loads(SPLIT.read_text())[name]


def read_labels(name):
    """{posting_id: (verdict, reason)} from a hand-label file. Fails loudly if
    the file doesn't label exactly the ids in that split."""
    labels = {}
    for line in LABELS[name].read_text().splitlines():
        m = _LABEL_LINE.match(line)
        if m:
            pid = int(m.group(1))
            if pid in labels:
                raise ValueError(f"{pid} labeled twice in {LABELS[name].name}")
            labels[pid] = (m.group(2).lower(), m.group(3).strip())
    expected = set(split_ids(name))
    if set(labels) != expected:
        raise ValueError(f"{LABELS[name].name} labels {sorted(labels)} but the "
                         f"{name} split is {sorted(expected)}")
    return labels
