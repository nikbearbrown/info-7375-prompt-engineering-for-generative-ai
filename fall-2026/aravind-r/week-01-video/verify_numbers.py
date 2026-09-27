"""Print every number that appears on screen in the video, from a real run.

Run it yourself and paste the output (with the header lines) into SOURCES.md.
probabilities() below is copied verbatim from Chapter 1, Part 2. Cross-check its
[1, 2, 3] output against what lessons/01-randomness-and-first-prompts/code/main.py
prints at temperature 1.0 — if they disagree, the lesson code wins and the
video changes.
"""
import datetime
import math
import platform
import sys


def probabilities(logits, temperature=1.0):
    if not logits or not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("Need logits and a positive finite temperature")
    if not all(math.isfinite(x) for x in logits):
        raise ValueError("Logits must be finite")
    peak = max(logits)
    weights = [math.exp((x - peak) / temperature) for x in logits]
    total = sum(weights)
    return [weight / total for weight in weights]


def fmt(values, places):
    return "[" + ", ".join(f"{v:.{places}f}" for v in values) + "]"


print("run date:", datetime.datetime.now().astimezone().isoformat(timespec="seconds"))
print("python:", platform.python_version(), "|", sys.platform)
print()

z = [1, 2, 3]
direct = [math.exp(x) for x in z]
shifted = [math.exp(x - max(z)) for x in z]
p_direct = [w / sum(direct) for w in direct]
p_shifted = [w / sum(shifted) for w in shifted]
print("B03 direct weights      ", fmt(direct, 6), " sum", f"{sum(direct):.6f}")
print("B03 direct probabilities", fmt(p_direct, 10))
print("B04 shifted scores      ", [x - max(z) for x in z])
print("B04 shifted weights     ", fmt(shifted, 6), " sum", f"{sum(shifted):.6f}")
print("B04 shifted probabilities", fmt(p_shifted, 10))
print("B04 bit-identical?      ", p_direct == p_shifted)
print("B04 largest difference  ", max(abs(a - b) for a, b in zip(p_direct, p_shifted)))
print("chapter probabilities() ", probabilities(z))
print()

try:
    math.exp(1000)
    print("B07 math.exp(1000)       did NOT raise — update the video")
except OverflowError as err:
    print("B07 math.exp(1000)      ", f"{type(err).__name__}: {err}")
print("B07 probabilities([1000, 1000])", probabilities([1000, 1000]))
print("B07 largest float       ", sys.float_info.max)
print()

print("B08 math.exp(-1000)     ", math.exp(-1000))
print("B08 probabilities([0, -1000])", probabilities([0, -1000]))
print("B08 smallest positive float", math.ulp(0.0))
print("B08 true size of exp(-1000) = 10 **", round(-1000 / math.log(10), 2), "(computed, not printed by Python)")
