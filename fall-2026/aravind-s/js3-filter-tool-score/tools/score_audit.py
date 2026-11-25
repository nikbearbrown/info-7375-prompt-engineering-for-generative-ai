"""Score the reject audit: Aravind's committed verdicts against the sealed answers.

Reads the audit folder's VERDICTS.md and sealed/answers.json, after checking the answer file's SHA-256 against the
one SAMPLE.md published before any verdict, and the filter run's verdicts.json for the number of rejected postings.
Writes RESULTS.md in the audit folder and prints a short summary. Standard library only.

A miss is a posting the filter rejected that he marked Keep; a wrong keep is one it kept that he marked Reject;
a "?" is counted on its own, never as a mistake. Only the random rejects support a rate, so the miss bound uses
them alone: k misses in n judged random rejects, with the exact one-sided 95% upper bound (Clopper-Pearson).

Usage: python3 tools/score_audit.py js3/audit/<run> [--filter-run js3/filter-run/<run>]
"""
import argparse
import hashlib
import json
import math
import re
import sys
from pathlib import Path

ALPHA = 0.05
GROUPS = ["random reject", "kept sample", "close call: kept near the cutoff", "close call: failed one rule"]


def binom_cdf(k: int, n: int, p: float) -> float:
    return sum(math.comb(n, i) * p ** i * (1 - p) ** (n - i) for i in range(k + 1))


def upper_bound(k: int, n: int, alpha: float = ALPHA) -> float:
    """Exact one-sided upper confidence bound (Clopper-Pearson) for a rate seen as k of n."""
    if n <= 0:
        raise ValueError("n must be positive")
    if k >= n:
        return 1.0
    lo, hi = k / n, 1.0
    for _ in range(200):
        mid = (lo + hi) / 2
        if binom_cdf(k, n, mid) > alpha:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2


def read_verdicts(path: Path) -> dict:
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^\| (\d{2}) \| (Keep|Reject|\?) \| (.*) \|$", line)
        if m:
            rows[int(m.group(1))] = (m.group(2), m.group(3).strip())
    return rows


def read_after_reveal(path: Path) -> dict:
    """{card: (verdict, when, why, his words)} from AFTER-REVEAL.md: checks asked after the answers were opened.

    They never change VERDICTS.md; the results are reported both ways.
    """
    rows = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            m = re.match(r"^\| (\d{2}) \| (Keep|Reject|\?) \| (.*?) \| (.*?) \| (.*) \|$", line)
            if m:
                rows[int(m.group(1))] = tuple(x.strip() for x in m.group(2, 3, 4, 5))
    return rows


def published_hash(sample_md: Path) -> str:
    m = re.search(r"SHA-256 `([0-9a-f]{64})`", sample_md.read_text(encoding="utf-8"))
    if not m:
        raise SystemExit("STOP: SAMPLE.md publishes no SHA-256")
    return m.group(1)


def filter_side(a: dict) -> str:
    if a["fate"] == "kept":
        return f"kept, score {a['score']}"
    if a["fate"] == "rejected":
        rules = a["failed_rules"]
        return f"rejected by {a['deciding_rule']}" + (f" (also fails {', '.join(r for r in rules if r != a['deciding_rule'])})"
                                                      if len(rules) > 1 else " (its only failed rule)")
    return a["fate"]


def score(audit_dir: Path, filter_run: Path) -> dict:
    answers_path = audit_dir / "sealed" / "answers.json"
    digest = hashlib.sha256(answers_path.read_bytes()).hexdigest()
    if digest != published_hash(audit_dir / "SAMPLE.md"):
        raise SystemExit(f"STOP: sealed/answers.json has SHA-256 {digest}, not the one SAMPLE.md published")
    answers = {a["card"]: a for a in json.loads(answers_path.read_text(encoding="utf-8"))["answers"]}
    verdicts = read_verdicts(audit_dir / "VERDICTS.md")
    missing = sorted(set(answers) - set(verdicts))
    if missing:
        raise SystemExit(f"STOP: no verdict for cards {missing}")
    records = json.loads((filter_run / "verdicts.json").read_text(encoding="utf-8"))["records"]
    rejected_total = sum(1 for r in records if r["fate"] == "rejected")

    rows = []
    for card in sorted(answers):
        a, (his, note) = answers[card], verdicts[card]
        if his == "?":
            outcome = "?"
        elif (a["fate"] == "kept") == (his == "Keep"):
            outcome = "agree"
        else:
            outcome = "miss" if a["fate"] == "rejected" else "wrong keep"
        rows.append({"card": card, "title": a["title"].strip(), "group": a["group"], "filter": filter_side(a),
                     "fate": a["fate"], "deciding_rule": a.get("deciding_rule"), "failed_rules": a.get("failed_rules") or [],
                     "his": his, "note": note, "outcome": outcome})

    random_rejects = [r for r in rows if r["group"] == "random reject"]
    judged = [r for r in random_rejects if r["his"] != "?"]
    k = sum(1 for r in judged if r["outcome"] == "miss")
    n = len(judged)
    bound = upper_bound(k, n)
    result = {"digest": digest, "rows": rows, "rejected_total": rejected_total, "k": k, "n": n,
              "q": len(random_rejects) - n, "bound": bound, "after": None}
    after = read_after_reveal(audit_dir / "AFTER-REVEAL.md")
    if after:
        def verdict_after(r):
            return after[r["card"]][0] if r["card"] in after else r["his"]
        judged2 = [r for r in random_rejects if verdict_after(r) != "?"]
        k2 = sum(1 for r in judged2 if verdict_after(r) == "Keep")
        result["after"] = {"checks": after, "k": k2, "n": len(judged2), "q": len(random_rejects) - len(judged2),
                           "bound": upper_bound(k2, len(judged2))}
    return result


