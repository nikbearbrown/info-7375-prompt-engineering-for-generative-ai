"""profile_lca.py — profile the FY2026 Q3 LCA disclosure workbook without loading it into a database.

Python standard library only (zipfile + streaming XML). Reads a handful of columns and writes:
  - distinct values (with row counts) of CASE_STATUS, VISA_CLASS, WAGE_UNIT_OF_PAY
  - the shape of WORKSITE_STATE values (two-letter codes or full names)
  - employers whose EMPLOYER_FEIN appears under more than one EMPLOYER_NAME spelling
  - how many sheet rows are completely blank (the sheet declares ~595k empty rows after the data)

It answers none of the SponsorSQL test questions: no filtering by job, city or status,
and no case counts per employer beyond rows per spelling.

Usage: python3 profile_lca.py <path to LCA_Disclosure_Data_FY2026_Q3.xlsx> profile-FY2026-Q3.json
"""
import json
import re
import sys
import zipfile
import xml.etree.ElementTree as ET
from collections import Counter, defaultdict

NS = "{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
WANT = ["CASE_STATUS", "VISA_CLASS", "EMPLOYER_NAME", "TRADE_NAME_DBA",
        "EMPLOYER_FEIN", "WORKSITE_STATE", "WAGE_UNIT_OF_PAY"]


def col_letters(ref):
    return re.match(r"[A-Z]+", ref).group(0)


def main(xlsx, out):
    z = zipfile.ZipFile(xlsx)
    rows, header, colmap = [], None, {}
    with z.open("xl/worksheets/sheet1.xml") as f:
        cur = {}
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag == NS + "c":
                letters = col_letters(el.get("r"))
                if header is None or letters in colmap:
                    t = el.get("t")
                    v = el.find(NS + "v")
                    if t == "s" and v is not None:
                        cur[letters] = ("s", int(v.text))
                    elif t == "inlineStr":
                        cur[letters] = ("v", "".join(el.find(NS + "is").itertext()))
                    elif v is not None:
                        cur[letters] = ("v", v.text)
                el.clear()
            elif el.tag == NS + "row":
                if header is None:
                    header = cur
                else:
                    rows.append(tuple(cur.get(colmap_rev[n]) for n in WANT))
                cur = {}
                el.clear()
                if header is not None and not colmap:
                    # resolve header after first row (shared strings needed)
                    header_idx = {k: v for k, v in header.items()}
                    names = resolve(z, {v[1] for v in header_idx.values() if v[0] == "s"})
                    hdr = {k: (names[v[1]] if v[0] == "s" else v[1]) for k, v in header_idx.items()}
                    colmap = {k: n for k, n in hdr.items() if n in WANT}
                    colmap_rev = {n: k for k, n in colmap.items()}
                    missing = [n for n in WANT if n not in colmap_rev]
                    if missing:
                        sys.exit(f"missing columns: {missing}")

    need = {c[1] for r in rows for c in r if c and c[0] == "s"}
    strings = resolve(z, need)
    val = lambda c: None if c is None else (strings[c[1]] if c[0] == "s" else c[1])

    status, visa, unit, state_shape = Counter(), Counter(), Counter(), Counter()
    fein_names = defaultdict(Counter)
    blank = sum(1 for r in rows if all(c is None for c in r))
    data_rows = [r for r in rows if not all(c is None for c in r)]
    for r in data_rows:
        s, v, name, dba, fein, st, u = (val(c) for c in r)
        status[s] += 1
        visa[v] += 1
        unit[u] += 1
        state_shape["two-letter" if st and re.fullmatch(r"[A-Z]{2}", st) else f"other:{st}"] += 1
        if fein and name:
            fein_names[fein][name] += 1

    variants = []
    for fein, names in fein_names.items():
        if len(names) > 1:
            variants.append({"spellings": dict(names.most_common()), "rows": sum(names.values())})
    variants.sort(key=lambda x: -x["rows"])

    other_states = {k: n for k, n in state_shape.items() if k != "two-letter"}
    result = {
        "file": xlsx.split("/")[-1],
        "sheet_rows_after_header": len(rows),
        "blank_rows": blank,
        "data_rows": len(data_rows),
        "CASE_STATUS": dict(status.most_common()),
        "VISA_CLASS": dict(visa.most_common()),
        "WAGE_UNIT_OF_PAY": dict(unit.most_common()),
        "WORKSITE_STATE_two_letter_rows": state_shape["two-letter"],
        "WORKSITE_STATE_other_values": dict(Counter(other_states).most_common(20)),
        "employers_with_multiple_spellings": len(variants),
        "top_multi_spelling_employers": variants[:60],
        "note": "Employer ID (EMPLOYER_FEIN) used only to group spellings; not written out.",
    }
    json.dump(result, open(out, "w"), indent=2, ensure_ascii=False)
    print(json.dumps({k: result[k] for k in ("sheet_rows_after_header", "blank_rows", "data_rows", "CASE_STATUS", "VISA_CLASS", "WAGE_UNIT_OF_PAY",
                                             "WORKSITE_STATE_two_letter_rows", "employers_with_multiple_spellings")}, indent=1))


def resolve(z, need):
    out, i = {}, -1
    if not need:
        return out
    top = max(need)
    with z.open("xl/sharedStrings.xml") as f:
        for _, el in ET.iterparse(f, events=("end",)):
            if el.tag == NS + "si":
                i += 1
                if i in need:
                    out[i] = "".join(el.itertext())
                el.clear()
                if i >= top:
                    break
    return out


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
