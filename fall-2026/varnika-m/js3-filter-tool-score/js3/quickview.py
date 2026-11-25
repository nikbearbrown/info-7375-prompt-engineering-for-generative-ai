"""A short view of the blind labeling sheet: title, location, and the lines that state requirements.

    python3 -m js3.quickview        # writes audit/quick-view.md

Lines are picked by words that state a requirement (years, required, must, clearance, degree...),
not by the filter, and the filter's verdict is not shown. The full text is in labeling-sheet.md.
"""

import html
import json
import re
import sys

from js3.filter import text_of
from js3.load import FOLDER, load

ASKS = re.compile(r"(?i)(\d+\s*\+?\s*(?:-|–|to)?\s*\d*\s*years|year of|years of|require|must|clearance|degree|"
                  r"bachelor|master|phd|new grad|graduat|intern|senior|proficien|experience (?:with|in|building))")


def lines_of(posting):
    markup = html.unescape(posting.get("content") or "")
    parts = re.split(r"(?i)</li>|</p>|<br\s*/?>|</h[1-6]>|\n", markup)
    seen, out = set(), []
    for part in parts:
        line = text_of(part)
        if 15 < len(line) < 300 and ASKS.search(line) and line.lower() not in seen:
            seen.add(line.lower())
            out.append(line)
    return out[:6]


def main():
    postings, _ = load()
    by_key = {p["key"]: p for p in postings}
    items = json.loads((FOLDER / "audit" / "sample.json").read_text())["items"]
    out = ["# Quick view of the labeling sheet (blind)", "",
           "Up to 6 lines per posting that state a requirement. The full text is in `labeling-sheet.md`.", ""]
    for item in items:
        p = by_key[item["key"]]
        out.append("**%d. %s — %s** · %s" % (item["item"], p["company_name"], p["title"].strip(),
                                             (p.get("location") or {}).get("name")))
        out += ["- " + line for line in lines_of(p)] or ["- (no requirement lines found; see the full sheet)"]
        out.append("")
    (FOLDER / "audit" / "quick-view.md").write_text("\n".join(out), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
