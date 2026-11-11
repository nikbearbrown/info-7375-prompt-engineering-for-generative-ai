"""Run the same judging task three ways (ACTION-SURFACE.md) on one stored posting and save every raw output.
Written by Claude.

    python tools/action_surface.py 8333122

1 paste: prompt text on stdin, --tools ""            (the agent's own surface)
2 file : posting.json + persona.json in the cwd, --tools Read
3 agent: --tools WebFetch,Write, WebFetch allowed only for boards-api.greenhouse.io; told to fetch the board and write
         state.json itself
"""
from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent import claude_judge, config, persona as pm, textprep  # noqa: E402

EVID = ROOT / "evidence" / "action-surface"
MODEL = config.load(ROOT).claude_model


def call(args: list[str], prompt: str, cwd: Path) -> dict:
    exe = shutil.which("claude")
    started = datetime.now(timezone.utc).isoformat(timespec="seconds")
    p = subprocess.run([exe, "-p", "--output-format", "json", "--model", MODEL, "--no-session-persistence",
                        "--strict-mcp-config", "--setting-sources", "project", *args],
                       input=prompt.encode("utf-8"), capture_output=True, cwd=cwd, timeout=600)
    return {"started_at": started, "args": args, "stdout": p.stdout.decode("utf-8", "replace"),
            "cwd_after": sorted(x.name for x in cwd.iterdir())}


def main(pid: int) -> None:
    cfg = config.load(ROOT)
    persona = pm.load(ROOT / "data" / "persona_resume.json", cfg.vocab)
    sel = json.loads((ROOT / "experiments" / "output" / "label_selection.json").read_text(encoding="utf-8"))
    job = next(j for j in json.loads((ROOT / sel["board"]).read_bytes())["jobs"] if int(j["id"]) == pid)
    req = textprep.requirements_text(textprep.requirements_sentences(job["content"], cfg.cut_headings, cfg.drop_phrases))
    loc = (job.get("location") or {}).get("name", "")
    EVID.mkdir(parents=True, exist_ok=True)
    pasted = claude_judge.fill_prompt(cfg.prompt_template, persona, job["title"], loc, req)
    results = {}
    with tempfile.TemporaryDirectory(prefix="js1as-") as tmp:
        results["1-paste"] = call(["--tools", ""], pasted, Path(tmp))
    with tempfile.TemporaryDirectory(prefix="js1as-") as tmp:
        t = Path(tmp)
        (t / "posting.json").write_text(json.dumps({"id": pid, "title": job["title"], "location": loc,
                                                    "content": req}, ensure_ascii=False), encoding="utf-8")
        shown = {k: persona[k] for k in ("target_title_keywords", "skills", "years_experience", "highest_degree",
                                         "preferred_cities", "remote_ok")}
        (t / "persona.json").write_text(json.dumps(shown), encoding="utf-8")
        ask = ("Read posting.json and persona.json in the current directory. "
               + cfg.prompt_template.split("Reply with exactly one JSON object", 1)[1].join(
                   ["Then reply with exactly one JSON object", ""]))
        results["2-file"] = call(["--tools", "Read", "--allowedTools", "Read"], ask, t)
    with tempfile.TemporaryDirectory(prefix="js1as-") as tmp:
        ask = (f"Fetch https://boards-api.greenhouse.io/v1/boards/stripe/jobs and write a file state.json in the "
               f"current directory containing {{\"seen_ids\": [...every job id on the board...]}}. Then say whether job "
               f"{pid} is relevant to a candidate with skills {persona['skills']} and {persona['years_experience']} "
               f"years of experience, in one sentence.")
        results["3-agent"] = call(["--tools", "WebFetch,Write",
                                   "--allowedTools", "WebFetch(domain:boards-api.greenhouse.io)", "Write"], ask, Path(tmp))
        sp = Path(tmp) / "state.json"
        results["3-agent"]["state_json_head"] = sp.read_text(encoding="utf-8", errors="replace")[:600] if sp.exists() else None
    for name, r in results.items():
        (EVID / f"{name}.json").write_text(json.dumps(r, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [f"Ran {results['1-paste']['started_at']} UTC on posting {pid} ({job['title'].strip()}), model {MODEL}. "
             "Full raw outputs are in `evidence/action-surface/`.", ""]
    for name, r in results.items():
        try:
            env = json.loads(r["stdout"])
            res = str(env.get("result", ""))[:400].replace("\n", " ")
            extra = f" · permission denials: {len(env.get('permission_denials') or [])}" if env.get("permission_denials") is not None else ""
            lines.append(f"- **{name}** (is_error={env.get('is_error')}{extra}; files in cwd afterwards: {r['cwd_after']}): {res}")
        except ValueError:
            lines.append(f"- **{name}**: stdout was not JSON: {r['stdout'][:200]!r}")
    text = (ROOT / "ACTION-SURFACE.md").read_text(encoding="utf-8")
    start, end = "<!-- generated:start -->", "<!-- generated:end -->"
    head, rest = text.split(start, 1)
    (ROOT / "ACTION-SURFACE.md").write_text(head + start + "\n" + "\n".join(lines) + "\n" + end + rest.split(end, 1)[1],
                                            encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main(int(sys.argv[1]))
