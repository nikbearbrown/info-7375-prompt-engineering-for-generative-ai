"""The hand-label sample: fixed seed, the sizes the procedure names, no posting in two groups,
and the held-out groups drawn before anything else. Records here are CONSTRUCTED."""

import unittest

from jobwatch import sample


def record(n, fate, score=3, reasons=()):
    return {"board": "greenhouse/anthropic", "key": str(n), "fate": fate, "score": score, "reasons": list(reasons)}


def corpus():
    records = [record(n, "kept", score=2 if n % 2 else 3) for n in range(60)]
    records += [record(100 + n, "rejected", score=1, reasons=["score"]) for n in range(100)]
    records += [record(300 + n, "rejected", score=0, reasons=["role", "score"]) for n in range(100)]
    return records


class SampleTest(unittest.TestCase):
    def test_sizes_and_no_overlap(self):
        members = sample.draw(corpus())
        self.assertEqual(len(members), sum(sample.SIZES.values()))
        self.assertEqual(len({(m["board"], m["key"]) for m in members}), len(members))
        for stratum, size in sample.SIZES.items():
            self.assertEqual(sum(m["stratum"] == stratum for m in members), size)

    def test_same_seed_same_sample_whatever_the_input_order(self):
        a = sample.draw(corpus())
        b = sample.draw(list(reversed(corpus())))
        self.assertEqual(a, b)

    def test_label_ids_do_not_follow_the_groups(self):
        members = sample.draw(corpus())
        first_ten = {m["stratum"] for m in members[:10]}
        self.assertGreater(len(first_ten), 1)
        self.assertEqual([m["label_id"] for m in members], [f"P{n:02d}" for n in range(1, len(members) + 1)])

    def test_held_out_is_drawn_first_so_later_groups_cannot_take_from_it(self):
        records = corpus()
        members = sample.draw(records)
        held = {m["key"] for m in members if m["stratum"].startswith("held-out")}
        # Redrawing only the held-out groups with the same seed gives the same postings.
        import random
        rng = random.Random(sample.SEED)
        kept = sorted((r for r in records if r["fate"] in ("kept", "review")), key=lambda r: (r["board"], r["key"]))
        rejected = sorted((r for r in records if r["fate"] == "rejected"), key=lambda r: (r["board"], r["key"]))
        expected = {r["key"] for r in rng.sample(kept, 15)}
        expected |= {r["key"] for r in rng.sample(rejected, 15)}
        self.assertEqual(held, expected)

    def test_close_calls_come_from_their_pools(self):
        members = sample.draw(corpus())
        keys = {m["key"]: m["stratum"] for m in members}
        for key, stratum in keys.items():
            n = int(key)
            if stratum == "audit at the cutoff":
                self.assertTrue(n < 60 and n % 2 == 1)          # kept with score 2
            if stratum == "audit one point under the cutoff":
                self.assertTrue(100 <= n < 200)                 # rejected only for score, score 1


if __name__ == "__main__":
    unittest.main()
