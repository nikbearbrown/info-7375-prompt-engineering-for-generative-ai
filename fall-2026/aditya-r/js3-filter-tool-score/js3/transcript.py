"""Publish a local wire log as a sanitized transcript, and run the scripted test-client exchanges.

  .venv/bin/python -m js3.transcript publish <local wire.jsonl> <name> --client "<who>" --date <YYYY-MM-DD>
  .venv/bin/python -m js3.transcript selftest      (our server, js3 test client; NOT Claude)

`publish` refuses to write a transcript containing a home path, a username, or an email address.
Lines are copied verbatim (nothing is rewritten), so a refusal means a person must decide what to redact.
"""
import getpass
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "transcripts"
FORBIDDEN = [re.compile(r"/Users/[^/\"\s]+"), re.compile(r"/home/[^/\"\s]+"),
             re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[a-z]{2,}"), re.compile(re.escape(getpass.getuser()), re.I)]


def check(lines):
    hits = []
    for i, rec in enumerate(lines):
        for rx in FORBIDDEN:
            m = rx.search(rec["line"])
            if m and not m.group(0).endswith("@example.com"):
                hits.append((i, m.group(0)))
    return hits


def render_md(lines, header):
    out = [header, "", "| # | time (UTC) | direction | message |", "|---|---|---|---|"]
    for i, r in enumerate(lines, 1):
        msg = r["line"]
        try:
            m = json.loads(msg)
            label = m.get("method") or ("error " + str(m["error"]["code"]) if "error" in m else "result")
            if "result" in m and isinstance(m["result"], dict) and "isError" in m["result"]:
                label += f" (isError={m['result']['isError']})"
            label = f"id={m.get('id')} {label}"
        except Exception:
            label = "unparseable"
        out.append(f"| {i} | {r['t']} | {r['dir']} | `{label}` |")
    out += ["", "Full lines, verbatim: the `.jsonl` file with the same name."]
    return "\n".join(out) + "\n"


def publish(src, name, client, date, redact=None):
    """redact: {exact string: label}. Each replacement is counted and declared in the .md header."""
    lines = [json.loads(l) for l in Path(src).read_text(encoding="utf-8").splitlines() if l.strip()]
    counts = {}
    for old, label in (redact or {}).items():
        variants = {old, json.dumps(old)[1:-1]}  # raw and JSON-escaped spellings
        for r in lines:
            for v in variants:
                if v in r["line"]:
                    counts[label] = counts.get(label, 0) + r["line"].count(v)
                    r["line"] = r["line"].replace(v, label)
    hits = check(lines)
    if hits:
        raise SystemExit(f"REFUSED: private-looking strings in {len(hits)} line(s): {hits[:3]}")
    OUT.mkdir(exist_ok=True)
    (OUT / f"{name}.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in lines), encoding="utf-8")
    (OUT / f"{name}.md").write_text(render_md(lines, f"# Transcript `{name}`\n\n- client: **{client}**\n- date: {date}\n"
                                              f"- lines: {len(lines)} (both directions, as logged by the server or client)\n"
                                              f"- sanitization: " + ("; ".join(f"replaced the local sandbox path with `{k}` ({n} occurrences)" for k, n in counts.items()) + "; otherwise " if counts else "") + "no line was altered; forbidden-pattern check found 0 matches after that"),
                                    encoding="utf-8")
    print(f"published transcripts/{name}.jsonl ({len(lines)} lines)")


def selftest():
    import datetime as dt
    from .mcp_client import StdioClient
    log = OUT / "selftest_js3_test_client.raw.jsonl"
    OUT.mkdir(exist_ok=True)
    log.unlink(missing_ok=True)
    c = StdioClient([sys.executable, str(ROOT / "js3" / "mcp_server.py")], log_path=log, cwd="/")
    c.initialize("2025-11-25")
    c.request("tools/list")
    c.request("tools/call", {"name": "score_posting", "arguments": {"posting_id": "greenhouse:databricks:8091041002"}})
    c.request("tools/call", {"name": "score_posting", "arguments": {"posting_id": "greenhouse:databricks:0000000000"}})
    c.request("tools/call", {"name": "score_posting", "arguments": {"posting_id": 8091041002}})
    c.request("tools/call", {"name": "write_file", "arguments": {"path": "x"}})
    c.request("resources/list")
    c.send_raw("{not json")
    c.close()
    publish(log, "selftest_js3_test_client", "js3 test client (js3/mcp_client.py), NOT Claude",
            dt.date.today().isoformat())
    log.unlink()


if __name__ == "__main__":
    if sys.argv[1] == "publish":
        import argparse
        ap = argparse.ArgumentParser()
        ap.add_argument("cmd"); ap.add_argument("src"); ap.add_argument("name")
        ap.add_argument("--client", required=True); ap.add_argument("--date", required=True)
        a = ap.parse_args()
        publish(a.src, a.name, a.client, a.date)
    elif sys.argv[1] == "selftest":
        selftest()
