# usage: tamper.py <summary.json> <case>   (edits a COPY of a run's summary.json)
import json, sys
p, case = sys.argv[1], sys.argv[2]
s = json.load(open(p))
b = next(x for x in s["boards"] if x["key"] == "greenhouse:stripe-js2-nonexistent")
if case == "reason_http_500": b["reason"] = "http_500"
if case == "count_zero": b["count"] = 0
if case == "reason_budget": b["reason"] = "budget"
if case == "reason_repeat": b["reason"] = "repeat"
if case == "unvisited_and_finished":
    b["status"] = "UNVISITED"; s["exit"] = "FINISHED"; s["exit_code"] = 0
json.dump(s, open(p, "w"), indent=2)
