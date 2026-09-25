#!/usr/bin/env python3
"""
embedding_probe.py -- INFO 7375 Week 01 Explainer Video
Swathi Baba Eswarappa

Two follow-up measurements that pin down the mechanism:

  (A) The split is a property of the TOKENIZER, not of the word.
      cl100k_base and o200k_base cut 'strawberry' in different places.
      If letter structure were what the model indexes on, the cut could
      not move. It moves.

  (B) Spacing the word out changes the token IDs entirely -- which is
      exactly why the "spell it out" prompt trick works. This is the
      control experiment for the whole claim.

  (D) Merges are frequency-driven: a common string survives as ONE token,
      a rare one shatters. This is WHY the boundary lands where it does.

Run:  python3 code/embedding_probe.py
"""
import json

import numpy as np
import tiktoken

W = 78


def section(title: str) -> None:
    print()
    print("=" * W)
    print(title)
    print("=" * W)


def main() -> int:
    out = {}

    # ---- (A) the cut moves between tokenizers ---------------------------
    section("(A) THE SPLIT BELONGS TO THE TOKENIZER, NOT THE WORD")
    a = {}
    for name in ["cl100k_base", "o200k_base"]:
        enc = tiktoken.get_encoding(name)
        ids = enc.encode("strawberry")
        pieces = [enc.decode([i]) for i in ids]
        a[name] = {"ids": ids, "pieces": pieces, "vocab": enc.n_vocab}
        print("  %-12s vocab=%-7d  %s" % (name, enc.n_vocab, " | ".join(pieces)))
        print("  %-12s %s" % ("", "  ".join(str(i) for i in ids)))
    print()
    print("  Same 10 characters. Different cut. 'str|aw' vs 'st|raw'.")
    print("  The boundary is an artifact of which merge table was trained,")
    print("  not of anything inside the word.")
    out["tokenizer_dependence"] = a

    # ---- (B) the control: space the letters out --------------------------
    section("(B) CONTROL -- SPACING THE WORD CHANGES THE INPUT ENTIRELY")
    enc = tiktoken.get_encoding("cl100k_base")
    b = {}
    for label, text in [("plain", "strawberry"), ("spaced", "s t r a w b e r r y")]:
        ids = enc.encode(text)
        pieces = [enc.decode([i]) for i in ids]
        b[label] = {"text": text, "ids": ids, "pieces": pieces, "n": len(ids)}
        print("  %-7s %-21r -> %2d tokens" % (label, text, len(ids)))
        print("          pieces: %s" % pieces)
        print("          ids   : %s" % ids)
    print()
    n_plain, n_spaced = b["plain"]["n"], b["spaced"]["n"]
    print("  %d tokens vs %d tokens for the same word." % (n_plain, n_spaced))
    print("  Spaced out, every letter gets its OWN id -- so 'r' becomes")
    print("  countable the same way any repeated token is countable.")
    print("  The prompt trick does not make the model smarter about letters.")
    print("  It changes the input so the letters are tokens in the first place.")
    out["spacing_control"] = b

    # ---- (C) what the embedding lookup actually is -----------------------
    section("(C) THE EMBEDDING LOOKUP IS A ROW INDEX, NOT A SPELLING")
    rng = np.random.default_rng(7375)          # seeded: illustration is reproducible
    d_model = 8                                 # tiny, for display only
    ids = b["plain"]["ids"]
    print("  ILLUSTRATION (constructed): a real embedding table is not public,")
    print("  so the vectors below are random, seed=7375, d_model=%d." % d_model)
    print("  What is NOT constructed is the operation: E[token_id] -> row.")
    print()
    for tid, piece in zip(ids, b["plain"]["pieces"]):
        vec = rng.normal(0, 1, d_model).round(3)
        print("  E[%-6d]  (%-6r)  ->  %s" % (tid, piece, vec))
    print()
    print("  Nothing on the right-hand side is addressed by character.")
    print("  There is no slot for 'the 3rd letter'. The row is fetched by the")
    print("  integer and by nothing else. The spelling was consumed upstream.")
    out["embedding_illustration"] = {
        "constructed": True, "seed": 7375, "d_model": d_model,
        "note": "vectors random; the lookup-by-integer operation is real",
    }

    # ---- (D) merges follow frequency, not spelling --------------------
    section("(D) THE MERGE TABLE FOLLOWS FREQUENCY, NOT SPELLING")
    enc = tiktoken.get_encoding("cl100k_base")
    ladder = ["the", "people", "berry", "strawberry", "zyzzyva"]
    d = {}
    print("  %-14s %5s %5s %6s  pieces" % ("string", "chars", "toks", "ch/tok"))
    for wd in ladder:
        i = enc.encode(wd)
        pc = [enc.decode(x) for x in [[y] for y in i]]
        d[wd] = {"ids": i, "pieces": pc, "chars": len(wd),
                 "n": len(i), "chars_per_token": round(len(wd) / len(i), 2)}
        print("  %-14s %5d %5d %6.2f  %s"
              % (wd, len(wd), len(i), len(wd) / len(i), pc))
    print()
    print("  'berry' alone is ONE token (%d). Inside 'strawberry' it is still"
          % d["berry"]["ids"][0])
    print("  that same token -- but 'straw' is not common enough to survive, so")
    print("  it breaks into 'str'+'aw'. Meanwhile 'zyzzyva' (%d chars) shatters"
          % d["zyzzyva"]["chars"])
    print("  into %d tokens. BPE merges the most frequent adjacent pairs during"
          % d["zyzzyva"]["n"])
    print("  training; nothing in that process is aware of letters or spelling.")
    out["frequency_ladder"] = d

    with open("code/embedding_probe_output.json", "w") as fh:
        json.dump(out, fh, indent=2)
    print()
    print("  [wrote code/embedding_probe_output.json]")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
