import json
import sys
import zipfile
import xml.etree.ElementTree as ET
import re

source, keypath = sys.argv[1:]
ns = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
with zipfile.ZipFile(source) as z:
    strings = []
    with z.open("xl/sharedStrings.xml") as f:
        events = ET.iterparse(f, events=("start", "end"))
        _, root = next(events)
        for event, el in events:
            if event == "end" and el.tag == ns + "si":
                strings.append("".join(el.itertext()))
                root.clear()
    want = {"A", "B", "F", "G", "BR", "BT"}
    hits = set()
    cur = {}
    with z.open("xl/worksheets/sheet1.xml") as f:
        events = ET.iterparse(f, events=("start", "end"))
        _, root = next(events)
        for event, el in events:
            if event == "end" and el.tag == ns + "c":
                col = re.match(r"[A-Z]+", el.get("r")).group(0)
                if col in want:
                    v = el.find(ns + "v")
                    if v is not None:
                        cur[col] = strings[int(v.text)] if el.get("t") == "s" else v.text
                el.clear()
            elif event == "end" and el.tag == ns + "row":
                title = re.sub(r"[^a-z0-9]+", " ", cur.get("G", "").casefold()).strip()
                if (cur.get("B") == "Certified" and cur.get("F") == "H-1B"
                    and cur.get("BR", "").strip().upper() == "BOSTON"
                    and cur.get("BT", "").strip().upper() == "MA"
                    and " data analyst " in f" {title} "):
                    hits.add(cur.get("A"))
                cur = {}
                root.clear()
key = json.load(open(keypath))
expected = {row["case_number"] for row in key["q2_matching_rows"]}
print(json.dumps({"direct_source_case_numbers": len(hits),
                  "key_case_numbers": len(expected),
                  "sets_equal": hits == expected}, indent=2))
