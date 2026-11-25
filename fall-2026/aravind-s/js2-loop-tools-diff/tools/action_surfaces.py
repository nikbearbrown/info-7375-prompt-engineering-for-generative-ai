"""The action-surface comparison (the brief's Step 4, part 3): the same task with more autonomy each time.

The task: judge the contract's worked example (posting 55150071-...) for Jane, and record which posting ids were
seen. Way 1, the posting pasted into one fresh chat with no tools, is the agent's own Claude judge; its evidence
is experiment/check/. This tool runs the other two in a new, empty throwaway folder and saves everything:

  python3 tools/action_surfaces.py file    Claude Code with one tool, Read, and the posting and the résumé as files
  python3 tools/action_surfaces.py agent   Claude Code with WebFetch (only api.ashbyhq.com) and Write, told to fetch
                                           the board itself and write its own state file

Both runs keep the rest of the judge's lockdown (no MCP servers, no settings, no memory, no saved session, no API
key, dontAsk). The record (experiment/surfaces/<way>.json) has every tool call, what each returned (cut at 2,000
characters), the reply, and every file left in the folder with its size and SHA-256.
"""

from __future__ import annotations

import hashlib
import json
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from job_agent import claude_judge as cj  # noqa: E402
from job_agent import resume as resume_mod  # noqa: E402

WORKED_EXAMPLE = "55150071-fce8-48f5-aea4-14ed78b83511"
BOARD = "https://api.ashbyhq.com/posting-api/job-board/openai"
FORMAT = ("Reply with one JSON object and nothing else, with exactly these keys: \"verdict\" (\"relevant\" or "
          "\"not_relevant\"), \"justification\" (one to three sentences), \"resume_fields\", \"posting_fields\" and "
          "\"quotes\" (as in the rules).")


def lockdown_without_tools() -> list:
    flags = list(cj.LOCKDOWN)
    at = flags.index("--tools")
    del flags[at: at + 2]
    return flags


def run(way: str) -> int:
    system = (REPO / "prompts" / "baseline.txt").read_text(encoding="utf-8")
    jane = resume_mod.load(REPO / "persona" / "jane-doe.json")
    jobs = json.loads((REPO / "runs" / "2026-10-30T093102Z" / "response.json").read_bytes())["jobs"]
    posting = next(j for j in jobs if j["id"] == WORKED_EXAMPLE)
    binary = cj.find_claude()
    started = datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    with tempfile.TemporaryDirectory(prefix=f"job-agent-surface-{way}-") as folder:
        if way == "file":
            Path(folder, "posting.json").write_text(json.dumps({f: posting.get(f) for f in cj.POSTING_FIELDS}, indent=1), encoding="utf-8")
            Path(folder, "resume.json").write_text(json.dumps(resume_mod.for_claude(jane), indent=1), encoding="utf-8")
            tools = ["--tools", "Read", "--allowedTools", "Read"]
            task = ("Read posting.json and resume.json in the current folder. Judge whether the posting is relevant for "
                    "the job seeker by the rules you were given. " + FORMAT)
        elif way == "agent":
            tools = ["--tools", "WebFetch,Write", "--allowedTools", "WebFetch(domain:api.ashbyhq.com)", "Write"]
            task = (f"Fetch the job board at {BOARD}. Find the posting with id {WORKED_EXAMPLE} and judge whether it is "
                    "relevant for the job seeker whose résumé is below, by the rules you were given. Then write a file "
                    "named state.json in the current folder holding a JSON list of every posting id you saw on the "
                    "board. " + FORMAT + "\nRésumé (contact fields removed):\n"
                    + json.dumps(resume_mod.for_claude(jane), indent=1))
        else:
            print(__doc__)
            return 2
        argv = [str(binary), *cj.OUTPUT, "--model", cj.DEFAULT_MODEL, "--system-prompt", system,
                *lockdown_without_tools(), *tools]
        raw = cj.run_cli(argv, task.encode("utf-8"), folder, cj.environment(binary), timeout=600)
        events = cj._for_the_record(raw["stdout"])
        left = []
        for path in sorted(Path(folder).iterdir()):
            body = path.read_bytes()
            item = {"name": path.name, "bytes": len(body), "sha256": hashlib.sha256(body).hexdigest()}
            if path.name == "state.json":
                try:
                    ids = json.loads(body.decode("utf-8"))
                    item["ids_listed"] = len(ids) if isinstance(ids, list) else None
                    item["ids_on_the_board"] = len(jobs)
                    item["ids_that_are_real"] = sum(1 for i in ids if i in {j["id"] for j in jobs}) if isinstance(ids, list) else None
                    item["content_head"] = body.decode("utf-8")[:1500]
                except ValueError:
                    item["content_head"] = body.decode("utf-8", "replace")[:1500]
            left.append(item)
    calls, results = [], []
    for event in events:
        content = (event.get("message") or {}).get("content") if isinstance(event.get("message"), dict) else None
        for block in content if isinstance(content, list) else []:
            if isinstance(block, dict) and block.get("type") == "tool_use":
                calls.append({"tool": block.get("name"), "input": block.get("input")})
            if isinstance(block, dict) and block.get("type") == "tool_result":
                text = block.get("content")
                text = json.dumps(text) if not isinstance(text, str) else text
                results.append({"is_error": block.get("is_error"), "content_head": text[:2000], "chars": len(text)})
    init = next((e for e in events if e.get("type") == "system" and e.get("subtype") == "init"), {})
    result = next((e for e in reversed(events) if e.get("type") == "result"), {})
    record = {
        "way": way, "started_at": started, "task": task if way == "file" else task.split("\nRésumé")[0] + " [résumé follows]",
        "command": [cj._tilde(a) if a != system else "<the system prompt in prompts/baseline.txt>" for a in argv],
        "claude_code": cj._init_summary(init), "tool_calls": calls, "tool_results": results,
        "permission_denials": result.get("permission_denials"), "num_turns": result.get("num_turns"),
        "reply": result.get("result"), "exit_code": raw["exit_code"], "seconds": raw["seconds"],
        "cost_usd_cli_estimate": result.get("total_cost_usd"), "files_left_in_the_folder": left, "events": events,
    }
    out = REPO / "experiment" / "surfaces"
    out.mkdir(parents=True, exist_ok=True)
    path = out / f"{way}.json"
    if path.exists():
        print(f"refused: {path.relative_to(REPO)} exists; saved runs are never replaced")
        return 3
    path.write_text(json.dumps(record, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({k: record[k] for k in ("way", "claude_code", "tool_calls", "permission_denials", "num_turns",
                                             "exit_code", "seconds", "cost_usd_cli_estimate", "files_left_in_the_folder")},
                     indent=1, ensure_ascii=False)[:6000])
    print("reply:", (record["reply"] or "")[:1500])
    return 0


if __name__ == "__main__":
    sys.exit(run(sys.argv[1] if len(sys.argv) > 1 else ""))
