"""The contract's three wrong versions, as plausible-but-wrong implementations.

Each one must be caught by a test in test_mutants.py. They wrap the real
agent so that each differs from it in exactly one way.
"""
import importlib


def _rules():
    return importlib.import_module("agent.rules")


def shifted_judge_all(postings, resume, requirements):
    """Wrong version 1: verdicts attached to the wrong ids, shifted by one after sorting."""
    ordered = sorted(postings, key=lambda p: p["id"])
    verdicts = [_rules().evaluate(p, resume, requirements) for p in ordered]
    ids = [p["id"] for p in ordered]
    for verdict, posting_id in zip(verdicts, ids[1:] + ids[:1]):
        verdict["posting_id"] = posting_id
    return verdicts


def uncited_judge_all(postings, resume, requirements):
    """Wrong version 2: right verdicts, but the justification cites nothing."""
    verdicts = _rules().judge_all(postings, resume, requirements)
    for verdict in verdicts:
        verdict["citations"] = []
    return verdicts


def string_skills(resume, requirements):
    """Wrong version 3: iterates every value under skills, so the agent_note string
    is read letter by letter and single letters count as skills."""
    found = []
    for field, value in resume["skills"].items():
        for skill in value:
            found.append((field, skill))
    return found
