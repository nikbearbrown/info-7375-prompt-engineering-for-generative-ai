# INFO 7375: Context retrieval and Claude Cowork
# Companion: lessons/07-context-retrieval-and-cowork/docs/en.md
# Python standard library; offline reference implementation.
# Read the lesson limitations before reusing this teaching example.
import math
import re
from collections import Counter

def vector(text):
    return Counter(re.findall(r"\b\w+\b", text.lower()))

def cosine(left, right):
    dot = sum(value * right.get(term, 0) for term, value in left.items())
    norm = math.sqrt(sum(v*v for v in left.values()) * sum(v*v for v in right.values()))
    return dot / norm if norm else 0.0

def retrieve(query, documents, k=2):
    if type(k) is not int or k < 1:
        raise ValueError("k must be positive")
    query_vector = vector(query)
    scores = [(key, cosine(query_vector, vector(text))) for key, text in documents.items()]
    return sorted((row for row in scores if row[1] > 0), key=lambda row: (-row[1], row[0]))[:k]

def demo():
    return retrieve("office hours", {"s1": "Office hours by appointment",
                                      "s2": "Submit Python assignments"})

if __name__ == "__main__":
    import json
    print(json.dumps(demo(), indent=2))
