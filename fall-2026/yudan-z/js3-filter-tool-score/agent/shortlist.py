"""Build the source-grounded shortlist from a filter run.

python -m agent.shortlist runs/filter-v4.jsonl
Writes runs/shortlist-<version>.md (top 10 with every claim) and runs/shortlist-<version>.csv (every posting shown).
Every line comes from the run file, which comes from the posting text; nothing is added here.
"""
import csv
import json
import os
import sys


def main(path, top=10):
    rows = [json.loads(line) for line in open(path, encoding="utf-8")]
    version = os.path.basename(path).replace("filter-", "").replace(".jsonl", "")
    shown = [r for r in rows if r["decision"] != "reject"]
    shown.sort(key=lambda r: (-r["score"], r["title"].strip()))
    post = {}
    for line in open("data/postings.jsonl", encoding="utf-8"):
        p = json.loads(line)
        post[p["key"]] = p
    with open(f"runs/shortlist-{version}.csv", "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["score", "decision", "company", "title", "location", "url", "why it cannot tell"]
                   + [c["claim"] for c in shown[0]["claims"] if shown] if shown else [])
        for r in shown:
            labels = {c["claim"]: c["label"] for c in r["claims"]}
            w.writerow([r["score"], r["decision"], r["board"], r["title"].strip(), r["location"], post[r["key"]]["url"],
                        "; ".join(r["abstain_reasons"])] + [labels.get(c["claim"], "") for c in shown[0]["claims"]])
    out = [f"# Shortlist, filter {version}", "",
           f"{len(shown)} of {len(rows)} saved postings reach Mira "
           f"({sum(r['decision'] == 'keep' for r in shown)} keep, "
           f"{sum(r['decision'] == 'cannot tell' for r in shown)} cannot tell). "
           f"The top {min(top, len(shown))} by score are below; every posting is in `shortlist-{version}.csv`.", ""]
    for i, r in enumerate(shown[:top], 1):
        out += [f"## {i}. {r['title'].strip()} ({r['board']})", "",
                f"{r['location']} · score {r['score']} · **{r['decision']}**"
                + (f" ({'; '.join(r['abstain_reasons'])})" if r["abstain_reasons"] else ""),
                f"<{post[r['key']]['url']}>", "", "| Claim | Label | Evidence from the posting |", "|---|---|---|"]
        out += [f"| {c['claim']} | {c['label']} | {c['evidence'].replace('|', '/')} |" for c in r["claims"]]
        out.append("")
    open(f"runs/shortlist-{version}.md", "w", encoding="utf-8").write("\n".join(out))
    print(f"{len(shown)} shown -> runs/shortlist-{version}.md, runs/shortlist-{version}.csv")


if __name__ == "__main__":
    main(sys.argv[1])
