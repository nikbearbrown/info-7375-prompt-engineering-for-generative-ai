"""One change to one object at a time (Chapter 9), and its measurement on labels.

A variant is a JSON file naming the one object it changes and the module attribute(s) that hold
it, for example:

  {"name": "v0.2-cut-machine-learning-from-description",
   "object": "the filter file (FILTER.md description topics)",
   "set": {"jobwatch.screen.DESCRIPTION_TOPICS": ["model inference", "model serving", ...]}}

rescore() rebuilds the filter's records with only that change in place; everything else (the
corpus, the tokenizer, the other rules, the labels) is the same object as before."""

import json
from contextlib import ExitStack
from unittest import mock

from jobwatch import screen


def load(path):
    with open(path, encoding="utf-8") as fh:
        spec = json.load(fh)
    if not spec.get("object") or not spec.get("set"):
        raise ValueError(f"{path}: a variant names one object and the attribute(s) it sets")
    return spec


def _value(v):
    return tuple(v) if isinstance(v, list) else v


def rescore(items, spec=None):
    """{(board, key): record} for the given items, with the variant's change in place (or none)."""
    with ExitStack() as stack:
        for target, value in ((spec or {}).get("set") or {}).items():
            stack.enter_context(mock.patch(target, _value(value)))
        return {(i.board, i.key): screen.score(i) for i in items}
