"""Count ten fixed LCA questions independently of the draft Claude SQL.

Usage: python3 evals/build_answer_key.py DATABASE.sqlite OUTPUT.json
The input database is produced by load_lca_sqlite.py from the checked workbook.
"""

import argparse
import json
import re
import sqlite3
import statistics
from collections import Counter, defaultdict


SOURCE_SHA256 = "f8ca8448a528671f784d3692923775a13741c99caec2816b2fe30c8885bd28b3"


def normalized(value):
    return re.sub(r"[^a-z0-9]+", " ", (value or "").casefold()).strip()


def title_has(value, phrase):
    return f" {phrase} " in f" {normalized(value)} "


def ranked(counter, limit=None):
    pairs = sorted(counter.items(), key=lambda item: (-item[1], item[0]))
    if limit is not None:
        pairs = pairs[:limit]
    return [{"name": name, "cases": count} for name, count in pairs]


def main(database, output):
    con = sqlite3.connect(database)
    con.row_factory = sqlite3.Row
    metadata = dict(con.execute("SELECT key, value FROM metadata"))
    if metadata.get("source_sha256") != SOURCE_SHA256:
        raise ValueError("The database does not match the checked source workbook")

    status = Counter()
    visa = Counter()
    q1 = Counter()
    q2 = []
    q3 = Counter()
    q4 = defaultdict(list)
    q5 = Counter()
    q6 = Counter()
    q7 = Counter()
    q7_spelling = Counter()
    q8 = Counter()
    q9 = Counter()
    q10 = Counter()
    amazon = Counter()
    total = 0
    capgemini_fein = set()

    for row in con.execute("SELECT * FROM lca ORDER BY sheet_row"):
        total += 1
        case_status = (row["CASE_STATUS"] or "").strip()
        visa_class = (row["VISA_CLASS"] or "").strip()
        title = row["JOB_TITLE"] or ""
        employer = (row["EMPLOYER_NAME"] or "").strip()
        city = (row["WORKSITE_CITY"] or "").strip().upper()
        state = (row["WORKSITE_STATE"] or "").strip().upper()
        level = (row["PW_WAGE_LEVEL"] or "").strip().upper() or "[blank]"
        data_analyst = title_has(title, "data analyst")
        data_role = any(title_has(title, phrase) for phrase in
                        ("data analyst", "business analyst", "bi analyst"))
        status[case_status] += 1
        visa[visa_class] += 1

        if normalized(employer) == "amazon data services inc":
            amazon[employer] += 1

        if visa_class == "H-1B" and (row["SOC_CODE"] or "").startswith("15-2051"):
            q8[title.strip()] += 1

        if visa_class == "H-1B" and data_analyst and case_status == "Certified - Withdrawn":
            q10[employer] += 1

        if visa_class != "H-1B" or case_status != "Certified":
            continue

        if data_role and level == "I":
            q6[employer] += 1
        if data_role and normalized(employer) == "capgemini america inc":
            q7[title.strip()] += 1
            q7_spelling[employer] += 1
            capgemini_fein.add(row["EMPLOYER_FEIN"])

        if not data_analyst:
            continue
        if state == "MA":
            q1[employer] += 1
            if city == "BOSTON":
                q2.append({
                    "sheet_row": row["sheet_row"],
                    "case_number": row["CASE_NUMBER"],
                    "employer": employer,
                    "job_title": title,
                    "worksite_city": city,
                    "worksite_state": state,
                })
        if city and state:
            q3[f"{city}, {state}"] += 1
        q5[level] += 1
        date = row["DECISION_DATE"]
        if date:
            q9[date[:7]] += 1
        if (row["WAGE_UNIT_OF_PAY"] or "").strip() == "Year":
            wage = row["WAGE_RATE_OF_PAY_FROM"]
            if wage not in (None, ""):
                q4[state].append(float(wage))

    con.close()
    if total != 437496 or status != Counter({"Certified": 401412,
                                             "Certified - Withdrawn": 26303,
                                             "Withdrawn": 7224, "Denied": 2557}):
        raise ValueError("Loaded row/status control totals disagree with source profile")
    if len(capgemini_fein) != 1:
        raise ValueError(f"Capgemini spellings are not one employer ID: {capgemini_fein}")

    result = {
        "source_sha256": SOURCE_SHA256,
        "populated_rows": total,
        "case_status_control": dict(status),
        "visa_class_control": dict(visa),
        "definitions": {
            "case": "one populated spreadsheet row, not a worker position or visa approval",
            "certified": "CASE_STATUS exactly Certified; Certified - Withdrawn is separate",
            "title": "case-insensitive whole phrase after punctuation becomes spaces; senior titles are included",
            "worksite": "the one WORKSITE_CITY/STATE pair disclosed on this row; additional worksites cannot be located from this file",
            "employer": "EMPLOYER_NAME as filed, including spelling variants, except Q7's explicitly named Capgemini variants",
            "wage": "WAGE_RATE_OF_PAY_FROM where WAGE_UNIT_OF_PAY is Year; other units are excluded rather than converted",
        },
        "q1_massachusetts_employers_top10": ranked(q1, 10),
        "q1_total_cases": sum(q1.values()),
        "q2_boston_cases": len(q2),
        "q2_matching_rows": q2,
        "q3_cities_top10": ranked(q3, 10),
        "q3_total_cases_with_city_and_state": sum(q3.values()),
        "q4_median_annual_base_wage_by_state": {
            state: {"median_usd": round(statistics.median(values), 2), "cases": len(values)}
            for state, values in sorted(q4.items()) if state
        },
        "q4_total_annual_wage_cases": sum(len(values) for values in q4.values()),
        "q5_wage_levels": dict(sorted(q5.items())),
        "q5_total_cases": sum(q5.values()),
        "q6_level_i_data_role_employers_count": len(q6),
        "q6_level_i_data_role_cases": sum(q6.values()),
        "q6_level_i_data_role_employers_top10": ranked(q6, 10),
        "q6_level_i_data_role_all_employers": ranked(q6),
        "q7_capgemini_case_count": sum(q7.values()),
        "q7_capgemini_spellings": dict(q7_spelling),
        "q7_capgemini_titles_top10": ranked(q7, 10),
        "q7_capgemini_all_titles": ranked(q7),
        "q8_soc_data_scientist_titles_top10": ranked(q8, 10),
        "q8_total_h1b_cases_all_statuses": sum(q8.values()),
        "q9_certified_data_analyst_cases_by_decision_month": dict(sorted(q9.items())),
        "q9_total_cases": sum(q9.values()),
        "q10_certified_withdrawn_employers_top10": ranked(q10, 10),
        "q10_total_cases": sum(q10.values()),
        "amazon_data_services_spelling_diagnostic_all_statuses": dict(amazon),
    }
    with open(output, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
        f.write("\n")
    print(json.dumps({"q2_boston_cases": len(q2),
                      "q6_employer_names": len(q6),
                      "q7_capgemini_cases": sum(q7.values()),
                      "q8_soc_cases": sum(q8.values()),
                      "q10_withdrawn_cases": sum(q10.values())}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database")
    parser.add_argument("output")
    args = parser.parse_args()
    main(args.database, args.output)
