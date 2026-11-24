"""FILTER.md 'The evidence rules' as tests, written before jobwatch/evidence.py existed.

The 'five years preferred' case is the student's fourth wrong version, word for word:
'Treat an exact quote as sufficient evidence. A posting says "Five years preferred." The claim
"Five years are required" must come back contradicted.' Everything here is CONSTRUCTED."""

import unittest

from jobwatch import evidence

POSTING = "<p>Five years preferred.</p><p>We sponsor H-1B visas for this role.</p>"


class QuoteCheckTest(unittest.TestCase):
    def test_a_quote_is_found_only_word_for_word_in_the_saved_text(self):
        text = evidence.plain(POSTING)
        self.assertTrue(evidence.quote_found(text, "Five years preferred."))
        self.assertTrue(evidence.quote_found(text, "five  years\npreferred"))   # case and spacing only
        self.assertFalse(evidence.quote_found(text, "Five years required."))   # one word changed
        self.assertFalse(evidence.quote_found(text, ""))

    def test_the_quote_check_names_what_it_checked(self):
        result = evidence.check_quote(evidence.plain(POSTING), "Five years preferred.")
        self.assertEqual(result, "quote found")
        self.assertEqual(evidence.check_quote(evidence.plain(POSTING), "Ten years preferred."), "quote not found")
        self.assertEqual(evidence.check_quote(evidence.plain(POSTING), None), "no quote")


class LabelTest(unittest.TestCase):
    def test_wv4_an_exact_quote_is_not_sufficient_evidence(self):
        # The claim "Five years are required", quoted with "Five years preferred.", must come back
        # contradicted: the quote check passes, and only the person's label decides.
        check = evidence.check_quote(evidence.plain(POSTING), "Five years preferred.")
        self.assertEqual(check, "quote found")
        self.assertEqual(evidence.final_label(human_label="contradicted", quote_check=check), "contradicted")

    def test_an_unlabelled_claim_stays_not_reviewed_even_with_a_found_quote(self):
        # "Not reviewed: The agent found a potential quote and I still need to check its meaning."
        self.assertEqual(evidence.final_label(human_label=None, quote_check="quote found"), "not reviewed")

    def test_only_the_four_labels_are_accepted(self):
        for label in ("supported", "contradicted", "insufficient", "not reviewed"):
            self.assertEqual(evidence.final_label(human_label=label, quote_check="quote found"), label)
        with self.assertRaises(ValueError):
            evidence.final_label(human_label="probably", quote_check="quote found")

    def test_silence_on_sponsorship_is_said_in_the_students_words(self):
        # "If the posting is silent about sponsorship, the agent says 'I cannot tell whether this
        # role offers sponsorship.'"
        self.assertEqual(evidence.CANNOT_TELL_SPONSORSHIP, "I cannot tell whether this role offers sponsorship.")


if __name__ == "__main__":
    unittest.main()
