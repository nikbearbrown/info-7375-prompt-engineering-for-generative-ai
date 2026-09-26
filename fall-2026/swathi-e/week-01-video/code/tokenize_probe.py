#!/usr/bin/env python3
"""
tokenize_probe.py -- INFO 7375 Week 01 Explainer Video
Swathi Baba Eswarappa

Mechanistic groundwork for the claim:
  "The unit is a token, not a word -- and why that breaks letter-counting prompts."

Every number printed here is produced live by `tiktoken` on this machine.
Nothing in the video is hand-typed; the video reads this file's output.

Run:  python3 code/tokenize_probe.py
"""
import json
import sys
from collections import Counter

import tiktoken

WORDS = ["strawberry", "banana", "occurrence"]
ENCODINGS = ["cl100k_base", "o200k_base"]
# The letter we ask the model to count, per word.
TARGET = {"strawberry": "r", "banana": "a", "occurrence": "c"}


def probe(word: str, enc_name: str) -> dict:
    enc = tiktoken.get_encoding(enc_name)
    ids = enc.encode(word)
    pieces = [enc.decode([i]) for i in ids]

    target = TARGET[word]
    true_count = word.count(target)

    # Where does the target letter actually live, by absolute character index?
    char_idx = [i for i, ch in enumerate(word) if ch == target]

    # Rebuild the character span each token covers, so we can show exactly
    # which token boundary each occurrence of the target letter falls inside.
    spans, cursor = [], 0
    for p in pieces:
        spans.append((cursor, cursor + len(p)))
        cursor += len(p)

    # Per-token count of the target letter. Summing these is what a model would
    # have to do -- but only if it could see inside a token, which it cannot.
    per_token = [p.count(target) for p in pieces]

    return {
        "word": word,
        "encoding": enc_name,
        "char_len": len(word),
        "token_ids": ids,
        "token_pieces": pieces,
        "n_tokens": len(ids),
        "target_letter": target,
        "true_letter_count": true_count,
        "target_char_indices": char_idx,
        "token_char_spans": spans,
        "per_token_target_count": per_token,
        "letter_count_crosses_boundary": sum(1 for c in per_token if c > 0) > 1,
        "roundtrip_ok": enc.decode(ids) == word,
    }


def main() -> int:
    results = []
    for enc_name in ENCODINGS:
        for word in WORDS:
            results.append(probe(word, enc_name))

    w = 78
    print("=" * w)
    print("TOKENIZER PROBE -- tiktoken %s | python %s"
          % (tiktoken.__version__, sys.version.split()[0]))
    print("=" * w)

    for r in results:
        print()
        print("-" * w)
        print("word=%-12s encoding=%-12s chars=%d  tokens=%d"
              % (r["word"], r["encoding"], r["char_len"], r["n_tokens"]))
        print("-" * w)
        print("  token IDs      : %s" % r["token_ids"])
        print("  token pieces   : %s" % r["token_pieces"])
        for (piece, tid, (a, b), c) in zip(
            r["token_pieces"], r["token_ids"], r["token_char_spans"],
            r["per_token_target_count"]
        ):
            print("      %-10r id=%-8d chars[%d:%d]  '%s' x%d"
                  % (piece, tid, a, b, r["target_letter"], c))
        print("  target letter  : '%s'" % r["target_letter"])
        print("  true count     : %d   at char indices %s"
              % (r["true_letter_count"], r["target_char_indices"]))
        print("  per-token split: %s  -> sum=%d"
              % (r["per_token_target_count"], sum(r["per_token_target_count"])))
        print("  crosses token boundary: %s" % r["letter_count_crosses_boundary"])
        print("  decode(ids) == word  : %s" % r["roundtrip_ok"])

    # ---- The headline fact, stated as a measurement, not an opinion. --------
    print()
    print("=" * w)
    print("WHAT THE MODEL RECEIVES")
    print("=" * w)
    for r in results:
        if r["word"] == "strawberry":
            print("  %-12s -> %d integers: %s"
                  % (r["encoding"], r["n_tokens"], r["token_ids"]))
    print()
    print("  The 10 characters of 'strawberry' are never handed to the model.")
    print("  A small list of integers is. Each integer is then replaced by a")
    print("  learned embedding vector. The vector is indexed BY the integer;")
    print("  it is not built FROM the letters. There is no 'r' in a vector.")

    with open("code/token_probe_output.json", "w") as fh:
        json.dump(results, fh, indent=2)
    print()
    print("  [wrote code/token_probe_output.json]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
