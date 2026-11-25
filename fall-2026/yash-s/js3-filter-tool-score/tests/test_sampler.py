"""The reject-audit sampler is reproducible and never draws a posting twice.
The records here are CONSTRUCTED."""
import random
import unittest

import helpers  # noqa: F401  (puts the project folder on sys.path)
import sample_audit as S


def recs(n, board="OpenAI"):
    return [{"board": board, "id": str(i), "score": i % 100, "decision": "rejected"} for i in range(n)]


class Sampler(unittest.TestCase):
    def test_same_seed_gives_the_same_sample_whatever_the_input_order(self):
        pop = recs(200)
        a, _ = S.draw(random.Random(7), pop, 30, set())
        b, _ = S.draw(random.Random(7), list(reversed(pop)), 30, set())
        self.assertEqual([S.key(r) for r in a], [S.key(r) for r in b])
        self.assertEqual(len(a), 30)

    def test_already_drawn_postings_are_not_drawn_again(self):
        pop, taken = recs(40), set()
        first, _ = S.draw(random.Random(1), pop, 30, taken)
        second, pool = S.draw(random.Random(1), pop, 30, taken)
        self.assertEqual(pool, 10)
        self.assertFalse({S.key(r) for r in first} & {S.key(r) for r in second})

    def test_hand_fields_are_the_four_blank_columns(self):
        self.assertEqual(S.HAND_FIELDS, ["MY_VERDICT", "MY_REASON", "FALSE_FRIEND_WORD", "MY_NOTES"])


if __name__ == "__main__":
    unittest.main()
