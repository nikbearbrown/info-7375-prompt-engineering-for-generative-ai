"""Write the blind judging sheets (filter verdict hidden) for the audit sample and a separate held-out set.

python3 make_judge_sheets.py   -- seed 7376 for held-out; held-out excludes every audit-sample id.
"""
import csv
import json
import random
from pathlib import Path

from jsagent3.evidence import sections
from jsagent3.mcp_server import load_postings

HERE = Path(__file__).resolve().parent


def snippet(p, n=4):
    req = [ln for k, ln in sections(p["body"]) if k == "required" and ln.startswith("-")]
    return " / ".join(x.lstrip("- ")[:110] for x in req[:n])


def sheet(path, title, rows, posts):
    with path.open("w") as f:
        f.write(f"# {title}\n\nFilter verdict hidden. For each: is this worth Rohan's time (Java/Spring backend, "
                "co-op / intern / early career)? Answer `n Y` or `n N`, plus a few words when it isn't obvious.\n\n")
        for n, pid in rows:
            p = posts[pid]
            f.write(f"**{n}.** {p['title']} — {p['location'] or '(no location)'}  \n{p['url']}  \n")
            s = snippet(p)
            if s:
                f.write(f"> {s}\n")
            f.write("\n")


def main():
    posts = load_postings()
    audit = list(csv.DictReader((HERE / "audit" / "sample.csv").open()))
    sheet(HERE / "audit" / "to-judge.md", "Audit sample (seed 7375, 54 postings)",
          [(int(r["n"]), r["id"]) for r in audit], posts)
    decisions = json.loads((HERE / "out" / "v1" / "decisions.json").read_text())
    taken = {r["id"] for r in audit}
    pool = [d for d in decisions if d["role"] and d["id"] not in taken]  # role-titled: where scoring matters
    rng = random.Random(7376)
    held = rng.sample(sorted(pool, key=lambda d: d["id"]), 20)
    hp = HERE / "labels" / "heldout.csv"
    hp.parent.mkdir(exist_ok=True)
    with hp.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "id", "my_label", "my_note"])
        for n, d in enumerate(held, 1):
            w.writerow([n, d["id"], "", ""])
    sheet(HERE / "labels" / "heldout-to-judge.md", "Held-out set (seed 7376, 20 role-titled postings, not in audit)",
          [(n, d["id"]) for n, d in enumerate(held, 1)], posts)
    print(len(audit), "audit rows;", len(held), "held-out rows; pool", len(pool))


if __name__ == "__main__":
    main()
