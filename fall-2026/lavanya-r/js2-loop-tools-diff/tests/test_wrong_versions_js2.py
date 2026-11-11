"""GATE.md section 6: each plausible-but-wrong version is BUILT here, and the
same property our real tests rely on is shown to catch it. If a property
passed a wrong version, it would be a weak test."""

import shutil
import unittest
import urllib.parse
from unittest import mock

from agent import loop
from agent.policy import ALLOWED_HOSTS
from tests.boundary_cases import CASES, sandbox
from tests.loop_fakes import LIMITS, TIMEOUT, FakeClock, FakeNet, ashby, gh, \
    lever, url

GH, LV, AS = "greenhouse", "lever", "ashby"
THREE = [{"ats": GH, "board": "acme"}, {"ats": LV, "board": "beta"},
         {"ats": AS, "board": "gamma"}]


# ---------- the properties ----------

def empty_board_is_flagged(report):
    return all(b["status"] != "ok" and b["new_count"] is None
               for b in report["boards"] if b["jobs"] == 0)


def host_check_is_exact(allowed):
    """allowed(url) -> bool must refuse every look-alike and off-list host in
    the boundary cases and accept the real one."""
    cases = [(t, exp) for n, op, t, exp in CASES if op == "url"] + [
        ("https://evilgreenhouse.io/v1/boards/x/jobs", "refuse"),
        ("https://greenhouse.io.evil.example/", "refuse")]
    return all(allowed(t) == (exp == "allow") for t, exp in cases)


def requests_within_budget(net_calls, limits):
    return len(net_calls) <= limits["requests"]


# ---------- the wrong versions ----------

def wrong_contains_host_check(u):
    return any(h.split(".", 1)[1] in u for h in ALLOWED_HOSTS)


def right_host_check(u):
    p = urllib.parse.urlsplit(u)
    return p.scheme == "https" and p.hostname in ALLOWED_HOSTS


class WrongBudget(loop.Budget):
    """Counts boards but not retries: the second attempt is free."""

    def take_request(self):
        self._time()
        if self.requests >= self.limits["requests"]:
            raise loop.BudgetExhausted("requests", self.requests,
                                       self.limits["requests"])
        if not getattr(self, "_in_retry", False):
            self.requests += 1
        self._in_retry = not getattr(self, "_in_retry", False)


REAL_CLASSIFY = loop.classify


def wrong_classify(ats, resp):
    status, reason, postings = REAL_CLASSIFY(ats, resp)
    if status == "suspicious_empty":
        return "ok", "0 jobs", postings          # a quiet day, it says
    return status, reason, postings


class Base(unittest.TestCase):
    def setUp(self):
        self.tmp, self.policy, _ = sandbox()

    def tearDown(self):
        shutil.rmtree(self.tmp)

    def go(self, answers, limits=LIMITS):
        self.net = FakeNet(self.policy, answers, FakeClock())
        r, _ = loop.run(THREE, policy=self.policy, get=self.net.get,
                        limits=dict(limits), clock=FakeClock(),
                        sleep=lambda s: None, stamp="W", kind="test")
        return r


class TestWrongVersion1EmptyIsQuiet(Base):
    answers = staticmethod(lambda: {url(GH, "acme"): [(200, gh(1))],
                                    url(LV, "beta"): [(200, lever(1))],
                                    url(AS, "gamma"): [(200, b'{"jobs":[]}')]})

    def test_real_code_passes(self):
        self.assertTrue(empty_board_is_flagged(self.go(self.answers())))

    def test_wrong_version_is_caught(self):
        with mock.patch.object(loop, "classify", wrong_classify):
            r = self.go(self.answers())
        self.assertEqual(r["exit"], "finished")         # looks clean ...
        self.assertFalse(empty_board_is_flagged(r))     # ... and is caught


class TestWrongVersion2ContainsHostCheck(unittest.TestCase):
    def test_right_check_passes(self):
        self.assertTrue(host_check_is_exact(right_host_check))

    def test_wrong_version_is_caught(self):
        self.assertTrue(wrong_contains_host_check(
            "https://boards-api.greenhouse.io.evil.example/v1/boards/x/jobs"))
        self.assertFalse(host_check_is_exact(wrong_contains_host_check))


class TestWrongVersion3RetriesSkipBudget(Base):
    answers = staticmethod(lambda: {url(GH, "acme"): [TIMEOUT, TIMEOUT],
                                    url(LV, "beta"): [TIMEOUT, TIMEOUT],
                                    url(AS, "gamma"): [(200, ashby(1))]})
    limits = {**LIMITS, "requests": 3}

    def test_real_code_passes(self):
        self.go(self.answers(), self.limits)
        self.assertTrue(requests_within_budget(self.net.calls, self.limits))

    def test_wrong_version_is_caught(self):
        with mock.patch.object(loop, "Budget", WrongBudget):
            self.go(self.answers(), self.limits)
        self.assertFalse(requests_within_budget(self.net.calls, self.limits))


if __name__ == "__main__":
    unittest.main()
