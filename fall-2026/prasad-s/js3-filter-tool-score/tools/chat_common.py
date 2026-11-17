"""Shared rules for the chat helpers prep_chat.py and save_reply.py.

Sets, the prompt file, and where replies go. See CONTRACT.md §1 (saved
replies item), §9 decision 4, experiments/chat_plan.md and
experiments/selected_ids.json. Paths are relative to a JS1 root so the
tests can use a temporary folder.
"""

import json
import os
import subprocess
from pathlib import Path

JS1 = Path(__file__).resolve().parents[1]

SETS = ("run2", "sampling", "dev", "heldout")
RUN2_REPORT = Path("evidence") / "run_report_run2_2026-10-28.json"
SELECTED_IDS = Path("experiments") / "selected_ids.json"
DEFAULT_PROMPT = Path("prompts") / "claude_prompt_baseline.txt"
PLACEHOLDER = "(paste the --for-claude block from the viewer here)"
SAMPLING_SIZE = 5  # the sampling set is the first 5 development ids
SAMPLING_REPEATS = range(1, 5)  # r1-r4
CONVERSATION = "fresh Incognito chat"
# Decision 2026-10-29: the prompt version's prefix names its experiment folder.
PROMPT_FOLDERS = {"baseline-": "baseline", "revision-": "revision"}
# Decision 2026-10-29: run 2 and the sampling report use the baseline prompt only (chat_plan.md).
BASELINE_ONLY_SETS = ("run2", "sampling")
UTF8_ENV = dict(os.environ, LANG="en_US.UTF-8", LC_ALL="en_US.UTF-8")


class ChatToolError(Exception):
    """A refusal: the tool stops and writes or copies nothing."""


def _read_json(path):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise ChatToolError(f"cannot read {path}: {exc}") from exc


def set_ids_and_source(root, set_name):
    """(ids in the set, board response file the set's postings come from)."""
    root = Path(root)
    if set_name == "run2":
        summary = _read_json(root / RUN2_REPORT)["summary"]
        return list(summary["new_ids"]), root / "evidence" / summary["source"]["file"]
    selected = _read_json(root / SELECTED_IDS)
    source = root / selected["source"]
    if set_name == "dev":
        return list(selected["development"]), source
    if set_name == "heldout":
        return list(selected["held_out"]), source
    if set_name == "sampling":
        return list(selected["development"][:SAMPLING_SIZE]), source
    raise ChatToolError(f"unknown set {set_name!r}; use one of {', '.join(SETS)}")


def require_member(root, set_name, posting_id):
    """Refuse unless posting_id belongs to the set. Returns the set's source file."""
    ids, source = set_ids_and_source(root, set_name)
    if posting_id not in ids:
        raise ChatToolError(f"posting_id {posting_id} is not in set {set_name}")
    return source


def read_prompt(path):
    """(prompt text, PROMPT_VERSION). The first line must be 'PROMPT_VERSION: <version>'."""
    try:
        text = Path(path).read_text(encoding="utf-8")
    except OSError as exc:
        raise ChatToolError(f"cannot read prompt {path}: {exc}") from exc
    first = text.split("\n", 1)[0].rstrip("\r")
    label = "PROMPT_VERSION: "
    if not first.startswith(label) or not first[len(label):].strip():
        raise ChatToolError(f"{path}: first line must be 'PROMPT_VERSION: <version>'")
    return text, first[len(label):].strip()


def prompt_folder(version):
    for prefix, folder in PROMPT_FOLDERS.items():
        if version.startswith(prefix):
            return folder
    raise ChatToolError(f"PROMPT_VERSION {version!r} starts with neither 'baseline-' nor 'revision-'")


def check_prompt_for_set(set_name, version):
    """Returns the experiment folder name for this prompt version."""
    folder = prompt_folder(version)
    if set_name in BASELINE_ONLY_SETS and folder != "baseline":
        raise ChatToolError(f"set {set_name} uses the baseline prompt only; got {version!r}")
    return folder


def run_clipboard(command, data=None):
    """pbcopy / pbpaste with a UTF-8 locale, so text survives unchanged."""
    try:
        result = subprocess.run([command], input=data, capture_output=True, env=UTF8_ENV, check=True)
    except (OSError, subprocess.CalledProcessError) as exc:
        raise ChatToolError(f"{command} failed: {exc}") from exc
    return result.stdout
