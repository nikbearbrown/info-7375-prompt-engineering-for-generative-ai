"""Each candidate change alone, measured on the audit's TUNING sets only (random rejects, close calls, kept, gate close
calls), against my pass-2 hand labels. This is where changes were chosen; the held-out set is measured separately with
`python3 -m agent measure` (SCORE-REPORT.md).

    python3 scripts/tune_changes.py
"""
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)
os.chdir(HERE)

from agent import audit, collection, config, filter as filt, resume  # noqa: E402
from agent.policy import Policy  # noqa: E402

policy = Policy()
sample = json.loads(open("audit/sample.json").read())
labels = audit.read_labels(open("audit/hand-labels-pass2.csv").read())
postings, _ = collection.load_run(config.RUNS_DIR / sample["run"], policy)
jobs = {f"{b}:{j['id']}": (b, j) for b, j in postings}
persona = resume.load(config.RESUME)
tune = list(dict.fromkeys(k for name, keys in sample["sets"].items() if name != "held_out" for k in keys))
files = ["filters/v1.0.json"] + sorted(glob.glob("filters/changes/*.json")) + ["filters/v1.1.json"]
print(f"tuning postings: {len(tune)} (held-out set not read)")
print("| Filter file | Agrees with my label | Keeps (tuning) | Keeps (all 589) | False keeps | False rejects |")
print("|---|---|---|---|---|---|")
for path in files:
    spec = filt.load_filter(path)
    r = audit.measure([(path, spec)], tune, jobs, persona, labels)[0]
    everywhere = sum(filt.decide(j, b, persona, spec).verdict == filt.KEEP for b, j in postings)
    title = lambda keys: ", ".join(jobs[k][1]["title"].strip() for k in keys) or "none"
    print(f"| `{path}` | {r['agree']} of {r['judged']} | {r['kept']} | {everywhere} | {title(r['false_keeps'])} | {len(r['false_rejects'])} |")
