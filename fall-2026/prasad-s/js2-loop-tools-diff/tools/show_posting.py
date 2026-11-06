"""Read-only posting viewer for hand-labeling (experiments/labeling_protocol.md).

Shows one posting's title and location.name as they are in the file, and its
content after CONTRACT.md §4 cleanup steps 1-4. It shows nothing else: the
labeling protocol requires a viewer with no verdicts or hints. Writes no files.

Usage:
    python3.13 tools/show_posting.py <posting_id> [--source FILE] [--for-claude]
"""

import argparse
import json
import sys
from pathlib import Path

JS1 = Path(__file__).resolve().parents[1]
if str(JS1) not in sys.path:
    sys.path.insert(0, str(JS1))

from agent.errors import RunError  # noqa: E402
from agent.rule import clean_content  # noqa: E402
from agent.state import parse_board_response  # noqa: E402

SELECTED_IDS = JS1 / "experiments" / "selected_ids.json"
NOT_STATED = "not stated"
NO_CONTENT = "(no content field)"


def default_source():
    """The "source" file named in experiments/selected_ids.json, relative to JS1."""
    data = json.loads(SELECTED_IDS.read_text(encoding="utf-8"))
    return JS1 / data["source"]


def find_posting(raw, posting_id):
    """§4 step 1 (JSON parse, via the agent's parser), then the first posting with this id."""
    for posting in parse_board_response(raw):
        if posting["posting_id"] == posting_id:
            return posting
    return None


def fields(posting):
    """(title raw, location.name raw, content cleaned by §4 steps 2-4)."""
    title = posting.get("title")
    location = posting.get("location")
    name = location.get("name") if isinstance(location, dict) else None
    content = posting.get("content")
    return (
        title if isinstance(title, str) else NOT_STATED,
        name if isinstance(name, str) else NOT_STATED,
        clean_content(content) if isinstance(content, str) else NO_CONTENT,
    )


def render(posting):
    title, location, content = fields(posting)
    return "\n".join([
        f"posting_id: {posting['posting_id']}",
        f"title: {title}",
        f"location.name: {location}",
        f"content: {content}",
    ])


def render_for_claude(posting):
    title, location, content = fields(posting)
    return "\n".join([f"TITLE: {title}", f"LOCATION: {location}", f"CONTENT: {content}"])


def main(argv=None):
    parser = argparse.ArgumentParser(prog="python3.13 tools/show_posting.py",
                                     description="Show one posting for hand-labeling. Shows no verdicts or hints.")
    parser.add_argument("posting_id")
    parser.add_argument("--source", metavar="FILE",
                        help="saved board response (default: the source in experiments/selected_ids.json)")
    parser.add_argument("--for-claude", action="store_true",
                        help="print only the TITLE/LOCATION/CONTENT block to paste into a chat")
    args = parser.parse_args(argv)

    try:
        source = Path(args.source) if args.source else default_source()
    except (OSError, ValueError, KeyError) as exc:
        print(f"error: cannot read the source from {SELECTED_IDS}: {exc}", file=sys.stderr)
        return 2
    try:
        posting = find_posting(source.read_bytes(), args.posting_id)
    except (OSError, RunError) as exc:
        print(f"error: cannot read board response {source}: {exc}", file=sys.stderr)
        return 2
    if posting is None:
        print(f"error: posting_id {args.posting_id} is not in {source}", file=sys.stderr)
        return 1
    print(render_for_claude(posting) if args.for_claude else render(posting))
    return 0


if __name__ == "__main__":
    sys.exit(main())
