"""The reject audit (FILTER.md "How the filter will be measured").

    python3 audit.py draw       write state/audit/audit_v1.0.csv (for me to judge), audit_postings_v1.0.md, draw.json
    python3 audit.py report     after I have judged every row: k/n with a 95% interval per group

The draw, seeded and made only from postings outside the held-out set:
- kept: 10 random kept postings (all of them, if fewer than 10 are kept outside held-out)
- reject: 30 random rejected postings
- near: the 10 rejected postings closest to the threshold, meaning no reject rule fired and the score was
  highest below it (3, then 2, ...), ties broken by the seed. A posting a rule rejected is never "near",
  whatever its score: its distance from the threshold is not what decided it.
The three groups don't overlap. The sheet's order is shuffled, so the group is not visible while I judge.
I judge every row myself: "right" if the filter's verdict is what Riley's agent should have done, else "wrong".
"""
import csv
import io
import json
import math
import random
import sys

import corpus
import filter as F
from policy import Policy
from tools import Tools

SEED = 20261125
AUDITED = "1.0"  # the audit judged v1.0's verdicts; it stays pinned to v1.0
SIZES = {"kept": 10, "reject": 30, "near": 10}
COLUMNS = ["n", "key", "title", "location", "url", "verdict", "score", "why", "your_call", "reason"]


def held_out(tools):
    keys = set()
    for split in ("state/labels/split.json", "state/labels/split_v1_1.json"):
        keys |= {k for k, side in json.loads(tools.read_text(split))["split"].items() if side == "held-out"}
    return keys


def why(v):
    if v["rejected_by"]:
        return "; ".join(f"{rule}: \"{words}\"" for rule, words in sorted(v["rejected_by"].items()))
    signal = f"title: {v['title_signal']}" if v["title_signal"] else "title: no analyst"
    skills = ", ".join(v["skills"]) or "none"
    return f"score {v['score']} vs threshold {v['threshold']} ({signal}; skills: {skills})"


def draw(postings, excluded, seed=SEED):
    rng = random.Random(seed)
    pool = sorted((p for p in postings if p["key"] not in excluded), key=lambda p: p["key"])
    scored = [(p, F.evaluate(p, AUDITED)) for p in pool]
    kept = [x for x in scored if x[1]["verdict"] == "keep"]
    rejected = [x for x in scored if x[1]["verdict"] == "reject"]
    groups = {"kept": rng.sample(kept, min(SIZES["kept"], len(kept)))}
    groups["reject"] = rng.sample(rejected, SIZES["reject"])
    taken = {p["key"] for p, _ in groups["reject"]}
    by_score = [x for x in rejected if not x[1]["rejected_by"] and x[0]["key"] not in taken]
    rng.shuffle(by_score)
    by_score.sort(key=lambda x: -x[1]["score"])  # stable: the shuffle breaks ties
    groups["near"] = by_score[:SIZES["near"]]
    rows = [(name, p, v) for name, items in groups.items() for p, v in items]
    rng.shuffle(rows)
    return rows, {"pool": len(pool), "kept": len(kept), "rejected": len(rejected)}


def wilson(k, n, z=1.96):
    if n == 0:
        return None
    centre = (k + z * z / 2) / (n + z * z)
    half = z * math.sqrt(k * (n - k) / n + z * z / 4) / (n + z * z)
    return max(0.0, centre - half), min(1.0, centre + half)


def main(argv):
    tools = Tools(Policy())
    run, postings = corpus.load(tools)
    if argv[1:] == ["draw"]:
        rows, pool = draw(postings, held_out(tools))
        out = io.StringIO()
        w = csv.DictWriter(out, fieldnames=COLUMNS, lineterminator="\n")
        w.writeheader()
        md = [f"# Reject audit, filter v{AUDITED} ({len(rows)} postings)", "",
              "For each one, decide whether the filter's verdict is what Riley Navarro's agent should have done "
              "(fictional: entry-level Data/BI/Business Analyst, 0-2 years, US or US remote, needs sponsorship). "
              "Write `right` or `wrong` in `your_call` in `audit_v1.0.csv`, with a one-line reason.", ""]
        for n, (_, p, v) in enumerate(rows, 1):
            w.writerow({"n": n, "key": p["key"], "title": p["title"], "url": p["url"], "verdict": v["verdict"],
                        "score": v["score"], "why": why(v), "your_call": "", "reason": "",
                        "location": "; ".join(dict.fromkeys(p["locations"])) or "not given"})
            md += [f"## {n}. {p['title']}", "", f"- **Filter verdict:** {v['verdict']}: {why(v)}",
                   f"- **Location:** {'; '.join(dict.fromkeys(p['locations'])) or 'not given'}",
                   f"- **Link:** {p['url']}", "", p["text"] or "_No description text in the response._", ""]
        meta = {"filter": AUDITED, "seed": SEED, "sizes": SIZES, "pool": pool,
                "excluded": "every held-out label (split.json, split_v1_1.json)",
                "groups": {p["key"]: name for name, p, _ in rows}}
        tools.write_text(f"state/audit/audit_v{AUDITED}.csv", out.getvalue())
        tools.write_text(f"state/audit/audit_postings_v{AUDITED}.md", "\n".join(md) + "\n")
        tools.write_text(f"state/audit/draw_v{AUDITED}.json", json.dumps(meta, indent=1) + "\n")
        print(f"drew {len(rows)}: " + ", ".join(f"{k} {sum(g == k for g in meta['groups'].values())}"
                                               for k in SIZES) + f" from a pool of {pool}")
        return 0
    if argv[1:] == ["report"]:
        groups = json.loads(tools.read_text(f"state/audit/draw_v{AUDITED}.json"))["groups"]
        rows = list(csv.DictReader(tools.read_text(f"state/audit/audit_v{AUDITED}.csv").splitlines()))
        missing = [r["n"] for r in rows if r["your_call"].strip().lower() not in ("right", "wrong")]
        if missing:
            print(f"not judged yet: rows {', '.join(missing)}")
            return 1
        for name in list(SIZES) + ["all"]:
            sel = [r for r in rows if name == "all" or groups[r["key"]] == name]
            k = sum(r["your_call"].strip().lower() == "wrong" for r in sel)
            lo, hi = wilson(k, len(sel))
            print(f"{name:7} wrong {k}/{len(sel)}  95% interval {lo:.2f}-{hi:.2f}")
            for r in sel:
                if r["your_call"].strip().lower() == "wrong":
                    print(f"    #{r['n']} {r['verdict']} {r['title']}: {r['reason']}")
        return 0
    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv))
