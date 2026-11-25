"""The chat view of a blind card file: every fact line word for word, and each description's first 32 words.

Aravind judges cards in chat. This makes that view mechanically from CARDS.md, so nothing on it is written by someone
who knows the answers, and the view can be checked against the cards (tests/test_fresh_kit.py). The cut of 32 words
was hand-set by Claude Code to keep 20 to 55 cards readable in one message; the cards themselves keep 150 words.

Usage: python3 tools/chat_cards.py <kit>/CARDS.md [--out <kit>/CHAT-CARDS.md]
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

CHAT_WORDS = 32
BOARDS = {"ashby-openai": "OpenAI", "greenhouse-verkada": "Verkada", "lever-palantir": "Palantir"}
SECTIONS = (("Years", "Sentences with a number of years"), ("Start", "Start sentences"),
            ("Status", "Sentences about status, sponsorship or clearance"),
            ("Topics", "Sentences with a topic word and an action word"))


def render(cards: str) -> str:
    blocks = re.split(r"^## Card (\d\d)\n", cards, flags=re.M)[1:]
    out = ["# The chat view of CARDS.md", "",
           f"Made by `tools/chat_cards.py` from CARDS.md: every fact line word for word, and the first {CHAT_WORDS} "
           "words of each description. Nothing here is written by hand.", ""]
    for number, body in zip(blocks[::2], blocks[1::2]):
        def field(pattern):
            return re.search(pattern, body, re.M).group(1)
        board, title = field(r"^- Board: (\S+)"), field(r"^\*\*(.+?)\*\*$")  # no backslash inside an f-string: 3.9
        places, kind = field(r"^- Locations: (.*)$"), field(r"^- Employment type: (.*)$")
        posted = field(r"^- Posted: (.*)$")[:10]
        out.append(f"**{number}. {title}** ({BOARDS.get(board, board)}; {places}; {kind}; posted {posted})")
        for label, name in SECTIONS:
            m = re.search(r"^\*\*" + re.escape(name) + r":\*\*\n\n((?:- .*\n)+)", body, re.M)
            out += [f"- {label}: {line[2:]}" for line in (m.group(1).splitlines() if m else []) if line != "- none"]
        words = field(r"^> (.*)$").split()
        out += [f"- First {CHAT_WORDS} words: " + " ".join(words[:CHAT_WORDS]) +
                (" ..." if len(words) > CHAT_WORDS else ""), ""]
    return "\n".join(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("cards", type=Path)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args(argv)
    text = render(args.cards.read_text(encoding="utf-8"))
    if args.out:
        args.out.write_text(text, encoding="utf-8")
        print(f"wrote {args.out}")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
