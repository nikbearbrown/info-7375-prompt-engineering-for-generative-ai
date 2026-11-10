"""Run budgets (GATE "Loop, budgets, and exits"; F8, F10, F11).

The clock and sleep are injectable so tests drive time with a fake clock. Every check
returns the name of the limit that blocks ("attempts" or "network-window"), or None.
"""

import time

from .limits import (ATTEMPT_CAP_SECONDS, MAX_HTTP_ATTEMPTS, NETWORK_WINDOW_SECONDS,
                     RETRY_MIN_ATTEMPT_SECONDS, RETRY_MIN_NETWORK_SECONDS, RETRY_WAIT_SECONDS)

ATTEMPTS = "attempts"
NETWORK_WINDOW = "network-window"


class Budget:
    def __init__(self, clock=time.monotonic, sleep=time.sleep):
        self.clock = clock
        self.sleep = sleep
        self.start = clock()
        self.network_deadline = self.start + NETWORK_WINDOW_SECONDS
        self.attempts_used = 0

    def elapsed(self) -> float:
        return self.clock() - self.start

    def network_remaining(self) -> float:
        return self.network_deadline - self.clock()

    def attempts_left(self) -> int:
        return MAX_HTTP_ATTEMPTS - self.attempts_used

    # ---------- first attempt of a board ----------

    def check_attempt(self) -> str | None:
        """May a new board's first attempt start? Needs a request left and an open window."""
        if self.attempts_left() <= 0:
            return ATTEMPTS
        if self.network_remaining() <= 0:
            return NETWORK_WINDOW
        return None

    def attempt_timeout(self) -> float:
        """F10: the smaller of 10 seconds and the time left in the network window."""
        return max(0.0, min(ATTEMPT_CAP_SECONDS, self.network_remaining()))

    def record_attempt(self) -> None:
        """Count one transport call (F8). Called immediately before the transport runs."""
        if self.attempts_left() <= 0:
            raise RuntimeError("attempt budget already exhausted")
        self.attempts_used += 1

    # ---------- the single retry (F11) ----------

    def check_retry_before_wait(self) -> str | None:
        """A request must remain and at least 2 s of network time: 1 s wait + 1 s attempt."""
        if self.attempts_left() <= 0:
            return ATTEMPTS
        if self.network_remaining() < RETRY_MIN_NETWORK_SECONDS:
            return NETWORK_WINDOW
        return None

    def wait_for_retry(self) -> None:
        self.sleep(RETRY_WAIT_SECONDS)

    def check_retry_after_wait(self) -> str | None:
        """Recheck after the wait: a request must remain and at least 1 s of attempt time."""
        if self.attempts_left() <= 0:
            return ATTEMPTS
        if self.network_remaining() < RETRY_MIN_ATTEMPT_SECONDS:
            return NETWORK_WINDOW
        return None
