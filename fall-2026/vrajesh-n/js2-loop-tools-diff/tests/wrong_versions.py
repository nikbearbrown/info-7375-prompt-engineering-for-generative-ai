"""The five plausible-but-wrong implementations named in GATE.md. The tests must catch every one."""
import json
import urllib.error

from earlybird import boards
from earlybird.policy import NEEDS_APPROVAL, WRITABLE, Policy
from earlybird.tools import Tools
from earlybird import Refused


def parse_jobs_key_or_empty(platform, body):
    """Wrong version 1: one 'defensive' parser for every ATS. A response with no 'jobs' key is treated as an
    empty board. Lever sends a bare list, so Palantir parses to 0 postings and nothing raises."""
    data = json.loads(body)
    items = data.get("jobs", []) if isinstance(data, dict) else []
    return [boards.normalize(platform, j) for j in items]


class Swallow404Tools(Tools):
    """Wrong version 2: an HTTP 404 is turned into an empty board instead of an error."""

    def fetch(self, board, url, raw_name):
        out = super().fetch(board, url, raw_name)
        if out["status"] == "error" and out["error"].startswith("HTTP 4"):
            return {"status": "ok", "body": b'{"jobs": []}', "raw_path": out.get("raw_path")}
        return out


class PrefixPolicy(Policy):
    """Wrong version 3: checks writes by string prefix, so 'reports-evil' passes as 'reports'."""

    def check_write(self, path, approval=None):
        p = self.resolve(path)
        for rel in NEEDS_APPROVAL:
            if p == (self.root / rel).resolve() and (approval or "").strip() != "yes":
                raise Refused("needs approval")
        if any(str(p).startswith(str((self.root / rel).resolve())) for rel in WRITABLE):
            return p
        raise Refused(f"write to {path} refused")


class BudgetAfterTools(Tools):
    """Wrong version 4: counts the request against the budget after sending it."""

    def fetch(self, board, url, raw_name):
        self.policy.check_fetch(url)
        body, raw_path = self._get(url, raw_name)
        self.budget.spend_request(board)
        return {"status": "ok", "body": body, "raw_path": raw_path}


class RetryOn404Tools(Tools):
    """Wrong version 5: retries every HTTP error, including a 404 that retrying cannot fix."""

    def fetch(self, board, url, raw_name):
        self.policy.check_fetch(url)
        for attempt in (1, 2):
            self.budget.spend_request(board)
            try:
                body, raw_path = self._get(url, raw_name)
                return {"status": "ok", "body": body, "raw_path": raw_path}
            except urllib.error.HTTPError as e:
                if attempt == 1:
                    self.sleep(5)
                    continue
                return {"status": "error", "error": f"HTTP {e.code}"}
