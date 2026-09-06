# INFO 7375: Training mechanics and Claude configuration
# Companion: lessons/09-training-and-configuration/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
import math

def sigmoid(x):
    if x >= 0:
        return 1 / (1 + math.exp(-x))
    e = math.exp(x)
    return e / (1 + e)

def loss(data, w, b):
    return sum(max(w*x+b, 0) - y*(w*x+b) + math.log1p(math.exp(-abs(w*x+b)))
               for x, y in data) / len(data)

def train(data, steps=200, rate=.2):
    if not data or any(not math.isfinite(x) or y not in (0, 1) for x, y in data):
        raise ValueError("Need finite features and binary labels")
    if type(steps) is not int or steps < 1 or not math.isfinite(rate) or rate <= 0:
        raise ValueError("Positive training budget and rate required")
    w = b = 0.0
    history = [loss(data, w, b)]
    for _ in range(steps):
        errors = [(sigmoid(w*x+b)-y, x) for x, y in data]
        w -= rate * sum(e*x for e, x in errors) / len(data)
        b -= rate * sum(e for e, _ in errors) / len(data)
    history.append(loss(data, w, b))
    return {"w":w, "b":b, "loss":history}

def demo():
    return train([(-2,0), (-1,0), (1,1), (2,1)])

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
