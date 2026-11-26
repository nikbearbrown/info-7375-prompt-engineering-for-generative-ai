"""Persistence is not training: a behaviour that changes across sessions can live entirely in a file.

    python -B experiments/persistence.py
Six fresh sessions, same model, same prompt (prompts/judge_v1.md), same posting (a Snowflake
Solution Engineer posting that is NOT in the 80-posting label sample):
  A1, A2  plain
  B1, B2  plus experiments/persistence_note.md appended to the message, the way a memory file
          (CLAUDE.md, a notes file) is loaded into a new session
  C1, C2  plain again, the file no longer loaded
No session can see another (--no-session-persistence); nothing is fine-tuned or trained here.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from agent3 import corpus, judge, policy  # noqa: E402
from agent3.resume import load_resume  # noqa: E402


def main() -> int:
    sample = json.loads((policy.OUT / "audit" / "sample_v1.0.json").read_text(encoding="utf-8"))
    inside = {i for v in sample["sets"].values() for i in v}
    c = corpus.load()["postings"]
    pid = next(i for i in sorted(c) if i not in inside and c[i]["title"] == "Senior Solution Engineer"
               and c[i]["last_seen_run"] == "20261125T023341Z")
    resume = load_resume(policy.check_read(ROOT / "data" / "resume_jack_spencer.json"))
    template = (ROOT / "prompts" / "judge_v1.md").read_text(encoding="utf-8")
    note = (ROOT / "experiments" / "persistence_note.md").read_text(encoding="utf-8").strip()
    runs = {}
    for session, ctx in (("A1", ""), ("A2", ""), ("B1", note), ("B2", note), ("C1", ""), ("C2", "")):
        r = judge.judge(c[pid], resume, template, extra_context=("NOTES FILE LOADED INTO THIS SESSION:\n" + note) if ctx else "")
        runs[session] = {"note_loaded": bool(ctx), "verdict": r["verdict"], "valid": r["valid"],
                         "reason": (r.get("parsed") or {}).get("reason"), "session_id": r.get("session_id"),
                         "models_reported": r.get("models_reported"), "asked_at_utc": r.get("asked_at_utc")}
        print(session, "note" if ctx else "plain", r["verdict"], "|", (runs[session]["reason"] or r.get("rejection"))[:160])
    policy.write_bytes(policy.OUT / "experiments" / "persistence.json",
                       (json.dumps({"posting_id": pid, "title": c[pid]["title"], "note_file": "experiments/persistence_note.md",
                                    "runs": runs}, indent=1, ensure_ascii=False) + "\n").encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
