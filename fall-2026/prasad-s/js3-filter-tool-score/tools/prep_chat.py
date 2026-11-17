"""Build one chat prompt for a posting and copy it to the clipboard.

Puts the posting's --for-claude block (from tools/show_posting.py) in place
of the prompt's placeholder line. Prints only the posting id, the set, the
prompt version and the character count: never the posting text or a verdict.
Writes no files.

Usage:
    python3.13 tools/prep_chat.py <posting_id> --set run2|sampling|dev|heldout [--prompt FILE]
"""

import argparse
import sys
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
if str(TOOLS) not in sys.path:
    sys.path.insert(0, str(TOOLS))

import chat_common as common  # noqa: E402
import show_posting  # noqa: E402
from agent.errors import RunError  # noqa: E402  (show_posting put JS1 on sys.path)


def build_prompt(prompt_text, block):
    """Replace the one placeholder line with the --for-claude block."""
    lines = prompt_text.splitlines(keepends=True)
    hits = [i for i, line in enumerate(lines) if line.rstrip("\r\n") == common.PLACEHOLDER]
    if len(hits) != 1:
        raise common.ChatToolError(f"the prompt must contain the line {common.PLACEHOLDER!r} exactly once "
                                   f"(found {len(hits)})")
    line = lines[hits[0]]
    ending = line[len(line.rstrip("\r\n")):]
    lines[hits[0]] = block + ending
    return "".join(lines)


def prepare(root, posting_id, set_name, prompt_path):
    """(full prompt text, prompt version). Raises ChatToolError on any refusal."""
    source = common.require_member(root, set_name, posting_id)
    prompt_text, version = common.read_prompt(prompt_path)
    common.check_prompt_for_set(set_name, version)
    try:
        posting = show_posting.find_posting(Path(source).read_bytes(), posting_id)
    except (OSError, RunError) as exc:
        raise common.ChatToolError(f"cannot read board response {source}: {exc}") from exc
    if posting is None:
        raise common.ChatToolError(f"posting_id {posting_id} is not in {source}")
    return build_prompt(prompt_text, show_posting.render_for_claude(posting)), version


def main(argv=None, root=common.JS1, copy=None):
    parser = argparse.ArgumentParser(prog="python3.13 tools/prep_chat.py",
                                     description="Copy one posting's chat prompt to the clipboard.")
    parser.add_argument("posting_id")
    parser.add_argument("--set", required=True, choices=common.SETS, dest="set_name")
    parser.add_argument("--prompt", metavar="FILE", help=f"prompt file (default: {common.DEFAULT_PROMPT})")
    args = parser.parse_args(argv)
    prompt_path = Path(args.prompt) if args.prompt else Path(root) / common.DEFAULT_PROMPT
    try:
        text, version = prepare(root, args.posting_id, args.set_name, prompt_path)
        if copy is None:
            common.run_clipboard("pbcopy", text.encode("utf-8"))
        else:
            copy(text)
    except common.ChatToolError as exc:
        print(f"REFUSED: {exc}", file=sys.stderr)
        return 1
    print(f"posting_id: {args.posting_id}")
    print(f"set: {args.set_name}")
    print(f"prompt_version: {version}")
    print(f"characters copied: {len(text)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
