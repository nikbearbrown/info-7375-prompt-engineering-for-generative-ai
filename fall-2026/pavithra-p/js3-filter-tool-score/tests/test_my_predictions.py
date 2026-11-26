"""My own predictions, written before this test existed (2026-11-25, given in chat as "A keep, B reject, C keep").

Claude Code showed me three CONSTRUCTED postings; I predicted each verdict from my filter rules without running
anything, and only then was this test written to check them against filter v1.1 (and v1.0). Not a real posting.
"""
import unittest

from agent import config, filter as filt
from tests.jobs import PERSONA, job

CASES = {
    "A": (dict(title="Backend Engineer", location="Boston, MA (US)",
               content="<p>We use Java and Kafka. 2+ years of experience.</p>"), filt.KEEP),
    "B": (dict(title="Software Engineer", location="Austin, TX",
               content="<p>Python and Redis. 4 years of experience.</p>"), filt.REJECT),
    "C": (dict(title="Platform Engineer", location="Remote, US",
               content="<p>Kubernetes, Docker, Helm, AWS and Terraform.</p>"), filt.KEEP),
}


class MyPredictions(unittest.TestCase):
    def check(self, version):
        spec = filt.load_filter(config.ROOT / "filters" / f"{version}.json")
        for name, (posting, predicted) in CASES.items():
            with self.subTest(case=name, filter=version):
                self.assertEqual(filt.decide(job(id=name, **posting), "constructed:board", PERSONA, spec).verdict,
                                 predicted)

    def test_my_predictions_hold_for_v1_1(self):
        self.check("v1.1")

    def test_my_predictions_hold_for_v1_0(self):
        self.check("v1.0")


if __name__ == "__main__":
    unittest.main()
