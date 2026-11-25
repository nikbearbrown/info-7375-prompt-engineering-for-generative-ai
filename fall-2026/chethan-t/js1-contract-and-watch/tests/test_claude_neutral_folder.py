import json
import os
import subprocess
from pathlib import Path

from agent import claude_judge
from test_claude_wiring import VALID, fake_claude, isolated  # noqa: F401  (autouse fixture)

PROJECT = Path(__file__).resolve().parent.parent
REPO = next(p for p in [PROJECT, *PROJECT.parents] if (p / ".git").exists())


def test_23_claude_runs_from_fresh_empty_folder_outside_repo(monkeypatch, postings, resume):
    seen = {}

    def run(args, **kwargs):
        cwd = kwargs.get("cwd")
        seen["cwd"] = cwd
        seen["contents"] = os.listdir(cwd) if cwd else None
        envelope = {"type": "result", "is_error": False, "result": json.dumps(VALID)}
        return subprocess.CompletedProcess(args, 0, stdout=json.dumps(envelope), stderr="")

    monkeypatch.setattr(subprocess, "run", run)
    judgment = claude_judge.judge(postings["swe_boston_plain"], resume)

    assert judgment["status"] == "ok"
    assert seen["cwd"] is not None, "claude -p must get an explicit working folder"
    cwd = Path(seen["cwd"]).resolve()
    assert not cwd.is_relative_to(REPO.resolve())
    assert seen["contents"] == []      # empty when Claude starts
    assert not cwd.exists()            # temporary: removed afterwards


def test_24_reply_wrapped_in_json_fence_is_rejected(monkeypatch, postings, resume):
    # Strict contract: a ```json fence is extra text around the JSON.
    fake_claude(monkeypatch, "```json\n" + json.dumps(VALID) + "\n```")
    judgment = claude_judge.judge(postings["swe_boston_plain"], resume)
    assert judgment["status"] == "no Claude verdict"
