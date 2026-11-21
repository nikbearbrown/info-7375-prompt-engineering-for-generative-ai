"""Run SQLite ports of the October Claude SQL and compare with the frozen key.

This runs the draft queries' filters and grouping logic, not new Claude output.
DuckDB-only syntax is translated: ILIKE to lower/LIKE, TRY_CAST to CAST,
MEDIAN to a local aggregate, and DATE_TRUNC to substr of the ISO date.
The source draft and the independent answer key remain separate files.
"""

import argparse
import hashlib
import json
import sqlite3
import statistics


class Median:
    def __init__(self):
        self.values = []

    def step(self, value):
        if value is not None:
            self.values.append(float(value))

    def finalize(self):
        return statistics.median(self.values) if self.values else None


QUERIES = {
    "q1": """SELECT EMPLOYER_NAME, COUNT(*) AS cases FROM lca
        WHERE CASE_STATUS='Certified' AND VISA_CLASS='H-1B'
          AND lower(JOB_TITLE) LIKE '%data analyst%' AND WORKSITE_STATE='MA'
        GROUP BY EMPLOYER_NAME ORDER BY cases DESC, EMPLOYER_NAME LIMIT 10""",
    "q2": """SELECT COUNT(DISTINCT CASE_NUMBER) FROM lca
        WHERE CASE_STATUS='Certified' AND VISA_CLASS='H-1B'
          AND lower(JOB_TITLE) LIKE '%data analyst%'
          AND UPPER(TRIM(WORKSITE_CITY))='BOSTON' AND WORKSITE_STATE='MA'""",
    "q3": """SELECT UPPER(TRIM(WORKSITE_CITY)) AS city, WORKSITE_STATE AS state,
          COUNT(*) AS cases FROM lca WHERE CASE_STATUS='Certified'
          AND VISA_CLASS='H-1B' AND lower(JOB_TITLE) LIKE '%data analyst%'
        GROUP BY city, state ORDER BY cases DESC, city, state LIMIT 10""",
    "q4": """SELECT WORKSITE_STATE AS state, COUNT(*) AS cases,
          MEDIAN(CAST(WAGE_RATE_OF_PAY_FROM AS REAL) *
            CASE WAGE_UNIT_OF_PAY WHEN 'Year' THEN 1 WHEN 'Month' THEN 12
              WHEN 'Bi-Weekly' THEN 26 WHEN 'Week' THEN 52 WHEN 'Hour' THEN 2080 END)
          AS median_annual_offer FROM lca WHERE CASE_STATUS='Certified'
          AND VISA_CLASS='H-1B' AND lower(JOB_TITLE) LIKE '%data analyst%'
        GROUP BY state HAVING COUNT(*) >= 20
        ORDER BY median_annual_offer DESC""",
    "q5": """SELECT PW_WAGE_LEVEL, COUNT(*) AS cases FROM lca
        WHERE CASE_STATUS='Certified' AND VISA_CLASS='H-1B'
          AND lower(JOB_TITLE) LIKE '%data analyst%'
        GROUP BY PW_WAGE_LEVEL ORDER BY PW_WAGE_LEVEL""",
    "q6": """SELECT EMPLOYER_NAME, COUNT(*) AS level_1_cases FROM lca
        WHERE CASE_STATUS='Certified' AND VISA_CLASS='H-1B'
          AND PW_WAGE_LEVEL='I'
          AND (lower(JOB_TITLE) LIKE '%data analyst%'
            OR lower(JOB_TITLE) LIKE '%business analyst%'
            OR lower(JOB_TITLE) LIKE '%bi analyst%'
            OR lower(JOB_TITLE) LIKE '%business intelligence analyst%')
        GROUP BY EMPLOYER_NAME ORDER BY level_1_cases DESC, EMPLOYER_NAME LIMIT 25""",
    "q7": """SELECT EMPLOYER_NAME, JOB_TITLE, COUNT(*) AS cases FROM lca
        WHERE CASE_STATUS='Certified' AND VISA_CLASS='H-1B'
          AND lower(EMPLOYER_NAME) LIKE '%capgemini america%'
          AND (lower(JOB_TITLE) LIKE '%data%' OR lower(JOB_TITLE) LIKE '%analyst%')
        GROUP BY EMPLOYER_NAME, JOB_TITLE ORDER BY cases DESC, EMPLOYER_NAME, JOB_TITLE""",
    "q8": """SELECT JOB_TITLE, COUNT(*) AS cases FROM lca
        WHERE CASE_STATUS='Certified' AND VISA_CLASS='H-1B'
          AND SOC_CODE LIKE '15-2051%'
        GROUP BY JOB_TITLE ORDER BY cases DESC, JOB_TITLE LIMIT 20""",
    "q9": """SELECT substr(DECISION_DATE,1,7) AS month, COUNT(*) AS cases
        FROM lca WHERE CASE_STATUS='Certified' AND VISA_CLASS='H-1B'
          AND lower(JOB_TITLE) LIKE '%data analyst%'
        GROUP BY month ORDER BY month""",
    "q10": """SELECT EMPLOYER_NAME, COUNT(*) AS certified_then_withdrawn
        FROM lca WHERE CASE_STATUS='Certified - Withdrawn' AND VISA_CLASS='H-1B'
          AND lower(JOB_TITLE) LIKE '%data analyst%'
        GROUP BY EMPLOYER_NAME ORDER BY certified_then_withdrawn DESC, EMPLOYER_NAME
        LIMIT 10""",
}


