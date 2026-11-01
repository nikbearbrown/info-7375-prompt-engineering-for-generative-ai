"""Wrong version 2 (CONTRACT.md): substring matching instead of whole words.

`"java" in text` is true for "javascript", so Java is counted as evidence the posting never gives.
"""
from jobwatch import rule
from jobwatch.text import find_substring


def classify(posting, resume):
    return rule.classify(posting, resume, find=find_substring)
