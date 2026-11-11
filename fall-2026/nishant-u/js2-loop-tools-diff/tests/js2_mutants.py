"""GATE.md's six wrong versions, each a subclass of the real code that differs in one way.

Built lazily (inside functions) so that, before agent2 exists, each test fails on its own.
Each must be caught by a test in test_js2_mutants.py.
"""
import importlib
import json


def _policy():
    return importlib.import_module("agent2.policy")


def _loop():
    return importlib.import_module("agent2.loop")


def prefix_policy():
    """Wrong version 1: containment by string prefix, so out-evil passes as inside out."""
    class PrefixPolicy(_policy().Policy):
        def _contained(self, base, path):
            return str(path).startswith(str(base))
    return PrefixPolicy


def uncounted_retry_loop():
    """Wrong version 2: an error-policy retry is not counted against the request budget."""
    class UncountedRetryLoop(_loop().Loop):
        def _count_request(self, kind):
            if kind != "retry":
                super()._count_request(kind)
    return UncountedRetryLoop


def finished_despite_failure_loop():
    """Wrong version 3: a run whose boards were all attempted reports finished, failures or not."""
    class FinishedAnywayLoop(_loop().Loop):
        def exit_status(self, stopped_by_budget):
            return "budget-exhausted" if stopped_by_budget else "finished"
    return FinishedAnywayLoop


def truthy_approval_policy():
    """Wrong version 4: any truthy value ("yes", 1) counts as approval."""
    class TruthyPolicy(_policy().Policy):
        def _approved(self, value):
            return bool(value)
    return TruthyPolicy


def invented_value_loop():
    """Wrong version 5: a failed board is reported as 0 postings and "0 new"."""
    class InventedValueLoop(_loop().Loop):
        def _fail(self, entry, reason, http_status=None):
            super()._fail(entry, reason, http_status)
            entry["postings"], entry["new_ids"] = 0, []
    return InventedValueLoop


def replacing_update_policy():
    """Wrong version 6: update_state replaces the whole set with the given ids instead of merging."""
    class ReplacingPolicy(_policy().Policy):
        def update_state(self, target, ids, boards=()):
            path = self.authorize("update_state", target)
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps({"seen_ids": sorted(set(ids)), "boards": sorted(set(boards))}),
                            encoding="utf-8")
            return sorted(set(ids))
    return ReplacingPolicy
