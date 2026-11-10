"""Test doubles. Every response here is CONSTRUCTED for tests; real responses only come from
runs/<run_id>/raw/."""
import json


class FakeTransport:
    """routes: url -> list of responses used in order; each is (status, body_bytes) or an
    exception instance to raise. Records every call."""

    def __init__(self, routes):
        self.routes = {u: list(v) for u, v in routes.items()}
        self.calls = []

    def get(self, url, timeout=20):
        self.calls.append(url)
        queue = self.routes.get(url)
        if not queue:
            return 404, b'{"ok": false, "error": "Document not found"}'
        item = queue.pop(0) if len(queue) > 1 else queue[0]
        if isinstance(item, Exception):
            raise item
        return item


class FakeClock:
    def __init__(self, step=0.0):
        self.t, self.step = 0.0, step

    def __call__(self):
        self.t += self.step
        return self.t


def gh(*ids, total=None):
    jobs = [{"id": i, "title": "Software Engineer", "departments": [{"name": "Engineering"}],
             "location": {"name": "Boston, MA"}, "offices": [{"name": "Boston"}],
             "content": "&lt;p&gt;Python and SQL. 2+ years of experience.&lt;/p&gt;",
             "absolute_url": f"https://example.com/{i}"} for i in ids]
    return 200, json.dumps({"jobs": jobs, "meta": {"total": len(ids) if total is None else total}}).encode()


def ashby(*ids):
    jobs = [{"id": i, "title": "Software Engineer", "department": "Engineering", "team": "Platform",
             "location": "Boston, MA", "secondaryLocations": [], "isRemote": False, "workplaceType": "OnSite",
             "descriptionPlain": "Python and SQL. 2+ years of experience.", "jobUrl": f"https://example.com/{i}"}
            for i in ids]
    return 200, json.dumps({"apiVersion": "1", "jobs": jobs}).encode()


def lever(*ids):
    posts = [{"id": i, "text": "Software Engineer",
              "categories": {"department": "Engineering", "team": "Platform", "location": "Boston, MA",
                             "allLocations": ["Boston, MA"]},
              "workplaceType": "onsite", "descriptionPlain": "Python and SQL.",
              "lists": [{"text": "Requirements", "content": "<li>2+ years of experience</li>"}],
              "additionalPlain": "", "hostedUrl": f"https://example.com/{i}"} for i in ids]
    return 200, json.dumps(posts).encode()
