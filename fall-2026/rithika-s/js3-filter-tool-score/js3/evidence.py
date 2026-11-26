"""Check Claude's justification quotes against the posting's own text.

Each quote gets one check result:
    quote_found       the quote occurs verbatim in the title, the location
                      or the body (matched within one field; case-folded and
                      with every run of whitespace treated as one space)
    quote_not_found   it does not (an empty quote counts as not found)
    not_stated        the quote is exactly "NOT STATED"

and one verdict (the abstain rule):
    found                     -> "candidate"   (never "supported": a found
                                                quote has not yet been
                                                judged to support the claim)
    not_found or not_stated   -> "I cannot tell"

Claude's output must be JSON only, {"claims": [{"claim", "quote"}, ...]},
with 3-5 claims. Anything else is a parse error. It is reported and kept,
never repaired.

    python3 -m js3.evidence --shortlist out/shortlist   (prints a table)
"""

import argparse
import json
import sys
from pathlib import Path

from js3 import corpus as js3_corpus

ROOT = Path(__file__).resolve().parent.parent
NOT_STATED = "NOT STATED"
FOUND = "quote_found"
NOT_FOUND = "quote_not_found"
STATED_NOT = "not_stated"
CANDIDATE = "candidate"
CANNOT_TELL = "I cannot tell"
FIELDS = ("title", "location", "body_text")
MIN_CLAIMS, MAX_CLAIMS = 3, 5


class ParseError(Exception):
    """Claude's output is not exactly the required JSON shape."""


def normalize(text):
    """Case-fold and collapse whitespace; also return, for each character
    of the result, its index in the original text."""
    out, index = [], []
    in_space = False
    for i, ch in enumerate(text):
        if ch.isspace():
            if not in_space and out:
                out.append(" ")
                index.append(i)
            in_space = True
            continue
        in_space = False
        for c in ch.casefold():
            out.append(c)
            index.append(i)
    if out and out[-1] == " ":
        out.pop()
        index.pop()
    return "".join(out), index


def find_quote(quote, posting):
    """Return {"field", "start", "end"} (offsets in the original field
    text) for the first field containing the quote, or None."""
    needle, _ = normalize(quote)
    if not needle:
        return None
    for field in FIELDS:
        text = posting.get(field) or ""
        hay, index = normalize(text)
        pos = hay.find(needle)
        if pos >= 0:
            return {"field": field, "start": index[pos],
                    "end": index[pos + len(needle) - 1] + 1}
    return None


def check_quote(quote, posting):
    if quote == NOT_STATED:
        return {"check": STATED_NOT, "verdict": CANNOT_TELL, "where": None}
    where = find_quote(quote, posting)
    if where is None:
        return {"check": NOT_FOUND, "verdict": CANNOT_TELL, "where": None}
    return {"check": FOUND, "verdict": CANDIDATE, "where": where}


def parse_claims(raw):
    """Parse Claude's stdout strictly; return the list of claims."""
    if not isinstance(raw, str) or not raw.strip():
        raise ParseError("empty output")
    try:
        data = json.loads(raw.strip())
    except json.JSONDecodeError as exc:
        raise ParseError(f"not JSON-only output: {exc.msg}") from None
    if not isinstance(data, dict) or set(data) != {"claims"}:
        raise ParseError('top level must be an object with only "claims"')
    claims = data["claims"]
    if not isinstance(claims, list):
        raise ParseError('"claims" must be a list')
    if not MIN_CLAIMS <= len(claims) <= MAX_CLAIMS:
        raise ParseError(f"{len(claims)} claims; need {MIN_CLAIMS}-"
                         f"{MAX_CLAIMS}")
    for n, item in enumerate(claims, 1):
        if not isinstance(item, dict) or set(item) != {"claim", "quote"}:
            raise ParseError(f'claim {n} must have exactly "claim" and '
                             f'"quote"')
        if not all(isinstance(item[k], str) for k in ("claim", "quote")):
            raise ParseError(f"claim {n}: claim and quote must be strings")
        if not item["claim"].strip():
            raise ParseError(f"claim {n}: empty claim")
    return claims


def check_output(raw_stdout, posting):
    """{"parse_error": str|None, "claims": [claim, quote, check, verdict,
    where]}"""
    try:
        claims = parse_claims(raw_stdout)
    except ParseError as exc:
        return {"parse_error": str(exc), "claims": []}
    checked = []
    for item in claims:
        result = check_quote(item["quote"], posting)
        checked.append({"claim": item["claim"], "quote": item["quote"],
                        **result})
    return {"parse_error": None, "claims": checked}


def context(posting, where, width=300):
    """`width` characters of the posting around a found quote; for a quote
    that was not found (or NOT STATED), the first `width` characters of the
    body."""
    if where is None:
        return (posting.get("body_text") or "")[:width]
    text = posting.get(where["field"]) or ""
    start, end = where["start"], where["end"]
    if end - start >= width:
        return text[start:start + width]
    left = max(0, start - (width - (end - start)) // 2)
    left = min(left, max(0, len(text) - width))
    return text[left:left + width]


def load_shortlist(out_dir):
    manifest = json.loads((Path(out_dir) / "shortlist.json")
                          .read_text("utf-8"))
    return manifest


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--shortlist", default="out/shortlist")
    parser.add_argument("--root", default=str(ROOT))
    args = parser.parse_args(argv)
    out_dir = Path(args.shortlist)
    manifest = load_shortlist(out_dir)
    postings = {(p["board"], str(p["id"])): p
                for p in js3_corpus.load(args.root)["postings"]}
    for entry in manifest["postings"]:
        raw_path = out_dir / entry["claude_raw"]
        label = f"{entry['board']}/{entry['id']}"
        if not raw_path.exists():
            print(f"{label}: no Claude output")
            continue
        raw = json.loads(raw_path.read_text("utf-8"))
        result = check_output(raw["raw_stdout"],
                              postings[(entry["board"], entry["id"])])
        if result["parse_error"]:
            print(f"{label}: parse error: {result['parse_error']}")
            continue
        for n, c in enumerate(result["claims"], 1):
            print(f"{label} claim {n}: {c['check']} -> {c['verdict']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
