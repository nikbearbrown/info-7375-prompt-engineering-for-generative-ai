"""CONSTRUCTED test responses (not real board data) and a fake network/clock
for the loop tests. Nothing here touches the internet."""

import json

from agent import net, providers

LIMITS = {"boards": 10, "requests": 20, "seconds": 120,
          "request_timeout_seconds": 20, "retry_wait_seconds": 2}


def gh(*ids):
    return json.dumps({"jobs": [{"id": int(i), "title": f"Job {i}",
                                 "location": {"name": "Boston, MA"},
                                 "absolute_url": f"https://x/{i}"}
                                for i in ids]}).encode()


def lever(*ids):
    return json.dumps([{"id": f"lv-{i}", "text": f"Job {i}",
                        "categories": {"location": "Remote"},
                        "hostedUrl": f"https://x/{i}"} for i in ids]).encode()


def ashby(*ids):
    return json.dumps({"jobs": [{"id": f"as-{i}", "title": f"Job {i}",
                                 "location": "NYC", "jobUrl": f"https://x/{i}"}
                                for i in ids]}).encode()


TIMEOUT = object()


class FakeNet:
    """answers[url] = list of answers, one per attempt: (status, body) or
    TIMEOUT. Records every call."""

    def __init__(self, policy, answers, clock=None, per_request=0.0):
        self.policy, self.answers, self.calls = policy, answers, []
        self.clock, self.per_request = clock, per_request

    def get(self, url, timeout):
        self.policy.check_url(url)            # the real get does this too
        self.calls.append(url)
        if self.clock:
            self.clock.advance(self.per_request)
        seq = self.answers[url]
        ans = seq.pop(0) if len(seq) > 1 else seq[0]
        if ans is TIMEOUT:
            raise net.Timeout("fake timeout")
        return net.Response(*ans)


class FakeClock:
    def __init__(self):
        self.now = 0.0

    def __call__(self):
        return self.now

    def advance(self, s):
        self.now += s


def url(ats, board):
    return providers.url_for(ats, board)
