"""Deterministic SQL helper functions registered on every connection.

title_has() is the recovery planned in pre-mortem.md: a whole-phrase title match
after case and punctuation normalization. median() fills a gap in SQLite.
"""

import re
import statistics


def normalized(value):
    """Lower-case, turn every run of non-alphanumerics into one space, trim."""
    return re.sub(r"[^a-z0-9]+", " ", (value or "").casefold()).strip()


def title_has(title, phrase):
    """1 if the normalized phrase appears as whole words in the normalized title."""
    phrase = normalized(phrase)
    if not phrase:
        return 0
    return 1 if f" {phrase} " in f" {normalized(title)} " else 0


class Median:
    def __init__(self):
        self.values = []

    def step(self, value):
        if value is None or value == "":
            return
        try:
            self.values.append(float(value))
        except (TypeError, ValueError):
            return

    def finalize(self):
        return statistics.median(self.values) if self.values else None


def register(con):
    con.create_function("norm", 1, normalized, deterministic=True)
    con.create_function("title_has", 2, title_has, deterministic=True)
    con.create_aggregate("median", 1, Median)
