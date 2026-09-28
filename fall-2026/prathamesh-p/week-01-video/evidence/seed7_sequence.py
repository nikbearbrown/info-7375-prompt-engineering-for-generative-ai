"""Regenerate the exact seed-7 draw sequence behind main.py's counts.

Makes the same call sample() makes -- random.Random(7).choices(range(3),
probabilities([1, 2, 3], 1.0), k=1000) -- with probabilities() imported from
the course's own main.py, so the weights are identical. It saves the sequence
and exits non-zero unless the counts match main.py exactly.
"""
import json
import random
import sys
from collections import Counter
from pathlib import Path

COURSE_CODE = Path(r"C:\info7375\info-7375-prompt-engineering-for-generative-ai"
                   r"\lessons\01-randomness-and-first-prompts\code")
sys.path.insert(0, str(COURSE_CODE))
from main import probabilities, sample  # noqa: E402  (course reference code)

LOGITS, SEED, COUNT, TEMPERATURE = [1, 2, 3], 7, 1000, 1.0
EXPECTED = {"1": 268, "2": 630, "0": 102}  # main_output_2026-09-27.txt

rng = random.Random(SEED)
sequence = rng.choices(range(len(LOGITS)), probabilities(LOGITS, TEMPERATURE), k=COUNT)
counts = {str(k): v for k, v in Counter(sequence).items()}

# Cross-check against the course function itself, not just the saved file.
assert counts == {str(k): v for k, v in sample(LOGITS, COUNT, SEED, TEMPERATURE).items()}
if counts != EXPECTED:
    sys.exit(f"MISMATCH: {counts} != {EXPECTED}")

out = Path(__file__).with_name("seed7_sequence.json")
out.write_text(json.dumps({
    "call": "random.Random(7).choices(range(3), probabilities([1, 2, 3], 1.0), k=1000)",
    "source": str(COURSE_CODE / "main.py"),
    "python": sys.version.split()[0],
    "counts": counts,
    "sequence": sequence,
}, indent=1), encoding="utf-8")
print(f"OK counts={counts} first20={sequence[:20]} -> {out}")
