"""Load the selected public LCA fields into SQLite with Python's standard library.

Usage: python3 evals/load_lca_sqlite.py SOURCE.xlsx OUTPUT.sqlite
The contact, attorney, and preparer fields are deliberately excluded.
"""

import argparse
import hashlib
import os
import re
import sqlite3
import sys
import zipfile
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta


NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
EXPECTED_SHA256 = "f8ca8448a528671f784d3692923775a13741c99caec2816b2fe30c8885bd28b3"
FIELDS = (
    "CASE_NUMBER", "CASE_STATUS", "DECISION_DATE", "VISA_CLASS", "JOB_TITLE",
    "SOC_CODE", "SOC_TITLE", "TOTAL_WORKER_POSITIONS", "EMPLOYER_NAME",
    "TRADE_NAME_DBA", "EMPLOYER_FEIN", "WORKSITE_CITY", "WORKSITE_STATE",
    "WAGE_RATE_OF_PAY_FROM", "WAGE_RATE_OF_PAY_TO", "WAGE_UNIT_OF_PAY",
    "PW_WAGE_LEVEL", "TOTAL_WORKSITE_LOCATIONS",
)


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def shared_strings(z):
    values = []
    with z.open("xl/sharedStrings.xml") as f:
        events = ET.iterparse(f, events=("start", "end"))
        _, root = next(events)
        for event, el in events:
            if event == "end" and el.tag == NS + "si":
                values.append("".join(el.itertext()))
                root.clear()
    return values


def text_of_cell(el, strings):
    value = el.find(NS + "v")
    if el.get("t") == "inlineStr":
        inline = el.find(NS + "is")
        return "".join(inline.itertext()) if inline is not None else None
    if value is None:
        return None
    return strings[int(value.text)] if el.get("t") == "s" else value.text


def iso_excel_date(value):
    if value is None or value == "":
        return None
    return (datetime(1899, 12, 30) + timedelta(days=float(value))).date().isoformat()


def rows(z, strings):
    with z.open("xl/worksheets/sheet1.xml") as f:
        events = ET.iterparse(f, events=("start", "end"))
        _, root = next(events)
        current = {}
        header = None
        columns = None
        for event, el in events:
            if event == "end" and el.tag == NS + "c":
                letters = re.match(r"[A-Z]+", el.get("r")).group(0)
                if header is None or letters in columns:
                    current[letters] = text_of_cell(el, strings)
                el.clear()
            elif event == "end" and el.tag == NS + "row":
                row_number = int(el.get("r"))
                if header is None:
                    header = current
                    columns = {letter: name for letter, name in header.items() if name in FIELDS}
                    missing = set(FIELDS) - set(columns.values())
                    if missing:
                        raise ValueError(f"Missing expected fields: {sorted(missing)}")
                elif current:
                    named = {name: current.get(letter) for letter, name in columns.items()}
                    if any(value not in (None, "") for value in named.values()):
                        named["DECISION_DATE"] = iso_excel_date(named["DECISION_DATE"])
                        yield row_number, tuple(named[name] for name in FIELDS)
                current = {}
                root.clear()


def load(source, destination):
    digest = sha256(source)
    if digest != EXPECTED_SHA256:
        raise ValueError(f"Workbook checksum differs: {digest}")
    temporary = destination + ".partial"
    if os.path.exists(temporary):
        os.remove(temporary)
    con = sqlite3.connect(temporary)
    try:
        cols = ", ".join(f'"{name}" TEXT' for name in FIELDS)
        con.execute(f'CREATE TABLE lca (sheet_row INTEGER PRIMARY KEY, {cols})')
        con.execute("CREATE TABLE metadata (key TEXT PRIMARY KEY, value TEXT NOT NULL)")
        con.execute("INSERT INTO metadata VALUES (?, ?)", ("source_sha256", digest))
        con.execute("INSERT INTO metadata VALUES (?, ?)", ("source_file", os.path.basename(source)))
        placeholders = ", ".join("?" for _ in range(len(FIELDS) + 1))
        insert = f"INSERT INTO lca VALUES ({placeholders})"
        count = 0
        with zipfile.ZipFile(source) as z:
            strings = shared_strings(z)
            batch = []
            for sheet_row, values in rows(z, strings):
                batch.append((sheet_row, *values))
                if len(batch) >= 5000:
                    con.executemany(insert, batch)
                    count += len(batch)
                    batch.clear()
                    if count % 50000 == 0:
                        print(f"loaded {count:,} populated rows", flush=True)
            if batch:
                con.executemany(insert, batch)
                count += len(batch)
        con.execute("INSERT INTO metadata VALUES (?, ?)", ("populated_rows", str(count)))
        con.commit()
        if count != 437496:
            raise ValueError(f"Expected 437,496 populated rows, got {count:,}")
    except BaseException:
        con.close()
        if os.path.exists(temporary):
            os.remove(temporary)
        raise
    con.close()
    os.replace(temporary, destination)
    print(f"loaded {count:,} populated rows into {destination}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source")
    parser.add_argument("destination")
    args = parser.parse_args()
    load(args.source, args.destination)
