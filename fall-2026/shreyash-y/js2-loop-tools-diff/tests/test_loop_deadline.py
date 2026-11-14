"""Strict time budget, added 2026-11-10 after a second review (README "Known limitations of the
loop"). Written and committed BEFORE the loop change. The 120 s budget was checked before each
request, but the request itself could then run for its full 20 s timeout. A request started with
10 s left must be given at most 10 s. All responses here are CONSTRUCTED."""
import json
import pathlib
import tempfile
import unittest

from jsagent import loop, persona, policy, providers
from tests import fakes

URL = providers.board_url("greenhouse", "oscar")


class RecordingTransport(fakes.FakeTransport):
    def __init__(self, routes):
        super().__init__(routes)
        self.timeouts = []

    def get(self, url, timeout=20):
        self.timeouts.append(timeout)
        return super().get(url, timeout)


class StepClock:
    """Returns the given times in order, then repeats the last one."""
    def __init__(self, *times):
        self.times = list(times)

    def __call__(self):
        return self.times.pop(0) if len(self.times) > 1 else self.times[0]


class StrictDeadline(unittest.TestCase):
    def run_at(self, *times):
        with tempfile.TemporaryDirectory() as tmp:
            project = pathlib.Path(tmp).resolve()
            (project / "runs").mkdir()
            view = persona.public_view(json.loads((pathlib.Path(__file__).parent.parent / "persona" / "alex_morgan.json").read_text()))
            t = RecordingTransport({URL: [fakes.gh(1)]})
            rep = loop.run([{"name": "oscar", "ats": "greenhouse", "token": "oscar"}],
                           {"max_boards": 6, "max_requests": 12, "max_seconds": 120}, t,
                           policy.Files(project, project / "runs"), run_id="r", resume=view, clock=StepClock(*times))
            return t.timeouts, rep

    def test_request_gets_only_the_time_left(self):
        timeouts, rep = self.run_at(0, 110)          # start at 0; 110 s used when the request starts
        self.assertEqual(len(timeouts), 1)
        self.assertLessEqual(timeouts[0], 10)
        self.assertGreater(timeouts[0], 0)

    def test_plenty_of_time_keeps_the_normal_timeout(self):
        timeouts, _ = self.run_at(0, 1)
        self.assertEqual(timeouts, [20])


if __name__ == "__main__":
    unittest.main()