def digest(path):
    with open(path, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def compare(name, rows, key):
    if name == "q1":
        expected = [(x["name"], x["cases"]) for x in key["q1_massachusetts_employers_top10"]]
        actual = [(x[0], x[1]) for x in rows]
    elif name == "q2":
        expected, actual = key["q2_boston_cases"], rows[0][0]
    elif name == "q3":
        expected = [(x["name"], x["cases"]) for x in key["q3_cities_top10"]]
        actual = [(f"{x[0]}, {x[1]}", x[2]) for x in rows]
    elif name == "q4":
        expected = key["q4_median_annual_base_wage_by_state"]
        actual = {x[0]: {"median_usd": round(x[2], 2), "cases": x[1]} for x in rows}
    elif name == "q5":
        expected = key["q5_wage_levels"]
        actual = {(x[0] or "[blank]"): x[1] for x in rows}
    elif name == "q6":
        expected = [(x["name"], x["cases"]) for x in key["q6_level_i_data_role_all_employers"]]
        actual = [(x[0], x[1]) for x in rows]
    elif name == "q7":
        expected = {x["name"]: x["cases"] for x in key["q7_capgemini_all_titles"]}
        actual = {}
        for _, title, count in rows:
            actual[title] = actual.get(title, 0) + count
    elif name == "q8":
        expected = [(x["name"], x["cases"]) for x in key["q8_soc_data_scientist_titles_top10"]]
        actual = [(x[0], x[1]) for x in rows[:10]]
    elif name == "q9":
        expected = key["q9_certified_data_analyst_cases_by_decision_month"]
        actual = {x[0]: x[1] for x in rows}
    else:
        expected = [(x["name"], x["cases"]) for x in key["q10_certified_withdrawn_employers_top10"]]
        actual = [(x[0].strip(), x[1]) for x in rows]
    return actual == expected, actual, expected


def main(database, key_path, draft_path, output):
    with open(key_path, encoding="utf-8") as f:
        key = json.load(f)
    con = sqlite3.connect(database)
    con.create_aggregate("MEDIAN", 1, Median)
    results = {}
    for name, sql in QUERIES.items():
        rows = con.execute(sql).fetchall()
        passed, actual, expected = compare(name, rows, key)
        results[name] = {"pass": passed, "actual": actual, "expected": expected,
                         "sql_port": sql, "returned_rows": len(rows)}
    con.close()
    result = {"source_draft_sha256": digest(draft_path),
              "frozen_key_sha256": digest(key_path),
              "port_note": "SQLite syntax translation only; output-shape comparison follows the independent key's written rules.",
              "passes": sum(x["pass"] for x in results.values()),
              "total": len(results), "results": results}
    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.write("\n")
    for name, item in results.items():
        print(name, "PASS" if item["pass"] else "FAIL", "rows", item["returned_rows"])
    print(f"{result['passes']}/{result['total']} pass")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database")
    parser.add_argument("key")
    parser.add_argument("draft")
    parser.add_argument("output")
    args = parser.parse_args()
    main(args.database, args.key, args.draft, args.output)
