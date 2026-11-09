"""The independent check for a finished wrong answer. It never reads the loop's report.

    python3 check_identity.py [--config config/boards.json]

For each Greenhouse board, it asks Greenhouse for the board's own name
(/v1/boards/{token}) and compares that with the employer the config names. Ashby and
Lever have no public name endpoint, so their boards are reported as "not checkable",
not as passing. It goes through the same policy and writes only a new folder in runs/.
Exit code 0 if every checkable board matches, 1 if any does not.
"""
import argparse
import datetime as dt
import json
import re
import sys

from policy import Policy, PolicyViolation
from tools import Tools, TransientError

NAME_URL = "https://boards-api.greenhouse.io/v1/boards/{token}"


def same_name(a, b):
    def squash(s):
        return " ".join(re.sub(r"[^a-z0-9]+", " ", (s or "").lower()).split())
    return squash(a) == squash(b)


def check(tools, config_path, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    out = f"runs/{now.strftime('%Y-%m-%dT%H%M%SZ')}_identity-check"
    tools.make_run_dir(out)
    boards = json.loads(tools.read_text(config_path))["boards"]
    rows = []
    for board in boards:
        key = f"{board['system']}/{board['token']}"
        if board["system"] != "greenhouse":
            rows.append({"board": key, "expected": board["employer"], "actual": None, "result": "not checkable"})
            continue
        url = NAME_URL.format(token=board["token"])
        try:
            response = tools.http_get(url, timeout=15)
        except TransientError as e:
            rows.append({"board": key, "expected": board["employer"], "actual": None, "result": f"no answer: {e}"})
            continue
        tools.write_bytes(f"{out}/raw/greenhouse_{board['token']}_board.{'json' if response.status == 200 else 'txt'}",
                          response.body)
        actual = json.loads(response.body).get("name") if response.status == 200 else None
        result = ("match" if same_name(actual, board["employer"]) else "MISMATCH") if response.status == 200 \
            else f"HTTP {response.status}"
        rows.append({"board": key, "expected": board["employer"], "actual": actual, "result": result})
    ok = all(r["result"] in ("match", "not checkable") for r in rows)
    lines = [f"# Identity check {out.split('/')[-1]}", "", f"Config: `{config_path}`. This check does not read any run report.",
             "", "| Board | Employer in config | Board's own name | Result |", "|---|---|---|---|"]
    lines += [f"| {r['board']} | {r['expected']} | {r['actual'] or 'none'} | {r['result']} |" for r in rows]
    tools.write_text(f"{out}/result.json", json.dumps({"config": config_path, "ok": ok, "rows": rows}, indent=2) + "\n")
    tools.write_text(f"{out}/report.md", "\n".join(lines) + "\n")
    return out, ok, rows


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--config", default="config/boards.json")
    args = parser.parse_args(argv)
    try:
        out, ok, rows = check(Tools(Policy()), args.config)
    except PolicyViolation as e:
        print(f"error: {e}", file=sys.stderr)
        return 3
    for r in rows:
        print(f"  {r['board']}: {r['result']} (config: {r['expected']!r}, board: {r['actual']!r})")
    print(f"{'ok' if ok else 'MISMATCH'} -> {out}/report.md")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
