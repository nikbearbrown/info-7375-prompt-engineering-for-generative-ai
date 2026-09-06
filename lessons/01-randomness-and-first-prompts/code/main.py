# INFO 7375: Randomness and first prompts
# Companion: lessons/01-randomness-and-first-prompts/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
import math
import random
from collections import Counter

def probabilities(logits, temperature=1.0):
    if not logits or not math.isfinite(temperature) or temperature <= 0:
        raise ValueError("Need logits and a positive finite temperature")
    if not all(math.isfinite(x) for x in logits):
        raise ValueError("Logits must be finite")
    peak = max(logits)
    weights = [math.exp((x - peak) / temperature) for x in logits]
    total = sum(weights)
    return [weight / total for weight in weights]

def sample(logits, count=1000, seed=7, temperature=1.0):
    if type(count) is not int or count < 0:
        raise ValueError("Count must be nonnegative")
    rng = random.Random(seed)
    return dict(Counter(rng.choices(range(len(logits)),
                                   probabilities(logits, temperature), k=count)))

def demo():
    return {"probabilities": probabilities([1, 2, 3]),
            "counts": sample([1, 2, 3])}

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
