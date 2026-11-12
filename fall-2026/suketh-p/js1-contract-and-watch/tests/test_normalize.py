"""Normalization exactly as CONTRACT.md 'The relevance rule' defines it. Constructed inputs."""

import unittest

from jobwatch import normalize
from tests.helpers import esc


class TokensTest(unittest.TestCase):
    def test_lowercases_and_splits_on_non_alphanumerics(self):
        self.assertEqual(
            normalize.tokens("Senior Software Engineer, Inference"),
            ["senior", "software", "engineer", "inference"],
        )

    def test_digits_stay_inside_their_token(self):
        self.assertEqual(normalize.tokens("python3 & C++"), ["python3", "c"])

    def test_characters_outside_a_to_z_split_words(self):
        self.assertEqual(normalize.tokens("Résumé"), ["r", "sum"])

    def test_adjacent_text_blocks_are_separated(self):
        # Without a separator these would merge into the single token "pythonsql".
        self.assertEqual(normalize.tokens(esc("<li>Python</li><li>SQL</li>")), ["python", "sql"])

    def test_entities_are_decoded_until_nothing_changes_then_markup_removed(self):
        # Double-escaped link: "python" exists only inside the href attribute,
        # which is markup, not text. One decoding pass would leave it as text.
        content = esc(esc('<a href="https://example.com/python">Apply</a> SQL'))
        self.assertEqual(normalize.tokens(content), ["apply", "sql"])


class ContainsPhraseTest(unittest.TestCase):
    def test_single_word_matches_a_whole_token_only(self):
        self.assertFalse(normalize.contains_phrase(["leadership"], "lead"))
        self.assertTrue(normalize.contains_phrase(["team", "lead"], "lead"))

    def test_phrase_needs_consecutive_tokens(self):
        self.assertFalse(normalize.contains_phrase(["new", "jersey", "york"], "new york"))
        self.assertTrue(normalize.contains_phrase(["new", "york", "city"], "new york"))


class PlainTextTest(unittest.TestCase):
    def test_keeps_case_and_collapses_whitespace(self):
        content = esc("<p>Hello <b>World</b></p>\n<p>Python &amp; SQL</p>")
        self.assertEqual(normalize.plain_text(content), "Hello World Python & SQL")


if __name__ == "__main__":
    unittest.main()
