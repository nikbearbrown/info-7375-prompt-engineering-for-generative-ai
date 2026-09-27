# Max-subtraction runs for the Week 01 video.
# Imports probabilities() from the lesson's main.py without modifying it.
import math
import sys
from pathlib import Path

LESSON_CODE = (Path.home() / "info-7375-prompt-engineering-for-generative-ai"
               / "lessons" / "01-randomness-and-first-prompts" / "code")
sys.path.insert(0, str(LESSON_CODE))
from main import probabilities  # noqa: E402


def naive_probabilities(logits):
    weights = [math.exp(x) for x in logits]
    total = sum(weights)
    return [w / total for w in weights]


print("=== [1, 2, 3] ===")
logits = [1, 2, 3]
peak = max(logits)
raw = [math.exp(x) for x in logits]
shifted = [math.exp(x - peak) for x in logits]
print("raw exp(x):          ", raw)
print("shifted exp(x - max):", shifted)
print("probs from raw:      ", [w / sum(raw) for w in raw])
print("probs from shifted:  ", [w / sum(shifted) for w in shifted])
print("main.probabilities():", probabilities(logits))

print()
print("=== [1000, 1000] ===")
big = [1000, 1000]
try:
    print("naive (no max-subtraction):", naive_probabilities(big))
except Exception as exc:
    print(f"naive (no max-subtraction): {type(exc).__name__}: {exc}")
print("main.probabilities():      ", probabilities(big))

print()
print("=== [1000, 1001] ===")
gap = [1000, 1001]
try:
    print("naive (no max-subtraction):", naive_probabilities(gap))
except Exception as exc:
    print(f"naive (no max-subtraction): {type(exc).__name__}: {exc}")
print("main.probabilities():      ", probabilities(gap))
print("main.probabilities([0, 1]):", probabilities([0, 1]))

print()
print("=== [0, -1000] ===")
print("math.exp(-1000):     ", math.exp(-1000))
print("main.probabilities():", probabilities([0, -1000]))
