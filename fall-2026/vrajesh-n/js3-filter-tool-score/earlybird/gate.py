"""Budgets from GATE.md. Only a reviewed commit may change these constants; a run may only lower them."""
import time

from . import Refused

MAX_BOARDS = 12
MAX_REQUESTS = 15
MAX_SECONDS = 180
RETRY_WAIT_SECONDS = 5


class BudgetExhausted(Exception):
    """Raised before an action that would go over a budget. The action does not happen."""


class Budget:
    def __init__(self, boards=MAX_BOARDS, requests=MAX_REQUESTS, seconds=MAX_SECONDS, clock=time.monotonic):
        caps = {"boards": MAX_BOARDS, "requests": MAX_REQUESTS, "seconds": MAX_SECONDS}
        self.limits = {"boards": boards, "requests": requests, "seconds": seconds}
        for name, value in self.limits.items():
            if not isinstance(value, (int, float)) or value < 0:
                raise Refused(f"budget {name}={value!r} is not a non-negative number")
            if value > caps[name]:
                raise Refused(f"budget {name}={value} is above the GATE.md limit {caps[name]}; "
                              "only a reviewed commit may raise it")
        self.used = {"boards": 0, "requests": 0}
        self.clock = clock
        self.start = clock()

    def elapsed(self):
        return self.clock() - self.start

    def start_board(self, key):
        if self.used["boards"] >= self.limits["boards"]:
            raise BudgetExhausted(f"boards budget {self.limits['boards']} reached before {key}")
        self.used["boards"] += 1

    def spend_request(self, what):
        """Check, then count. Called before the request goes out, so an over-budget request never happens."""
        if self.used["requests"] >= self.limits["requests"]:
            raise BudgetExhausted(f"requests budget {self.limits['requests']} reached before {what}")
        if self.elapsed() >= self.limits["seconds"]:
            raise BudgetExhausted(f"seconds budget {self.limits['seconds']} reached before {what}")
        self.used["requests"] += 1

    @staticmethod
    def describe(snapshot):
        return ", ".join(f"{name} {used}" for name, used in snapshot.items())

    def snapshot(self):
        return {"boards": f"{self.used['boards']}/{self.limits['boards']}",
                "requests": f"{self.used['requests']}/{self.limits['requests']}",
                "seconds": f"{self.elapsed():.1f}/{self.limits['seconds']}"}
