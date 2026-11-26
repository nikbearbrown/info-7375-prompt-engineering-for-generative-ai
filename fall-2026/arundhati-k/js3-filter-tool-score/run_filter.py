"""Run a filter version on the saved snapshot and draw the audit sample.

python3 run_filter.py [--version v1] [--seed 7375]
Writes out/<version>/decisions.json and (first run only) audit/sample.csv with the filter verdict column HIDDEN
in audit/to-judge.md, so hand verdicts are made blind.
"""
import csv
import json
import random
import sys
from collections import Counter
from pathlib import Path

from jsagent3.filter import decide, load_rules
from jsagent3.mcp_server import load_postings

HERE = Path(__file__).resolve().parent


def arg(name, default):
    a = sys.argv[1:]
    return a[a.index(name) + 1] if name in a else default


def main():
    version, seed = arg("--version", "v1"), int(arg("--seed", "7375"))
    rules = load_rules(version)
    posts = load_postings()
    decisions = [decide(p, rules) for p in posts.values()]
    out = HERE / "out" / version
    out.mkdir(parents=True, exist_ok=True)
    (out / "decisions.json").write_text(json.dumps(decisions, indent=0))
    kept = [d for d in decisions if d["keep"]]
    rej = [d for d in decisions if not d["keep"]]
    close = [d for d in decisions if d["close_call"]]
    print(f"{version}: {len(decisions)} postings, kept {len(kept)}, rejected {len(rej)}, close calls {len(close)}")
    print("reject reasons:", Counter(d["reason"].split(":")[0].split(" <")[0] for d in rej).most_common())

    sample_path = HERE / "audit" / "sample.csv"
    if sample_path.exists() or "--no-sample" in sys.argv:
        return
    rng = random.Random(seed)
    s_rej = rng.sample([d for d in rej if not d["close_call"]], 32)
    s_close = sorted(close, key=lambda d: d["id"])
    s_close = rng.sample(s_close, min(12, len(s_close)))
    s_kept = rng.sample([d for d in kept if not d["close_call"]], 10)
    rows = [("random_reject", d) for d in s_rej] + [("close_call", d) for d in s_close] + \
           [("kept_sample", d) for d in s_kept]
    rng.shuffle(rows)  # so the judge cannot infer the filter verdict from position
    sample_path.parent.mkdir(exist_ok=True)
    with sample_path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "id", "stratum", "filter_keep", "filter_reason", "topics", "my_verdict", "my_note"])
        for n, (stratum, d) in enumerate(rows, 1):
            w.writerow([n, d["id"], stratum, d["keep"], d["reason"], " ".join(d["topics"]), "", ""])
    with (HERE / "audit" / "to-judge.md").open("w") as f:
        f.write(f"# Postings to judge (seed {seed}), filter verdict hidden\n\n"
                "For each: would this be worth Rohan's time? Answer Y or N (and a few words if it's not obvious).\n\n")
        for n, (_, d) in enumerate(rows, 1):
            p = posts[d["id"]]
            f.write(f"**{n}.** {p['title']} — {p['location'] or '(no location)'} — {p['url']}\n\n")
    print(f"sample: {len(rows)} rows -> {sample_path}")


if __name__ == "__main__":
    main()
