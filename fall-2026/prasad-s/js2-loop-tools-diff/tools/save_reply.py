"""Save one Claude reply from the clipboard, byte-for-byte, with its metadata entry.

No trimming, no fence stripping, no repairs (CONTRACT.md §2, §6). Refuses to
overwrite an existing reply file or metadata entry.

Where replies go:
    run2      claude_outputs/<id>.txt
    sampling  experiments/sampling/<id>_r<N>.txt              (--repeat 1-4)
    dev       experiments/prompt_experiment/<baseline|revision>/<id>.txt
    heldout   experiments/prompt_experiment/<baseline|revision>/<id>.txt

Sampling replies are never reused as development baseline replies
(experiments/chat_plan.md): every development id gets its own dev chat.

Usage:
    python3.13 tools/save_reply.py <posting_id> --set SET --model "MODEL"
        [--repeat N] [--prompt FILE] [--from-file PATH]
"""

import argparse
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import chat_common as common  # noqa: E402

PROMPT_COPIED = "PROMPT_VERSION:"
SPLITS = {"dev": "development", "heldout": "held_out"}


def collected_now():
    """One string with both times: the agent requires 'collected' to be a string."""
    local = datetime.now().astimezone()
    utc = local.astimezone(timezone.utc)
    return f"{local.isoformat(timespec='seconds')} (UTC {utc.strftime('%Y-%m-%dT%H:%M:%SZ')})"


def check_reply(data):
    """Refusals on the reply bytes. The bytes themselves are never changed."""
    if not data.strip():
        raise common.ChatToolError("the clipboard is empty")
    if data.decode("utf-8", errors="replace").lstrip().startswith(PROMPT_COPIED):
        raise common.ChatToolError("the clipboard holds the prompt (starts with PROMPT_VERSION:), not Claude's reply")


def plan_targets(root, posting_id, set_name, version, folder, repeat, model):
    """Every (reply path, metadata path, metadata key, entry) this save writes."""
    root = Path(root)
    base = {"collected": collected_now(), "model": model, "prompt_version": version,
            "conversation": common.CONVERSATION}
    if set_name == "run2":
        folder_path = root / "claude_outputs"
        return [(folder_path / f"{posting_id}.txt", folder_path / "metadata.json", posting_id,
                 {"file": f"{posting_id}.txt", **base, "set": "run2"})]
    if set_name == "sampling":
        stem = f"{posting_id}_r{repeat}"
        folder_path = root / "experiments" / "sampling"
        return [(folder_path / f"{stem}.txt", folder_path / "metadata.json", stem,
                 {"file": f"{stem}.txt", "posting_id": posting_id, **base, "set": "sampling", "repeat": repeat})]
    folder_path = root / "experiments" / "prompt_experiment" / folder
    return [(folder_path / f"{posting_id}.txt", folder_path / "metadata.json", posting_id,
             {"file": f"{posting_id}.txt", **base, "set": set_name, "split": SPLITS[set_name]})]


def _load_metadata(path):
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise common.ChatToolError(f"cannot read {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise common.ChatToolError(f"{path} is not a JSON object")
    return data


def save(root, posting_id, set_name, model, repeat, prompt_path, data):
    """Check everything first, then write. Returns the saved reply paths."""
    common.require_member(root, set_name, posting_id)
    if not model.strip():
        raise common.ChatToolError("--model must not be empty")
    if set_name == "sampling":
        if repeat not in common.SAMPLING_REPEATS:
            raise common.ChatToolError("--set sampling needs --repeat 1, 2, 3 or 4")
    elif repeat is not None:
        raise common.ChatToolError(f"--repeat is only for --set sampling, not {set_name}")
    _, version = common.read_prompt(prompt_path)
    folder = common.check_prompt_for_set(set_name, version)
    check_reply(data)

    targets = plan_targets(root, posting_id, set_name, version, folder, repeat, model)
    metadata = {}
    for reply_path, meta_path, key, _ in targets:
        if reply_path.exists():
            raise common.ChatToolError(f"{reply_path} already exists; not overwriting")
        metadata.setdefault(meta_path, _load_metadata(meta_path))
        if key in metadata[meta_path]:
            raise common.ChatToolError(f"{meta_path} already has an entry for {key}; not overwriting")

    for reply_path, meta_path, key, entry in targets:
        reply_path.parent.mkdir(parents=True, exist_ok=True)
        with open(reply_path, "xb") as fh:
            fh.write(data)
        metadata[meta_path][key] = entry
    for meta_path, entries in metadata.items():
        tmp = meta_path.with_name(meta_path.name + ".tmp")
        tmp.write_text(json.dumps(entries, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        os.replace(tmp, meta_path)
    return [reply_path for reply_path, _, _, _ in targets]


def main(argv=None, root=common.JS1):
    parser = argparse.ArgumentParser(prog="python3.13 tools/save_reply.py",
                                     description="Save Claude's reply from the clipboard, unchanged.")
    parser.add_argument("posting_id")
    parser.add_argument("--set", required=True, choices=common.SETS, dest="set_name")
    parser.add_argument("--model", required=True, help='model shown in the chat, e.g. "Opus 5.5"')
    parser.add_argument("--repeat", type=int, help="sampling only: 1-4")
    parser.add_argument("--prompt", metavar="FILE", help=f"prompt file (default: {common.DEFAULT_PROMPT})")
    parser.add_argument("--from-file", metavar="PATH", help="read the reply from a file instead of the clipboard (tests only)")
    args = parser.parse_args(argv)
    prompt_path = Path(args.prompt) if args.prompt else Path(root) / common.DEFAULT_PROMPT
    try:
        if args.from_file:
            try:
                data = Path(args.from_file).read_bytes()
            except OSError as exc:
                raise common.ChatToolError(f"cannot read {args.from_file}: {exc}") from exc
        else:
            data = common.run_clipboard("pbpaste")
        saved = save(root, args.posting_id, args.set_name, args.model, args.repeat, prompt_path, data)
    except common.ChatToolError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    for path in saved:
        print(f"saved: {path}")
    print(f"bytes: {len(data)}")
    first_line = data.decode("utf-8", errors="replace").split("\n", 1)[0]
    print(f"first line: {first_line!r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
