"""W4 guard: the hand labels (audit + held-out) were committed with their hash BEFORE any measurement or v1.1 change.

If someone edits a label after seeing results (for example to make a tuned threshold look better), this fails.
"""

import hashlib
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


class HeldOutFrozen(unittest.TestCase):
    def test_labels_match_committed_hash(self):
        want = (ROOT / "audit" / "hand-labels.sha256").read_text().split()[0]
        got = hashlib.sha256((ROOT / "audit" / "hand-labels.json").read_bytes()).hexdigest()
        self.assertEqual(got, want, "hand-labels.json changed after its hash was committed")

    def test_every_sampled_item_is_labeled(self):
        labels = json.loads((ROOT / "audit" / "hand-labels.json").read_text())["labels"]
        items = json.loads((ROOT / "audit" / "sample.json").read_text())["items"]
        self.assertEqual(sorted(int(k) for k, v in labels.items() if v.get("verdict")), [i["item"] for i in sorted(items, key=lambda i: i["item"])])


if __name__ == "__main__":
    unittest.main()
