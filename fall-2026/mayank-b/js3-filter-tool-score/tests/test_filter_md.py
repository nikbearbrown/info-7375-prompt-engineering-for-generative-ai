"""FILTER.md is the filter; config/filter.json is its machine copy. Changing one without the other fails here."""
import json
import re
import unittest

from helpers import HERE

MD = (HERE / "FILTER.md").read_text()
CFG = json.loads((HERE / "config/filter.json").read_text())


def section(start, end):
    return MD.split(start, 1)[1].split(end, 1)[0]


class FilterMatchesConfig(unittest.TestCase):
    def test_version(self):
        self.assertIn(f"**Version {CFG['version']} ·", MD)

    def test_role_words(self):
        rows = re.findall(r"^\| `([^`]+)` \|", section("### 1.1", "### 1.2"), re.M)
        self.assertEqual(rows, CFG["role_words_title"])

    def test_exclude_words(self):
        self.assertEqual(re.findall(r"`([^`]+)`", section("### 1.2", "Priya is early-career")), CFG["exclude_words_title"])

    def test_topic_words_and_forms(self):
        rows = re.findall(r"^\| `([^`]+)` \| ([^|]+) \|", section("### 1.4", "### 1.5"), re.M)
        self.assertEqual({w: [f.strip() for f in forms.split(",")] for w, forms in rows}, CFG["topic_words_text"])

    def test_threshold(self):
        self.assertIn(f"**T = {CFG['threshold_T']}**", section("### 1.5", "### 1.6"))

    def test_location(self):
        sec = section("### 1.3", "### 1.4")
        for x in [CFG["location"]["home"], *CFG["location"]["relocate"], *CFG["location"]["remote_us_pieces"]]:
            self.assertIn(x, sec)

    def test_ignore_lists(self):
        for board, words in CFG["ignore_words_by_board"].items():
            for w in words:
                self.assertRegex(section("### 1.6", "### 1.7"), rf"`{re.escape(w)}`.*{re.escape(board)}|{re.escape(board)}.*`{re.escape(w)}`")


if __name__ == "__main__":
    unittest.main()
