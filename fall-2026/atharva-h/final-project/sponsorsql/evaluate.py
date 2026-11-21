"""Scores agent answers against an answer key the model never sees.

Each question id maps to a comparator that turns the executed SQL result into
the key's shape. Comparison is exact after trimming text (and to the cent for
wages). A run that stops without an answer scores as a fail.
"""

import hashlib
import json
from pathlib import Path


def _s(value):
    return "" if value is None else str(value).strip()


def _i(value):
    return int(float(value))


def _pairs(rows, upper=False):
    out = []
    for row in rows:
        label = ", ".join(_s(v) for v in row[:-1])
        out.append((label.upper() if upper else label, _i(row[-1])))
    return out


def _named(columns, rows, want):
    """Pick columns by name fragments (e.g. 'median', 'case'); fall back to position."""
    lower = [c.lower() for c in columns]
    idx = []
    for i, fragment in enumerate(want):
        hit = next((j for j, c in enumerate(lower) if fragment in c), None)
        idx.append(hit if hit is not None else i)
    return [tuple(row[j] for j in idx) for row in rows]


def _key_pairs(items):
    return [(x["name"], x["cases"]) for x in items]


def compare(key_q, columns, rows, key):
    """Return (passed, actual, expected) for one question."""
    if key_q in ("q1", "q10"):
        exp = _key_pairs(key["q1_massachusetts_employers_top10" if key_q == "q1"
                              else "q10_certified_withdrawn_employers_top10"])
        act = _pairs(rows)
    elif key_q == "q2":
        exp = key["q2_boston_cases"]
        act = _i(rows[0][0]) if rows and len(rows[0]) == 1 else None
    elif key_q == "q3":
        exp = [(n.upper(), c) for n, c in _key_pairs(key["q3_cities_top10"])]
        act = _pairs(rows, upper=True)
    elif key_q == "q4":
        exp = {s: {"median_usd": v["median_usd"], "cases": v["cases"]}
               for s, v in key["q4_median_annual_base_wage_by_state"].items()}
        act = {}
        for state, median, cases in _named(columns, rows, ("state", "median", "case")):
            if median is not None:
                act[_s(state)] = {"median_usd": round(float(median), 2), "cases": _i(cases)}
    elif key_q == "q5":
        exp = key["q5_wage_levels"]
        act = {(_s(r[0]) or "[blank]"): _i(r[1]) for r in rows}
    elif key_q in ("q6", "q7"):
        source = key["q6_level_i_data_role_all_employers" if key_q == "q6" else "q7_capgemini_all_titles"]
        exp = {x["name"]: x["cases"] for x in source}
        act = {}
        for label, cases in _pairs(rows):
            act[label] = act.get(label, 0) + cases
    elif key_q == "q8":
        exp = _key_pairs(key["q8_soc_data_scientist_titles_top10"])
        act = _pairs(rows)[:10]
    elif key_q == "q9":
        exp = key["q9_certified_data_analyst_cases_by_decision_month"]
        act = {_s(r[0])[:7]: _i(r[1]) for r in rows}
    elif key_q in ("h1", "h5"):
        exp = key[f"{key_q}_count"]
        act = _i(rows[0][0]) if rows and len(rows[0]) == 1 else None
    elif key_q == "h2":
        exp = _key_pairs(key["h2_boston_employers_top10"])
        act = _pairs(rows)
    elif key_q == "h3":
        exp = key["h3_median_usd"]
        act = round(float(rows[0][0]), 2) if rows and rows[0][0] is not None else None
    elif key_q == "h4":
        exp = key["h4_wage_levels"]
        act = {(_s(r[0]) or "[blank]"): _i(r[1]) for r in rows}
    else:
        raise KeyError(f"no comparator for {key_q}")
    return act == exp, act, exp


def _recheck(results):
    """Re-run the text policy over every SQL string that was executed; should be 0."""
    from .policy import check_text
    bad = 0
    for r in results:
        for sql in (r.get("sql"), r.get("rows_sql")):
            if sql and not check_text(sql).allowed:
                bad += 1
    return bad


def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def run_set(question_set, responses, db_path, contract_path, state_dir, budget=None):
    """Run every question through the agent (no gate release) and score it."""
    from . import agent
    from .adapters import RecordedAdapter
    from .config import Budget

    qset = json.loads(Path(question_set).read_text(encoding="utf-8"))
    key_path = Path(question_set).parent / qset["answer_key"]
    if sha256_file(key_path) != qset["answer_key_sha256"]:
        raise ValueError(f"answer key {key_path} does not match its frozen SHA-256")
    key = json.loads(key_path.read_text(encoding="utf-8"))
    adapter = RecordedAdapter(responses)
    results, passes = [], 0
    for q in qset["questions"]:
        state = agent.run(q["question"], adapter, db_path, contract_path, qid=q["id"],
                          output_shape=q.get("output", ""), budget=budget or Budget(),
                          gate_mode="none", state_dir=state_dir)
        if state.result:
            try:
                passed, actual, expected = compare(q["key_q"], state.result["columns"],
                                                   state.result["rows"], key)
            except Exception as exc:  # wrong shape counts as a fail, with the reason
                passed, actual, expected = False, f"could not score: {exc}", None
        else:
            passed, actual, expected = False, None, None
        passes += passed
        results.append({
            "id": q["id"], "question": q["question"], "pass": passed,
            "stop_reason": state.stop_reason, "run_id": state.run_id,
            "interpretation": (state.result or {}).get("interpretation"),
            "sql": (state.result or {}).get("sql"),
            "rows_sql": (state.result or {}).get("rows_sql"),
            "check": (state.result or {}).get("check"),
            "policy_denials": state.used["denials"],
            "actual": actual, "expected": expected,
        })
    return {
        "set": qset["set"], "question_set_sha256": sha256_file(question_set),
        "answer_key_sha256": qset["answer_key_sha256"],
        "responses_file": Path(responses).name, "responses_sha256": sha256_file(responses),
        "contract": Path(contract_path).name, "contract_sha256": sha256_file(contract_path),
        "adapter": adapter.label, "passes": passes, "total": len(results),
        "policy_denials_total": sum(r["policy_denials"] for r in results),
        "executed_sql_failing_policy": _recheck(results),
        "results": results,
    }
