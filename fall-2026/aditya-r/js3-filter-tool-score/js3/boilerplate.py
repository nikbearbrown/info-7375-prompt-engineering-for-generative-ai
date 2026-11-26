"""Boilerplate segments per board: a normalized segment (line or sentence) that appears in >= 20% of that board's
postings in this corpus. Published as filters/boilerplate_segments.json so a reader can check by hand whether a
quote is boilerplate.  .venv/bin/python -m js3.boilerplate
"""
import json
from collections import Counter, defaultdict
from pathlib import Path

from inherited.rules import normalize

from .corpus import load_corpus
from .text import readable, segments

ROOT = Path(__file__).resolve().parent.parent
PATH = ROOT / "filters" / "boilerplate_segments.json"
MIN_SHARE = 0.2


def compute(corpus=None):
    corpus = corpus or load_corpus()
    seg, n = defaultdict(Counter), Counter()
    for p in corpus.values():
        n[p["board"]] += 1
        for s in {normalize(x) for x in segments(readable(p["text"]))}:
            if s:
                seg[p["board"]][s] += 1
    return {"min_share": MIN_SHARE, "postings_per_board": dict(sorted(n.items())),
            "segments": {b: sorted(s for s, k in cnt.items() if k >= MIN_SHARE * n[b]) for b, cnt in sorted(seg.items())}}


_cache = {}


def load():
    if "b" not in _cache:
        _cache["b"] = {b: set(v) for b, v in json.loads(PATH.read_text())["segments"].items()}
    return _cache["b"]


if __name__ == "__main__":
    out = compute()
    PATH.write_text(json.dumps(out, indent=1, ensure_ascii=False) + "\n")
    print({b: len(v) for b, v in out["segments"].items()})
