# INFO 7375: Claude tool use and verification
# Companion: lessons/11-tool-use-and-verification/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
import argparse
import json
import math
import os
from pathlib import Path
import sys

TOOLS = [{"name":"add","description":"Add two finite numbers",
          "input_schema":{"type":"object","properties":{"a":{"type":"number"},"b":{"type":"number"}},
                          "required":["a","b"],"additionalProperties":False}}]

def dispatch(name, args):
    if name != "add" or not isinstance(args, dict) or set(args) != {"a","b"}:
        raise ValueError("Unknown tool or invalid arguments")
    if any(type(v) not in (int, float) or not math.isfinite(v) for v in args.values()):
        raise ValueError("Arguments must be finite numbers, not booleans")
    value = args["a"] + args["b"]
    if not math.isfinite(value):
        raise ValueError("Result overflow")
    return value

def results(content):
    output = []
    seen = set()
    for block in content:
        if block.get("type") != "tool_use":
            continue
        identity = block.get("id")
        if not isinstance(identity, str) or not identity or identity in seen:
            raise ValueError("Tool IDs must be nonempty and unique")
        seen.add(identity)
        try:
            value = dispatch(block.get("name"), block.get("input"))
            row = {"type":"tool_result","tool_use_id":identity,"content":json.dumps(value)}
        except ValueError as exc:
            row = {"type":"tool_result","tool_use_id":identity,"content":str(exc),"is_error":True}
        output.append(row)
    return output

def loop(call, body, max_turns=4):
    if type(max_turns) is not int or not 1 <= max_turns <= 4:
        raise ValueError("Course request budget must be 1..4")
    body = {**body, "messages":list(body["messages"]), "tools":TOOLS}
    trace = []
    for _ in range(max_turns):
        response = call(body)
        trace.append(response)
        if response.get("stop_reason") == "end_turn":
            return {"status":"finished","trace":trace}
        if response.get("stop_reason") != "tool_use":
            return {"status":"stopped","reason":response.get("stop_reason"),"trace":trace}
        content = response["content"]
        returned = results(content)
        if not returned:
            raise ValueError("tool_use stop without tool calls")
        body["messages"].extend([{"role":"assistant","content":content},
                                 {"role":"user","content":returned}])
    return {"status":"budget-exhausted","trace":trace}

def demo():
    return results([{"type":"tool_use","id":"demo-1","name":"add","input":{"a":2,"b":3}}])

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    if not args.live:
        print(json.dumps({"mode":"offline-fixture","results":demo()}, indent=2))
        return
    sys.path.insert(0, str(Path(__file__).resolve().parents[3]))
    from coursekit.claude import payload, send
    try:
        outcome = loop(lambda body: send(body, live=True),
                       payload("Use add to compute 17 plus 25, then report the result.",
                               os.environ.get("CLAUDE_MODEL", "")))
    except (ValueError, RuntimeError) as exc:
        parser.exit(1, f"{exc}\n")
    print(json.dumps({"mode":"live", **outcome}, indent=2))

if __name__ == "__main__":
    main()
