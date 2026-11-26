import json
import os
import re
import unittest

from js3 import scorer

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _read(*parts, mode="r"):
    with open(os.path.join(BASE, *parts), mode, **({} if "b" in mode else {"encoding": "utf-8"})) as f:
        return f.read()


class FilterDocAgrees(unittest.TestCase):
    """FILTER.md and the JSON in force must say the same thing."""

    def setUp(self):
        self.doc = _read("FILTER.md")
        self.cfg = scorer.load_filter()

    def test_current_version_is_stated(self):
        self.assertIn(f"**Current version: {self.cfg['version']}**", self.doc)

    def test_every_word_list_entry_is_in_the_doc(self):
        for key in ("excluded_title_words", "role_phrases", "non_software_phrases", "seniority_words",
                    "entry_phrases", "requirement_headings", "end_headings"):
            for w in self.cfg[key]:
                self.assertIn(f"`{w}`", self.doc, f"{key}: {w!r} missing from FILTER.md")

    def test_every_weight_is_in_the_doc(self):
        for k, v in self.cfg["weights"].items():
            rule = k.split("_")[0]
            shown = f"{v:+.1f}" if isinstance(v, float) and k != "K2_unshipped_skill" else str(v)
            pat = {"K1_cap": "at most 8", "K2_unshipped_skill": "+0.25"}.get(k, shown).replace("-", "−")
            self.assertTrue(pat in self.doc or shown in self.doc, f"{k}={v} not in FILTER.md")
        self.assertIn(f"score ≥ {self.cfg['threshold']}", self.doc)

    def test_every_version_has_a_change_log_row(self):
        for f in os.listdir(os.path.join(BASE, "filter")):
            m = re.match(r"filter-v([\d.]+)\.json$", f)
            if m:
                self.assertRegex(self.doc, r"\| " + re.escape(m.group(1)) + r" \| 2026-", f"no change-log row for v{m.group(1)}")

    def test_frozen_v1_0_is_unchanged_from_its_recorded_hash(self):
        import hashlib
        tl = _read("evidence", "TIMELINE.md")
        h = hashlib.sha256(_read("evidence", "FILTER-v1.0-frozen.md", mode="rb")).hexdigest()
        self.assertIn(h[:16], tl)


if __name__ == "__main__":
    unittest.main()
