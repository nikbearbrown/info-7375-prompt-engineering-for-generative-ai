"""Write the labeling set's full descriptions to one readable Markdown file. Shows no verdicts.

Usage: .venv/bin/python -m experiment.print_postings
"""
from jsagent.text import strip_html

from .common import EXP, load_labels, load_postings

OUT = EXP / "postings_to_label.md"


def main():
    postings = load_postings()
    rows = load_labels(require_complete=False)
    parts = ["# Postings to hand-label (source: pre-implementation Klaviyo snapshot)\n"]
    for pid in rows:
        p = postings[pid]
        body = "\n".join(line.strip() for line in strip_html(p["content"]).splitlines() if line.strip())
        parts.append(f"\n---\n\n## {pid} — {p['title'].strip()}\n\n"
                     f"**Location:** {p['location']['name']}  \n**URL:** {p.get('absolute_url')}\n\n{body}\n")
    OUT.write_text("".join(parts))
    print(f"wrote {OUT} ({len(rows)} postings)")


if __name__ == "__main__":
    main()
