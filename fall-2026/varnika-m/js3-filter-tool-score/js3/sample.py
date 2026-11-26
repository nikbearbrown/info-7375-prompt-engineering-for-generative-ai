"""Draw the label sets of FILTER.md section 5 and write the blind labeling sheet.

    python3 -m js3.sample            # writes audit/sample.json, audit/labeling-sheet.md, audit/labels.csv

Seed 20261125 (fixed in FILTER.md before any label). No job is drawn twice: a posting whose
group (same company, title and description) was already drawn is skipped.
"""

import csv
import html
import json
import random
import re
import sys
from pathlib import Path

from js3.filter import group_key, run_filter, text_of
from js3.load import FOLDER, load, load_persona

SEED = 20261125
SIZES = {"reject": 30, "close_call": 8, "kept": 8, "held_out": 16}
QUALIFICATIONS = re.compile(r"(?i)(you may be a good fit|what we(?:'|’)re looking for|what you(?:'|’)ll need|"
                            r"requirements|qualifications|what we require|you have|about you|who you are|"
                            r"you might thrive|minimum)")


def draw(postings, results, shortlist, seed=SEED, sizes=SIZES):
    rng = random.Random(seed)
    used, sets = set(), {}

    def take(pool, n):
        pool = sorted(pool, key=lambda p: p["key"])
        rng.shuffle(pool)
        chosen = []
        for p in pool:
            if len(chosen) == n:
                break
            if group_key(p) not in used:
                used.add(group_key(p))
                chosen.append(p)
        return chosen

    score = {k: r["score"] for k, r in results.items()}
    sets["reject"] = take([p for p in postings if score[p["key"]] is not None and score[p["key"]] <= 3],
                          sizes["reject"])
    sets["close_call"] = take([p for p in postings if score[p["key"]] == 4], sizes["close_call"])
    sets["kept"] = take([item["posting"] for item in shortlist], sizes["kept"])
    sets["held_out"] = take([p for p in postings if score[p["key"]] is not None and score[p["key"]] >= 3],
                            sizes["held_out"])
    items = [(name, p) for name in ("reject", "close_call", "kept", "held_out") for p in sets[name]]
    rng.shuffle(items)
    return [{"item": n, "set": name, "key": p["key"], "group": group_key(p)} for n, (name, p) in enumerate(items, 1)]


def excerpt(posting, limit=1800):
    text = text_of(html.unescape(posting.get("content") or ""))
    match = QUALIFICATIONS.search(text)
    start = match.start() if match and match.start() > 200 else 0
    body = text[start:start + limit]
    return ("…" if start else "") + body + ("…" if start + limit < len(text) else "")


def sheet(items, by_key):
    lines = ["# Labeling sheet — JS3 (blind)", "",
             "Is each posting a real fit for Aarav Patel? Use my JS1 labeling rule "
             "(`../../js1-contract-and-watch/experiment/LABELING-RULE.md`): software engineering of his kind, "
             "he meets the **must-haves** (3 years or fewer), and a US location. Nice-to-haves never count.", "",
             "Aarav: Boston, MA; 29 months as a software engineer; TypeScript, Python, Java, SQL, Node.js, Kafka, "
             "Redis, MSSQL, PostgreSQL, AWS, Kubernetes, Docker, Helm, Fluent Bit, Jenkins. Rust and Terraform: "
             "familiar, not shipped.", "",
             "The postings are shuffled and the filter's verdict is hidden. Each excerpt starts at the "
             "qualifications when they can be found; the link has the full posting as of 2026-11-10 (it may have "
             "closed since; the saved text is what counts).", "",
             "**Answer format:** one line per item, `number Y` (fit) or `number N` (not fit), then a few words why. "
             "Example: `7 N sales role`.", ""]
    for item in items:
        p = by_key[item["key"]]
        lines += ["---", "", "### %d. %s — %s" % (item["item"], p.get("company_name"), p.get("title")), "",
                  "**Location:** %s · [posting](%s)" % ((p.get("location") or {}).get("name"), p.get("absolute_url")),
                  "", "> " + excerpt(p).replace("\n", " "), ""]
    return "\n".join(lines) + "\n"


def main(argv=None):
    postings, not_checked = load()
    if not_checked:
        print("not checked:", not_checked, file=sys.stderr)
    results, shortlist = run_filter(postings, load_persona())
    items = draw(postings, results, shortlist)
    by_key = {p["key"]: p for p in postings}
    out = FOLDER / "audit"
    out.mkdir(exist_ok=True)
    (out / "sample.json").write_text(json.dumps({"seed": SEED, "sizes": SIZES, "items": items}, indent=1) + "\n",
                                     encoding="utf-8")
    (out / "labeling-sheet.md").write_text(sheet(items, by_key), encoding="utf-8")
    with open(out / "labels.csv", "w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["item", "key", "label", "reason"])
        for item in items:
            writer.writerow([item["item"], item["key"], "", ""])
    print("%d items: %s" % (len(items), {k: sum(i["set"] == k for i in items) for k in SIZES}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
