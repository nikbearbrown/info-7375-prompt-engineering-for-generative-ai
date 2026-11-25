"""FILTER.md's four wrong versions, each a patch to the real agent3 code that differs in one way.

Each returns a context manager (unittest.mock.patch) and is built lazily, so before agent3
exists each mutant test fails on its own. test_js3_mutants.py shows each one is caught.
"""
import re
from unittest import mock

from tests.js3_helpers import flt, sl


def substring_matching():
    """Wrong version 1: a term matches anywhere, so 'ML' in 'HTML' and 'data' in 'metadata' count."""
    def find_term(text, term):
        match = re.search(re.escape(term), text or "", re.IGNORECASE)
        return match.group(0) if match else None
    return mock.patch.object(flt(), "find_term", find_term)


def silence_as_sponsorship():
    """Wrong version 2: a posting that never mentions visas is labeled 'sponsors visas: supported'."""
    real = sl().label_c3

    def label_c3(posting):
        result = real(posting)
        if result["label"] == "insufficient":
            return dict(result, label="supported")
        return result
    return mock.patch.object(sl(), "label_c3", label_c3)


def rank_by_keyword_count():
    """Wrong version 3: rank by how often role words occur, not by supported claims."""
    def rank_key(entry):
        text = entry["posting"]["text"] or ""
        hits = sum(len(re.findall(r"(?<!\w)" + re.escape(w) + r"(?!\w)", text, re.IGNORECASE))
                   for w in flt().ROLE_WORDS)
        return (-hits, entry["posting_id"])
    return mock.patch.object(sl(), "rank_key", rank_key)


def missing_location_defaulted():
    """Wrong version 4: a posting with no location is read as US-based."""
    real = flt().read_location

    def read_location(system, job):
        field, value = real(system, job)
        return field, value if value else "Remote - US"
    return mock.patch.object(flt(), "read_location", read_location)
