"""Shared helpers for the sampling report and the prompt experiment."""
import csv
import json
import random
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from jsagent import fetch, resume  # noqa: E402

# Real responses from the allow-listed host, all saved 2026-10-31 with full descriptions. Kept in experiments/source_raw so the
# 20-posting experiment set stays fixed while the watch (v3: every known Greenhouse board) keeps running.
RAWS = {
    "samsara": ROOT / "experiments" / "source_raw" / "2026-10-31T184610_samsara_live.json",
    "coinbase": ROOT / "experiments" / "source_raw" / "2026-10-31T165449_coinbase_live.json",
    "discord": ROOT / "experiments" / "source_raw" / "2026-10-31T165450_discord_live.json",
    "elastic": ROOT / "experiments" / "source_raw" / "2026-10-31T165450_elastic_live.json",
    "brex": ROOT / "experiments" / "source_raw" / "2026-10-31T165451_brex_live.json",
    "reddit": ROOT / "experiments" / "source_raw" / "2026-10-31T165451_reddit_live.json",
    "twilio": ROOT / "experiments" / "source_raw" / "2026-10-31T165452_twilio_live.json",
}
PERSONA = ROOT / "persona" / "evan-gordon.resume.json"
LABELS = ROOT / "experiments" / "prompt_experiment" / "labels.csv"
SEED = 7375
# The six postings the watch already showed Claude verdicts for; excluded so they can't anchor hand labels.
WATCHED = {"8141959", "7922530", "8250423", "8039914", "8281491", "8304547"}


def load_postings():
    out = {}
    for board, path in RAWS.items():
        for p in fetch.parse_postings(path.read_bytes()):
            out[p["id"]] = {**p, "board": board}
    return out


def load_resume():
    return resume.load_resume(PERSONA)


DATA_TITLE = re.compile(r"data engineer|analytics engineer|data platform|data infrastructure|data & analytics|"
                        r"analytics ai engineer|market data|data analyst", re.I)


def select_split():
    """No hand-picking: every data-titled posting on the 7 boards (incl. data analyst, CONTRACT v2.1), minus the 6
    watched ones, with repeated titles on the same board collapsed to the lowest id (Samsara lists one role in 8
    cities). That leaves 21; shuffled with seed 7375, the first 20 are split 10 dev / 10 held-out (one is left out)."""
    ps = load_postings()
    first = {}
    for pid in sorted(ps, key=int):
        p = ps[pid]
        if DATA_TITLE.search(p["title"]) and pid not in WATCHED:
            first.setdefault((p["board"], p["title"].strip().lower()), pid)
    chosen = sorted(first.values(), key=int)
    random.Random(SEED).shuffle(chosen)
    if len(chosen) > 20:
        print(f"pool {len(chosen)}; left out by the seeded shuffle: {chosen[20:]}", file=sys.stderr)
    return chosen[:10], chosen[10:20]


def read_labels():
    if not LABELS.exists():
        return {}
    with LABELS.open() as f:
        return {row["posting_id"]: row for row in csv.DictReader(f)}


def write_jsonl(path, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a") as f:
        for row in rows:
            f.write(json.dumps(row) + "\n")
