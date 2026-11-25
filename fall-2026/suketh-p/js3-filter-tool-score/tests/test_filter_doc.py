"""The document is the filter: every word list and number in jobwatch/screen.py must appear in
FILTER.md as written. If someone edits one without the other, this test fails."""

import unittest
from pathlib import Path

from jobwatch import location, screen

FILTER_MD = (Path(__file__).resolve().parent.parent / "FILTER.md").read_text(encoding="utf-8")


def series(words, last="or"):
    """'a, b, or c' as FILTER.md writes a list."""
    words = list(words)
    return ", ".join(words[:-1]) + f", {last} " + words[-1] if len(words) > 2 else f" {last} ".join(words)


class FilterDocumentTest(unittest.TestCase):
    def test_word_lists_appear_in_filter_md(self):
        for words in (screen.LEVEL_WORDS, screen.TITLE_TOPICS, screen.DESCRIPTION_TOPICS):
            with self.subTest(words=words):
                self.assertIn(series(words), FILTER_MD)
        self.assertIn("Require " + series(screen.ROLE_WORDS) + " in the title.", FILTER_MD)

    def test_numbers_appear_in_filter_md(self):
        self.assertIn(f"Give a matching title {screen.ROLE_POINTS} point.", FILTER_MD)
        self.assertIn(f"Add {screen.TITLE_TOPIC_POINTS} points for", FILTER_MD)
        self.assertIn(f"add {screen.DESCRIPTION_TOPIC_POINTS} point for", FILTER_MD)
        self.assertIn(f"score at least {screen.CUTOFF}.", FILTER_MD)
        self.assertIn(screen.FILTER_VERSION, FILTER_MD)

    def test_the_v0_2_threshold_appears_in_filter_md(self):
        import json
        v02 = json.loads((Path(__file__).resolve().parent.parent / "variants" / "v0.2-experience-minimum.json")
                         .read_text(encoding="utf-8"))
        years = v02["set"]["jobwatch.screen.EXPERIENCE_MINIMUM_YEARS"]
        self.assertIn(f"a minimum of {years}+ years that is not marked preferred", FILTER_MD)
        self.assertIn(v02["set"]["jobwatch.screen.FILTER_VERSION"], FILTER_MD)

    def test_the_us_country_words_are_the_ones_the_chosen_option_names(self):
        self.assertIn("United States, USA, US or U.S.", FILTER_MD)
        self.assertEqual(location.US_COUNTRY_WORDS, ("united states", "usa", "us", "u s"))


if __name__ == "__main__":
    unittest.main()
