"""Draw the F5 held-out set: 20 postings Isaac has never labeled, for one-change-at-a-time runs (JS3 2.4).

Why it exists: the brief measures every change on labels held out from tuning. The 50 audit
labels can't be used (FILTER v2 rules A and B2 were designed from them), and JS1's 10 held-out
postings were already used in JS1's final run, where one label was corrected after seeing the
result (Isaac chose fresh labels only, 2026-11-25).

Who is drawn: postings that pass rules 1a, 1b and 2 under the current filter, i.e. every one that
reaches the JD checks (3-6) and that a scorer change could move. Postings cut on the title or
location alone would make both sides of every experiment agree and say nothing. Excluded: the 50
audit samples and the 20 JS1-labeled postings. Uniform random, fixed seed, verdicts hidden.

Run: .venv/bin/python reports/heldout_sample.py   -> heldout/to_judge.md, hand_verdicts.csv, sample_key.json
"""

import csv
import io
import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "reports"))

from audit_sample import CSV_HEADER, _filled_labels, to_judge_md  # noqa: E402

SEED = 20261125
N = 20


def pool(all_verdicts: list[dict], audit_key: dict, js1_ids: set[str]) -> list[dict]:
    seen = {(k["board"], str(k["posting_id"])) for k in audit_key.values()}
    return sorted((e for e in all_verdicts
                   if e["status"] == "ok" and e["failed_check"] not in ("1a", "1b", "2")
                   and (e["board"], str(e["posting_id"])) not in seen
                   and not (e["board"] == "stripe" and str(e["posting_id"]) in js1_ids)),
                  key=lambda e: (e["board"], str(e["posting_id"])))   # order-free input -> same draw


def main() -> int:
    out = ROOT / "heldout"
    filled = _filled_labels(out / "hand_verdicts.csv")
    if filled:   # Isaac's labels are never overwritten
        print(f"refusing to write: heldout/hand_verdicts.csv already has labels ({', '.join(filled)})", file=sys.stderr)
        return 1
    postings = json.loads((ROOT / "audit" / "all_verdicts.json").read_text())["postings"]
    key = json.loads((ROOT / "audit" / "sample_key.json").read_text())
    js1 = {r["posting_id"] for r in csv.DictReader((ROOT / "labels" / "labels.csv").open())}
    candidates = pool(postings, key, js1)
    picks = random.Random(SEED).sample(candidates, N)
    samples = [(f"H{i:02d}", p) for i, p in enumerate(picks, start=1)]
    buf = io.StringIO()
    w = csv.writer(buf, lineterminator="\n")
    w.writerow(CSV_HEADER)
    for sid, p in samples:
        w.writerow([sid, p["board"], str(p["posting_id"]), "", ""])
    out.mkdir(exist_ok=True)
    (out / "sample_key.json").write_text(json.dumps(
        {sid: {"board": p["board"], "posting_id": p["posting_id"], "title": p["title"], "raw_file": p["raw_file"],
               "v2_verdict": p["verdict"], "v2_failed_check": p["failed_check"], "seed": SEED, "pool": len(candidates)}
         for sid, p in samples}, indent=1, ensure_ascii=False) + "\n")
    (out / "hand_verdicts.csv").write_text(buf.getvalue(), newline="")
    (out / "to_judge.md").write_text(to_judge_md(samples).replace("# Postings to judge", "# Held-out postings to judge (F5)", 1))
    print(f"{N} held-out samples from a pool of {len(candidates)} (seed {SEED}) -> heldout/")
    return 0


if __name__ == "__main__":
    sys.exit(main())
