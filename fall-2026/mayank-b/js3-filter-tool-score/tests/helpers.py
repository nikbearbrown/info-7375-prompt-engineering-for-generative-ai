"""Shared test helpers: a disposable project root, a scripted fetch, a fake clock. No network."""
import json
import shutil
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "src"))

from jsa import net  # noqa: E402

PERSONA = json.loads((HERE / "persona/priya-nair.resume.json").read_text())
BUDGET = json.loads((HERE / "config/budgets.json").read_text())
RUN_ID = "2026-11-10T00-00-00Z-test"


def temp_root() -> Path:
    root = Path(tempfile.mkdtemp(prefix="js2-"))
    for d in ("config", "persona", "state", "runs"):
        (root / d).mkdir()
    shutil.copy(HERE / "config/expected-boards.json", root / "config/expected-boards.json")
    return root


def gh(*ids):
    return json.dumps({"jobs": [{"id": i, "title": f"ML Engineer {i}", "location": {"name": "Boston, MA"},
                                 "absolute_url": f"https://example.invalid/{i}"} for i in ids]}).encode()


def ashby(*ids):
    return json.dumps({"jobs": [{"id": f"a{i}", "title": f"Applied AI {i}", "location": "Remote",
                                 "jobUrl": f"https://example.invalid/a{i}"} for i in ids]}).encode()


class ScriptedFetch:
    """url-substring -> list of responses, consumed in order. A response is (status, bytes) or an Exception."""

    def __init__(self, script):
        self.script = {k: list(v) for k, v in script.items()}
        self.calls = []

    def __call__(self, url, timeout):
        self.calls.append(url)
        for k, seq in self.script.items():
            if k in url:
                r = seq.pop(0) if len(seq) > 1 else seq[0]
                if isinstance(r, Exception):
                    raise r
                return r
        raise AssertionError(f"unexpected url {url}")


class Clock:
    def __init__(self, step=0.0):
        self.t, self.step = 0.0, step

    def __call__(self):
        self.t += self.step
        return self.t


def plan(*pairs):
    return [{"ats": a, "slug": s} for a, s in pairs]


TIMEOUT = net.Timeout
