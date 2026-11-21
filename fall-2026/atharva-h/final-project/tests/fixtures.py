"""A small synthetic LCA database for tests. Every row is invented; no real filing."""

import json
import sqlite3
from pathlib import Path

from sponsorsql.config import FIELDS

FIXTURE_SHA = "synthetic-test-fixture"

# (CASE_NUMBER, CASE_STATUS, VISA_CLASS, JOB_TITLE, EMPLOYER_NAME, CITY, STATE, WAGE, UNIT, LEVEL)
ROWS = [
    ("T-001", "Certified", "H-1B", "Data Analyst", "Example Data LLC", "Boston", "MA", "80000", "Year", "I"),
    ("T-002", "Certified", "H-1B", "Data-Analyst", "Example Data, LLC", "Boston", "MA", "82000", "Year", "II"),
    ("T-003", "Certified", "H-1B", "Senior Data  Analyst", "Example Data LLC", "Boston", "MA", "50", "Hour", "III"),
    ("T-004", "Certified", "H-1B", "Metadata Analyst", "Sample Corp", "Boston", "MA", "90000", "Year", "II"),
    ("T-005", "Certified - Withdrawn", "H-1B", "Data Analyst", "Sample Corp", "Boston", "MA", "70000", "Year", "I"),
    ("T-006", "Certified", "E-3 Australian", "Data Analyst", "Sample Corp", "Boston", "MA", "75000", "Year", "I"),
    ("T-007", "Certified", "H-1B", "Data Analyst", "Sample Corp", "Cambridge", "MA", "85000", "Year", ""),
    ("T-008", "Denied", "H-1B", "Data Engineer", "Sample Corp", "Austin", "TX", "95000", "Year", "II"),
    ("T-009", "Certified", "H-1B", "Business Analyst", "Fictional Inc", "Austin", "TX", "72000", "Year", "I"),
    ("T-010", "Certified", "H-1B", "Data Scientist", "Fictional Inc", "Austin", "TX", "120000", "Year", "II"),
    ("T-011", "Withdrawn", "H-1B", "Data Analyst", "Fictional Inc", "Boston", "MA", "78000", "Year", "I"),
    ("T-012", "Certified", "H-1B", "Data Analysts", "Fictional Inc", "Boston", "MA", "79000", "Year", "I"),
]


def build(path):
    path = Path(path)
    if path.exists():
        path.unlink()
    con = sqlite3.connect(path)
    cols = ", ".join(f'"{n}" TEXT' for n in FIELDS)
    con.execute(f"CREATE TABLE lca (sheet_row INTEGER PRIMARY KEY, {cols})")
    con.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
    con.execute("INSERT INTO metadata VALUES ('source_sha256', ?)", (FIXTURE_SHA,))
    for i, (case, status, visa, title, employer, city, state, wage, unit, level) in enumerate(ROWS, start=2):
        record = {n: None for n in FIELDS}
        record.update(CASE_NUMBER=case, CASE_STATUS=status, VISA_CLASS=visa, JOB_TITLE=title,
                      EMPLOYER_NAME=employer, WORKSITE_CITY=city, WORKSITE_STATE=state,
                      WAGE_RATE_OF_PAY_FROM=wage, WAGE_UNIT_OF_PAY=unit, PW_WAGE_LEVEL=level,
                      DECISION_DATE="2026-05-01", SOC_CODE="15-2051.00", EMPLOYER_FEIN="00-0000000")
        con.execute(f"INSERT INTO lca VALUES (?, {', '.join('?' for _ in FIELDS)})",
                    (i, *[record[n] for n in FIELDS]))
    con.commit()
    con.close()
    return path


BOSTON_ROWS_SQL = ("SELECT sheet_row, CASE_NUMBER, CASE_STATUS, VISA_CLASS, EMPLOYER_NAME, JOB_TITLE, "
                   "WORKSITE_CITY, WORKSITE_STATE FROM lca WHERE CASE_STATUS='Certified' "
                   "AND VISA_CLASS='H-1B' AND title_has(JOB_TITLE,'data analyst')=1 "
                   "AND UPPER(TRIM(WORKSITE_CITY))='BOSTON'")


def reply(sql, rows_sql=BOSTON_ROWS_SQL, answer_type="count", clarify=False):
    return json.dumps({"interpretation": "test reply", "sql": sql, "rows_sql": rows_sql,
                       "answer_type": answer_type, "limits": [], "needs_clarification": clarify})
