"""Count the five held-out questions independently of any model SQL.

Usage: python3 evals/build_heldout_key.py DATABASE.sqlite OUTPUT.json
Same definitions as ANSWER-KEY.md: exact statuses and visa class, whole-phrase
title match after normalization, the recorded worksite, filed employer names
(trimmed), Year wages only, alphabetical tie-break. Rows are read one by one and
counted in Python; no aggregate SQL is used.
"""

import argparse
import json
import re
import sqlite3
import statistics
from collections import Counter

SOURCE_SHA256 = "f8ca8448a528671f784d3692923775a13741c99caec2816b2fe30c8885bd28b3"


def normalized(value):
    return re.sub(r"[^a-z0-9]+", " ", (value or "").casefold()).strip()


def title_has(value, phrase):
    return f" {phrase} " in f" {normalized(value)} "


def main(database, output):
    con = sqlite3.connect(database)
    con.row_factory = sqlite3.Row
    if dict(con.execute("SELECT key, value FROM metadata")).get("source_sha256") != SOURCE_SHA256:
        raise ValueError("database does not match the checked source workbook")
    h1 = 0
    h2 = Counter()
    h3 = []
    h4 = Counter()
    h5 = 0
    total = 0
    for row in con.execute("SELECT * FROM lca ORDER BY sheet_row"):
        total += 1
        status = (row["CASE_STATUS"] or "").strip()
        visa = (row["VISA_CLASS"] or "").strip()
        title = row["JOB_TITLE"] or ""
        city = (row["WORKSITE_CITY"] or "").strip().upper()
        state = (row["WORKSITE_STATE"] or "").strip().upper()
        if visa != "H-1B":
            continue
        if status == "Denied" and title_has(title, "data engineer"):
            h5 += 1
        if status != "Certified":
            continue
        if state == "TX" and title_has(title, "business analyst"):
            h1 += 1
        if city == "BOSTON" and state == "MA":
            h2[(row["EMPLOYER_NAME"] or "").strip()] += 1
        if (state == "CA" and title_has(title, "data scientist")
                and (row["WAGE_UNIT_OF_PAY"] or "").strip() == "Year"
                and row["WAGE_RATE_OF_PAY_FROM"] not in (None, "")):
            h3.append(float(row["WAGE_RATE_OF_PAY_FROM"]))
        if (row["SOC_CODE"] or "").startswith("15-2051"):
            h4[(row["PW_WAGE_LEVEL"] or "").strip().upper() or "[blank]"] += 1
    con.close()
    if total != 437496:
        raise ValueError(f"expected 437,496 rows, found {total:,}")
    ranked = sorted(h2.items(), key=lambda item: (-item[1], item[0]))[:10]
    result = {
        "source_sha256": SOURCE_SHA256,
        "populated_rows": total,
        "h1_count": h1,
        "h2_boston_employers_top10": [{"name": n, "cases": c} for n, c in ranked],
        "h2_total_cases": sum(h2.values()),
        "h3_median_usd": round(statistics.median(h3), 2),
        "h3_cases": len(h3),
        "h4_wage_levels": dict(sorted(h4.items())),
        "h4_total_cases": sum(h4.values()),
        "h5_count": h5,
    }
    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.write("\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database")
    parser.add_argument("output")
    args = parser.parse_args()
    main(args.database, args.output)
