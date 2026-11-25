"""Both judges for one new posting (CONTRACT.md, Out): the rule's record and Claude's judgment, kept apart."""

from __future__ import annotations

import hashlib
from pathlib import Path

from . import claude_judge, rule
from .errors import BrokenInput

PROMPTS = Path(__file__).resolve().parent.parent / "prompts"


class Judges:
    def __init__(self, prompt: Path = PROMPTS / "baseline.txt", model: str = claude_judge.DEFAULT_MODEL,
                 runner=claude_judge.run_cli, binary=None):
        self.prompt, self.model, self.runner, self.binary = Path(prompt), model, runner, binary
        if not self.prompt.is_file():  # checked before anything is fetched
            raise BrokenInput(f"the prompt file {self.prompt.name} does not exist")

    def rule_verdict(self, job: dict, resume: dict) -> dict:
        return rule.judge(job, resume)

    def claude_verdict(self, job: dict, resume: dict, record_dir: Path) -> dict:
        return claude_judge.judge(job, resume, prompt_path=self.prompt, record_dir=Path(record_dir), model=self.model,
                                  runner=self.runner, binary=self.binary)

    def describe(self) -> dict:
        """The prompt file and its SHA-256, and the model: what makes two Claude calls the same call."""
        text = self.prompt.read_bytes()
        return {"file": self.prompt.name, "sha256": hashlib.sha256(text).hexdigest(), "model": self.model}

    def __call__(self, job: dict, resume: dict, run_dir: Path) -> dict:
        return {
            "rule": rule.judge(job, resume),
            "claude": claude_judge.judge(job, resume, prompt_path=self.prompt, record_dir=Path(run_dir) / "claude",
                                         model=self.model, runner=self.runner, binary=self.binary),
        }
