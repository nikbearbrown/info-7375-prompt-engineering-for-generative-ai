"""Reproduce the JS1 validator's path defect against the UNCHANGED JS1 code.

Run from this JS2 folder:  python3 -B review/reproduce.py
Reads ../js1-contract-and-watch only; writes nothing.
"""
import json
import pathlib
import sys

HERE = pathlib.Path(__file__).resolve().parent
JS1 = HERE.parent.parent / "js1-contract-and-watch"
sys.path.insert(0, str(JS1))

from agent.claude_judge import path_exists, validate  # noqa: E402

resume = json.loads((JS1 / "persona/priya-nair.resume.json").read_text())
saved = json.loads((JS1 / "evidence/claude/experiment/revision-dev/"
                    "6865698002.json").read_text())
reply = saved["raw_reply"]

print("Real Claude reply, asked_at", saved["asked_at"], "model",
      saved["models_used"])
print("resume_fields in that reply:", json.loads(reply)["resume_fields"])
print()

parsed, errors = validate(reply, 6865698002, resume)
print("1. validate(real reply)             ->",
      "VALID" if parsed else f"INVALID {errors}")

bracket = reply.replace("education.0.", "education[0].")
parsed, errors = validate(bracket, 6865698002, resume)
print("2. same reply, education[0].        ->",
      "VALID" if parsed else f"INVALID {errors}")

print()
print("path_exists on single paths (Priya has 1 education entry):")
for p in ["education.end_date", "education[0].end_date",
          "education.0.end_date", "education[5].end_date",
          "education.5.end_date", "education[0]", "education[x].end_date"]:
    print(f"   {p:26} -> {path_exists(resume, p)}")
