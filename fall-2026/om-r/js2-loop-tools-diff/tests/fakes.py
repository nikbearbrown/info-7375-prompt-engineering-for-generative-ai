"""Offline test doubles. Every response here is a CONSTRUCTED fixture, not
real board data; nothing in the test suite touches the network."""
import io
import json
import urllib.error


def greenhouse_body(*ids):
    return json.dumps({
        "jobs": [{"id": i, "title": f"Job {i}", "absolute_url": f"https://example.invalid/{i}"} for i in ids],
        "meta": {"total": len(ids)},
    }).encode()


def lever_body(*ids):
    return json.dumps([{"id": i, "text": f"Job {i}", "hostedUrl": f"https://example.invalid/{i}"} for i in ids]).encode()


def http_error(url, code, reason):
    return urllib.error.HTTPError(url, code, reason, hdrs=None, fp=io.BytesIO(b""))


class FakeFetch:
    """Callable with the same signature as agent.fetch.fetch(url, timeout=...).

    `routes` maps a substring of the URL (e.g. "/boards/gitlab/") to either a
    list of outcomes consumed in order, or a single outcome reused forever.
    An outcome is bytes (returned) or an exception instance (raised).

    `calls` is the ground truth of how many requests the loop really made -
    independent of anything the loop says about itself."""

    def __init__(self, routes):
        self.routes = {k: (list(v) if isinstance(v, list) else v) for k, v in routes.items()}
        self.calls = []

    def __call__(self, url, timeout=None):
        self.calls.append(url)
        for key, outcome in self.routes.items():
            if key in url:
                if isinstance(outcome, list):
                    outcome = outcome.pop(0)
                if isinstance(outcome, BaseException):
                    raise outcome
                return outcome
        raise AssertionError(f"FakeFetch: no route for {url}")
