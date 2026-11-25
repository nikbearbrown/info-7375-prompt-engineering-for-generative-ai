"""The only way the loop touches the network or the disk. Every call goes through policy, budget and trace."""
import json
import socket
import time
import urllib.error
import urllib.request
from urllib.parse import urlparse, urlunparse

from . import gate

# Ashby answered 403 to urllib's default User-Agent on 2026-10-14; identify ourselves honestly.
USER_AGENT = "earlybird/0.2 (INFO 7375 student project; read-only)"
TRANSIENT = (urllib.error.URLError, TimeoutError, socket.timeout, ConnectionError)


class Trace:
    """Every observation the loop makes, in order. Written to reports/<label>-trace.jsonl."""

    def __init__(self, budget):
        self.budget = budget
        self.events = []

    def record(self, board, action, **detail):
        event = {"step": len(self.events) + 1, "t": round(self.budget.elapsed(), 2), "board": board,
                 "action": action, **detail, "budget": self.budget.snapshot()}
        self.events.append(event)
        return event

    def jsonl(self):
        return "".join(json.dumps(e, ensure_ascii=False) + "\n" for e in self.events)


def same_action_key(url):
    u = urlparse(url)
    return urlunparse((u.scheme, (u.hostname or "").lower(), u.path, "", u.query, ""))


class Tools:
    def __init__(self, policy, budget, trace, day, replay=False, opener=urllib.request.urlopen,
                 sleep=time.sleep):
        self.policy, self.budget, self.trace, self.day = policy, budget, trace, day
        self.replay, self.opener, self.sleep = replay, opener, sleep
        self.done = set()

    # --- fetch, with the repeat rule and the error policy ----------------
    def fetch(self, board, url, raw_name):
        """Return {"status": "ok", "body", "raw_path"} or {"status": "error"|"repeat-refused", "error"}.

        Refused (policy) and BudgetExhausted propagate: the loop stops on them.
        """
        self.policy.check_fetch(url)
        key = same_action_key(url)
        if key in self.done:
            self.trace.record(board, "fetch", url=url, result="repeat-refused",
                              why="same URL already fetched in this run (GATE.md repeat rule)")
            return {"status": "repeat-refused", "error": "repeat of an action already taken this run"}
        self.done.add(key)
        for attempt in (1, 2):
            self.budget.spend_request(f"{board} attempt {attempt}")
            try:
                body, raw_path = self._get(url, raw_name)
            except urllib.error.HTTPError as e:
                err_path = self._save_error(raw_name, f"HTTP {e.code}", e)
                transient = 500 <= e.code < 600
                if transient and attempt == 1:
                    self._retry(board, url, f"HTTP {e.code}")
                    continue
                self.trace.record(board, "fetch", url=url, attempt=attempt, result="error", http=e.code,
                                  raw_path=err_path,
                                  why="4xx: retrying cannot fix it" if not transient else "5xx twice")
                return {"status": "error", "error": f"HTTP {e.code}", "raw_path": err_path}
            except FileNotFoundError:
                self.trace.record(board, "fetch", url=url, attempt=attempt, result="error",
                                  why=f"replay: no saved response data/raw/{self.day}/{raw_name}")
                return {"status": "error", "error": "no saved response for this day"}
            except TRANSIENT as e:
                if attempt == 1:
                    self._retry(board, url, type(e).__name__)
                    continue
                self.trace.record(board, "fetch", url=url, attempt=attempt, result="error",
                                  error=f"{type(e).__name__}: {e}", why="failed again after 1 retry")
                return {"status": "error", "error": f"{type(e).__name__} after 1 retry"}
            self.trace.record(board, "fetch", url=url, attempt=attempt, result="ok",
                              source="replay" if self.replay else "live", bytes=len(body), raw_path=raw_path)
            return {"status": "ok", "body": body, "raw_path": raw_path}
        raise AssertionError("unreachable")  # pragma: no cover

    def _retry(self, board, url, why):
        self.trace.record(board, "fetch", url=url, attempt=1, result="retry 1/1",
                          why=f"{why}: transient, waiting {gate.RETRY_WAIT_SECONDS}s (GATE.md error policy)")
        self.sleep(gate.RETRY_WAIT_SECONDS)

    def _get(self, url, raw_name):
        rel = f"data/raw/{self.day}/{raw_name}"
        if self.replay:
            path = self.policy.check_read(rel)
            return path.read_bytes(), rel
        req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT}, method="GET")
        with self.opener(req, timeout=30) as resp:
            body = resp.read()
        self.write_bytes(rel, body)
        return body, rel

    def _save_error(self, raw_name, status, err):
        if self.replay:
            return None
        rel = f"data/raw/{self.day}/{raw_name.rsplit('.', 1)[0]}.error.txt"
        try:
            body = err.read()
        except Exception:  # an HTTPError may carry no body
            body = b""
        self.write_bytes(rel, f"{status}\n".encode() + body)
        return rel

    # --- disk ----------------------------------------------------------
    def read_text(self, rel):
        return self.policy.check_read(rel).read_text(encoding="utf-8")

    def write_bytes(self, rel, data, approval=None):
        path = self.policy.check_write(rel, approval)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return path

    def write_text(self, rel, text, approval=None):
        return self.write_bytes(rel, text.encode("utf-8"), approval)
