"""Review packet (A): the time budget must not be overrun.

Spec, confirmed by me on 2026-11-10 before the patch: no request may run past the
60-second budget. Each request's timeout must be at most the time left in the budget.
If less than 1 second remains, the loop stops with budget_exhausted before sending.

Drafted by Claude Code from that spec; written and committed before the patch.
"""
import unittest

from agent2 import loop
from agent2.loop import Budget
from tests.fakes import FIGMA, SPOTIFY, FakeClock, FakeTransport, gh, lever, no_save


def recording_transport(clock, seconds_per_request):
    class Recording(FakeTransport):
        def __init__(self, script):
            super().__init__(script)
            self.timeouts = []

        def get(self, url, timeout):
            self.timeouts.append(timeout)
            clock.sleep(seconds_per_request)
            return super().get(url, timeout)
    return Recording({FIGMA.url: [gh(1)], SPOTIFY.url: [lever(1)]})


class TimeBudgetCannotBeOverrun(unittest.TestCase):
    def test_timeout_never_exceeds_time_left(self):
        clock = FakeClock()
        t = recording_transport(clock, seconds_per_request=50)   # after the first request, 10 s remain
        loop.run_loop([FIGMA, SPOTIFY], t, {}, Budget(max_seconds=60), no_save, clock=clock, sleep=clock.sleep)
        self.assertEqual(len(t.timeouts), 2)
        self.assertLessEqual(t.timeouts[1], 10, f"second request was given {t.timeouts[1]} s with only 10 s left")

    def test_stops_before_sending_when_under_one_second_left(self):
        clock = FakeClock()
        t = recording_transport(clock, seconds_per_request=59.5)  # 0.5 s left after the first request
        r = loop.run_loop([FIGMA, SPOTIFY], t, {}, Budget(max_seconds=60), no_save, clock=clock, sleep=clock.sleep)
        self.assertEqual(len(t.timeouts), 1, "a request was sent with under 1 s of budget left")
        self.assertEqual((r.exit, r.not_attempted), ("budget_exhausted", [SPOTIFY.key]))


if __name__ == "__main__":
    unittest.main()
