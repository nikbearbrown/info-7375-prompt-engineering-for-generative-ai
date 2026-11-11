"""Frozen config (CONTRACT.md, In): vocab, boilerplate, the Claude command and the prompt, each with a version."""
from __future__ import annotations

import json
import shlex
from dataclasses import dataclass
from pathlib import Path

CONTRACT_VERSION = "v2"
ALLOWED_HOSTS = ("boards-api.greenhouse.io",)
BOARD_SLUG = "stripe"           # v1 was "databricks"; CONTRACT.md, Contract v2
BOARD_URL = f"https://boards-api.greenhouse.io/v1/boards/{BOARD_SLUG}/jobs?content=true"
PROMPT_VERSION = "judge_v1"
RESUME_FIELDS = ("target_title_keywords", "skills", "years_experience", "preferred_cities", "remote_ok",
                 "highest_degree")
POSTING_FIELDS = ("title", "location", "content")
DISCLAIMER = ("rule_verdict is a deterministic record of CONTRACT.md's rule. claude_verdict is a model judgment, "
              "not fact. Neither is a hiring decision.")
ROOT = Path(__file__).resolve().parent.parent


class ConfigError(Exception):
    pass


@dataclass(frozen=True)
class Config:
    root: Path
    vocab: dict
    vocab_version: str
    cut_headings: tuple
    drop_phrases: tuple
    boilerplate_version: str
    claude_argv: tuple
    claude_model: str
    claude_cmd_version: str
    prompt_template: str
    prompt_version: str


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def parse_claude_cmd(text: str) -> dict:
    """`key: value` lines up to the first comment; argv is split like a POSIX shell, so --tools "" is one empty arg."""
    fields = {}
    for line in text.splitlines():
        if line.startswith("#"):
            break
        if ":" in line:
            k, v = line.split(":", 1)
            fields[k.strip()] = v.strip()
    for k in ("version", "model", "argv"):
        if not fields.get(k):
            raise ConfigError(f"config/claude_cmd.txt is missing `{k}:`")
    argv = shlex.split(fields["argv"], posix=True)
    if "--model" not in argv or argv[argv.index("--model") + 1] != fields["model"]:
        raise ConfigError("config/claude_cmd.txt: argv must pass --model equal to the `model:` line")
    return {"version": fields["version"], "model": fields["model"], "argv": tuple(argv)}


def load_prompt(root: Path, version: str) -> str:
    """prompts/<version>.md starts with `---\\nversion: <version>\\n---\\n`; the template is everything after."""
    text = (root / "prompts" / f"{version}.md").read_text(encoding="utf-8")
    head, sep, body = text.partition("\n---\n")
    if not text.startswith("---\n") or not sep or f"version: {version}" not in head:
        raise ConfigError(f"prompts/{version}.md must open with front matter naming version: {version}")
    return body


def load(root: Path = ROOT, prompt_version: str = PROMPT_VERSION) -> Config:
    vocab = _read_json(root / "config" / "skill_vocab.json")
    bp = _read_json(root / "config" / "boilerplate.json")
    cmd = parse_claude_cmd((root / "config" / "claude_cmd.txt").read_text(encoding="utf-8"))
    return Config(root=root, vocab=vocab["skills"], vocab_version=vocab["version"],
                  cut_headings=tuple(bp["cut_headings"]), drop_phrases=tuple(bp["drop_sentence_phrases"]),
                  boilerplate_version=bp["version"], claude_argv=cmd["argv"], claude_model=cmd["model"],
                  claude_cmd_version=cmd["version"], prompt_template=load_prompt(root, prompt_version),
                  prompt_version=prompt_version)
