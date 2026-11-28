"""A variant changes one object and nothing else, and the change is undone afterwards.
Items here are CONSTRUCTED."""

import unittest

from jobwatch import screen, variants


def item(title, description, key):
    return screen.Item(board="greenhouse/anthropic", key=key, title=title, location="Seattle, WA",
                       description=description, captured_at="2026-11-24T22:36:19Z")


ITEMS = [item("Software Engineer", "<p>machine learning</p>", "1"), item("ML Engineer", "", "2"),
         item("Software Engineer", "<p>data platform</p>", "3")]


class VariantTest(unittest.TestCase):
    def test_only_the_named_object_changes_and_it_is_restored(self):
        before = variants.rescore(ITEMS)
        spec = {"name": "cut", "object": "description topics",
                "set": {"jobwatch.screen.DESCRIPTION_TOPICS": [t for t in screen.DESCRIPTION_TOPICS if t != "machine learning"]}}
        after = variants.rescore(ITEMS, spec)
        self.assertEqual((before[("greenhouse/anthropic", "1")]["fate"], after[("greenhouse/anthropic", "1")]["fate"]),
                         ("kept", "rejected"))
        for key in ("2", "3"):
            self.assertEqual(before[("greenhouse/anthropic", key)], after[("greenhouse/anthropic", key)])
        self.assertIn("machine learning", screen.DESCRIPTION_TOPICS)

    def test_a_setting_change(self):
        after = variants.rescore(ITEMS, {"name": "cutoff 3", "object": "setting", "set": {"jobwatch.screen.CUTOFF": 3}})
        self.assertEqual([after[("greenhouse/anthropic", k)]["fate"] for k in ("1", "2", "3")], ["rejected", "kept", "rejected"])
        self.assertEqual(screen.CUTOFF, 2)


if __name__ == "__main__":
    unittest.main()
