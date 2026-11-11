"""Board names -> URLs. Written for the review packet BEFORE the patch (see review/REVIEW.md)."""

import tempfile
import unittest
from pathlib import Path

from jsagent2 import providers
from jsagent2.policy import Policy


class AshbyBoardNames(unittest.TestCase):
    def test_name_with_space_and_capitals_is_encoded(self):
        self.assertEqual(providers.url_for("ashby", "Jasper AI"),
                         "https://api.ashbyhq.com/posting-api/job-board/Jasper%20AI")

    def test_plain_names_unchanged(self):
        self.assertEqual(providers.url_for("ashby", "notion"), "https://api.ashbyhq.com/posting-api/job-board/notion")

    def test_name_cannot_change_the_path_or_query(self):
        # Loosening the rule must not let a board name walk the URL somewhere else.
        for bad in ["../x", "a/b", "..", ".", "a?b=1", "a#b", "a%2Fb", "a\\b", "", " ", "x" * 65, "a\nb"]:
            with self.subTest(name=bad):
                with self.assertRaises(ValueError):
                    providers.url_for("ashby", bad)

    def test_encoded_url_still_passes_policy(self):
        root = Path(tempfile.mkdtemp())
        url = providers.url_for("ashby", "Jasper AI")
        self.assertEqual(Policy(root).check_request("GET", url).verdict, "allow")


class GreenhouseBoardNames(unittest.TestCase):
    def test_greenhouse_rule_unchanged(self):
        # Out of scope for this change: Greenhouse names stay lowercase/digits/hyphen.
        self.assertEqual(providers.url_for("greenhouse", "stripe"), "https://boards-api.greenhouse.io/v1/boards/stripe/jobs")
        for bad in ["Stripe", "Jasper AI", "../x"]:
            with self.subTest(name=bad):
                with self.assertRaises(ValueError):
                    providers.url_for("greenhouse", bad)


if __name__ == "__main__":
    unittest.main()
