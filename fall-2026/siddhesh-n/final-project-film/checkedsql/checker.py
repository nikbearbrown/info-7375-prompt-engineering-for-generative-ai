#!/usr/bin/env python3
"""checker.py — run every query in a folder against the campaign data and score it against the
answer key in tests/questions.json. Standard library only (sqlite3, csv, json).

    python3 checker.py                       # score queries/ (the baseline SQL)
    python3 checker.py --queries some/dir    # score another set (later: Claude's queries)
    python3 checker.py --label "my baseline" --save results/baseline.md

A file named q06.sql answers Q06; q06_trap_row_average.sql also answers Q06 but is reported
separately as a trap: a deliberately wrong query the checker is expected to FAIL.
"""
import argparse
import csv
import datetime
import json
import re
import sqlite3
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent


def load_db():
    con = sqlite3.connect(":memory:")
    con.execute("""CREATE TABLE campaigns (week INTEGER, campaign TEXT, channel TEXT, device TEXT,
                   impressions INTEGER, clicks INTEGER, conversions INTEGER, spend REAL, revenue REAL)""")
    with open(HERE / "data" / "campaigns.csv") as f:
        rows = [tuple(r.values()) for r in csv.DictReader(f)]
    con.executemany("INSERT INTO campaigns VALUES (?,?,?,?,?,?,?,?,?)", rows)
    return con


def run_query(con, sql):
    # Read-only contract: refuse anything but a single SELECT.
    body = re.sub(r"--.*", "", sql).strip().rstrip(";").strip()
    if not body.upper().startswith("SELECT") or ";" in body:
        raise ValueError("not a single read-only SELECT")
    row = con.execute(body).fetchone()
    return None if row is None else row[0]


def grade(test, got):
    if got is None:
        return False
    if test["type"] == "number":
        try:
            return abs(float(got) - float(test["expected"])) <= test.get("tolerance", 0) + 1e-9
        except (TypeError, ValueError):
            return False
    return str(got).strip().lower() == str(test["expected"]).strip().lower()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--queries", default=str(HERE / "queries"))
    ap.add_argument("--label", default="baseline queries")
    ap.add_argument("--save", help="also write the score table to this markdown file")
    a = ap.parse_args()

    tests = {t["id"]: t for t in json.load(open(HERE / "tests" / "questions.json"))}
    con = load_db()
    rows, score, traps_caught, traps = [], 0, 0, 0
    for path in sorted(Path(a.queries).glob("q*.sql")):
        qid = "Q" + path.stem[1:3]
        test = tests.get(qid)
        if not test:
            continue
        is_trap = "trap" in path.stem
        try:
            got, err = run_query(con, path.read_text()), ""
        except Exception as e:  # a broken query is a fail, not a crash
            got, err = None, str(e)
        ok = grade(test, got)
        if is_trap:
            traps += 1
            traps_caught += not ok
        else:
            score += ok
        rows.append((qid, path.name, test["question"], test["expected"], got if not err else f"ERROR: {err}",
                     ("FAIL (trap caught)" if not ok else "PASS (trap missed!)") if is_trap else ("PASS" if ok else "FAIL")))

    n = sum(1 for _, f, *_ in rows if "trap" not in f)
    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [f"# Score table: {a.label}", "", f"Run: {stamp} · data: data/campaigns.csv (24 synthetic rows)", "",
             "| Q | query file | question | expected | got | result |", "|---|---|---|---|---|---|"]
    lines += [f"| {q} | `{f}` | {qs} | {e} | {g} | {r} |" for q, f, qs, e, g, r in rows]
    lines += ["", f"**Score: {score}/{n}**" + (f" · traps caught: {traps_caught}/{traps}" if traps else "")]
    out = "\n".join(lines)
    print(out)
    if a.save:
        Path(a.save).parent.mkdir(parents=True, exist_ok=True)
        Path(a.save).write_text(out + "\n")
    sys.exit(0 if score == n and traps_caught == traps else 1)


if __name__ == "__main__":
    main()