def write_results(audit_dir: Path, filter_run: Path, s: dict) -> str:
    rows = s["rows"]
    out = [f"# Audit results, filter run {audit_dir.name}", "",
           "Computed by `tools/score_audit.py` from Aravind's verdicts in VERDICTS.md (committed before the answers were "
           f"opened) and `sealed/answers.json` (SHA-256 `{s['digest']}`, the hash SAMPLE.md published before any verdict). "
           "Claude Code wrote the script and this file; the verdicts are his.", "",
           "## By group", "", "| Group | Cards | Agree | Miss | Wrong keep | ? |", "|---|---:|---:|---:|---:|---:|"]
    for g in GROUPS:
        sub = [r for r in rows if r["group"] == g]
        count = lambda o: sum(1 for r in sub if r["outcome"] == o)
        out.append(f"| {g} | {len(sub)} | {count('agree')} | {count('miss')} | {count('wrong keep')} | {count('?')} |")
    total = lambda o: sum(1 for r in rows if r["outcome"] == o)
    out += [f"| **all** | **{len(rows)}** | **{total('agree')}** | **{total('miss')}** | **{total('wrong keep')}** | "
            f"**{total('?')}** |", "",
            "## The miss count (random rejects only)", "",
            f"{s['k']} misses in {s['n']} judged random rejects ({s['q']} marked ?). As a sample result: {s['k']}/{s['n']}. "
            f"The exact one-sided 95% upper bound (Clopper-Pearson) is {s['bound'] * 100:.1f}%, which for the "
            f"{s['rejected_total']} postings this run rejected means up to about {round(s['bound'] * s['rejected_total'])} "
            "misses. This bounds what the sample supports; it is not a measured rate for every reject.", ""]
    a = s["after"]
    if a:
        out += ["## With the checks asked after the reveal (AFTER-REVEAL.md)", "",
                "These were asked after `sealed/answers.json` was opened, so they are reported beside the frozen result, "
                "never in place of it. VERDICTS.md is unchanged.", "",
                "| Card | Frozen verdict | After the reveal | When | Why it was asked | His words |", "|---|---|---|---|---|---|"]
        frozen = {r["card"]: r["his"] for r in rows}
        for card, (verdict, when, why, words) in sorted(a["checks"].items()):
            out.append(f"| {card:02d} | {frozen.get(card, '')} | {verdict} | {when} | {why} | {words} |")
        out += ["", f"With these checks: {a['k']} misses in {a['n']} judged random rejects ({a['q']} marked ?); the exact "
                f"one-sided 95% upper bound is {a['bound'] * 100:.1f}%, up to about "
                f"{round(a['bound'] * s['rejected_total'])} of the {s['rejected_total']} rejected postings.", ""]
    out += ["## Every disagreement and every ?", "",
            "| Card | Title | Group | Filter | His verdict | His note |", "|---|---|---|---|---|---|"]
    for r in rows:
        if r["outcome"] != "agree":
            label = {"miss": "Keep (miss)", "wrong keep": "Reject (wrong keep)", "?": "?"}[r["outcome"]]
            out.append(f"| {r['card']:02d} | {r['title']} | {r['group']} | {r['filter']} | {label} | {r['note']} |")
    misses = [r for r in rows if r["outcome"] == "miss"]
    out += ["", "## Misses by the rule that decided them", ""]
    if misses:
        by_rule = {}
        for r in misses:
            by_rule.setdefault(r["deciding_rule"], []).append(r)
        out += ["| Rule | Misses | Cards | Of these, the only rule the posting failed |", "|---|---:|---|---:|"]
        for rule in sorted(by_rule):
            cards = by_rule[rule]
            only = sum(1 for r in cards if r["failed_rules"] == [rule])
            card_list = ", ".join("%02d" % r["card"] for r in cards)  # no nested f-string: Python 3.9 must parse this
            out.append(f"| {rule} | {len(cards)} | {card_list} | {only} |")
    else:
        out.append("No misses.")
    text = "\n".join(out) + "\n"
    (audit_dir / "RESULTS.md").write_text(text, encoding="utf-8")
    return text


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("audit_dir", type=Path)
    ap.add_argument("--filter-run", type=Path, default=None)
    args = ap.parse_args(argv)
    filter_run = args.filter_run or args.audit_dir.parents[1] / "filter-run" / args.audit_dir.name
    s = score(args.audit_dir, filter_run)
    write_results(args.audit_dir, filter_run, s)
    outcomes = {}
    for r in s["rows"]:
        outcomes[r["outcome"]] = outcomes.get(r["outcome"], 0) + 1
    print(f"answers hash OK ({s['digest'][:12]}...); outcomes: {outcomes}")
    print(f"random rejects: {s['k']} misses in {s['n']} judged ({s['q']} ?); 95% upper bound {s['bound'] * 100:.1f}% "
          f"= up to about {round(s['bound'] * s['rejected_total'])} of {s['rejected_total']} rejects")
    if s["after"]:
        a = s["after"]
        print(f"with the checks after the reveal: {a['k']} misses in {a['n']}; bound {a['bound'] * 100:.1f}% "
              f"= up to about {round(a['bound'] * s['rejected_total'])}")
    print(f"wrote {args.audit_dir / 'RESULTS.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
