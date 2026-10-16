"""Print every number shown in the video, straight from the lesson's code.

Imports probabilities() from lessons/01-randomness-and-first-prompts/code/main.py
(unchanged) and prints each intermediate of the transformation for the
constructed scores [1, 2, 3] and [-1, 2, 3], plus the divide-by-sum contrast.
Standard library only. Run from the course repository root:

    python3 fall-2026/aravind-s/week-01-video/evidence/softmax_steps.py
"""
import importlib.util
import math
import platform
from pathlib import Path


def find_main():
    """Locate the lesson's main.py by walking up to the course repo root."""
    here = Path(__file__).resolve()
    for parent in here.parents:
        candidate = parent / "lessons/01-randomness-and-first-prompts/code/main.py"
        if candidate.exists():
            return candidate
    raise FileNotFoundError("run this inside the INFO 7375 course repository")


spec = importlib.util.spec_from_file_location("lesson_main", find_main())
lesson = importlib.util.module_from_spec(spec)
spec.loader.exec_module(lesson)


def fmt(values, places=4):
    return "[" + ", ".join(f"{v:.{places}f}" for v in values) + "]"


def steps(scores):
    """The same arithmetic as probabilities(), one line per intermediate."""
    peak = max(scores)
    shifted = [s - peak for s in scores]
    weights = [math.exp(s) for s in shifted]
    total = sum(weights)
    return peak, shifted, weights, total


def show(scores):
    peak, shifted, weights, total = steps(scores)
    probs = lesson.probabilities(scores)  # the lesson's own function
    print(f"scores            {scores}")
    print(f"peak (max)        {peak}")
    print(f"minus peak        {shifted}")
    print(f"weights = exp     {fmt(weights)}")
    print(f"total weight      {total:.4f}")
    print(f"probabilities()   {fmt(probs)}")
    print(f"sum               {sum(probs):.4f}")
    ratios = [probs[i + 1] / probs[i] for i in range(len(probs) - 1)]
    print(f"neighbour ratios  {fmt(ratios)}")
    order_kept = sorted(range(3), key=lambda i: scores[i]) == \
        sorted(range(3), key=lambda i: probs[i])
    print(f"order preserved   {order_kept}")


def divide_by_sum(scores):
    total = sum(scores)
    if total == 0:
        return f"sum = 0 -> ZeroDivisionError"
    return f"sum = {total} -> {fmt([s / total for s in scores])}"


print(f"Python {platform.python_version()} · lesson file {find_main().name}")
print(f"e = {math.e:.4f}")
print()
print("== The lesson's rule on the constructed scores [1, 2, 3] (temperature 1.0)")
show([1, 2, 3])
print()
print("== The lesson's rule on [-1, 2, 3]")
show([-1, 2, 3])
print()
print("== Divide-by-sum (NOT the lesson's rule; shown only for contrast)")
for s in ([1, 2, 3], [-1, 2, 3], [-1, 0, 1]):
    print(f"{str(s):12}      {divide_by_sum(s)}")
r = (3 / 6) / (2 / 6)
print(f"divide-by-sum neighbour ratio for [1, 2, 3]: 0.5000 / 0.3333 = {r:.4f}")
