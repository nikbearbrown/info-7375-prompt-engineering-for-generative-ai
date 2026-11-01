"""Freeze both prompts and the labels before the held-out run. Records hashes and time."""
import datetime as dt
import json
import os

from experiments.common import EXP, ROOT, sha256

FILES = ["prompts/baseline.txt", "prompts/revision.txt", "experiments/prompt/labels.csv"]
lock = {"locked_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sha256": {p: sha256(os.path.join(ROOT, p)) for p in FILES}}
path = os.path.join(EXP, "lock.json")
if os.path.exists(path):
    raise SystemExit("lock.json already exists")
with open(path, "w") as f:
    json.dump(lock, f, indent=1)
print(json.dumps(lock, indent=1))
