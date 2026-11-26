"""FILTER.md v1.2 is v1.1 plus exactly one adopted change (X2), and v1.1 is kept byte for byte.
Postings here are CONSTRUCTED."""
import json
import unittest

from helpers import J, P, ROOT, evaluate, rules, rules_v11
import experiment as X

# The sha256 of each rules file as recorded by the v1.1 run (runs/filter-v1.1-2026-11-18T212545Z/summary.json).
V11_HASHES = {
    "boilerplate.json": "8327bfe3e91a3ac43c82b5cff0319975ee0508d330ed9937e12644d050329916",
    "filter_rules.json": "080f6c90ed5e2c7353edaf8f9876437f2fca5d06d814de65e838abc0794490c9",
    "us_locations.json": "8fbadc763851074be5198e1a74b378364f068ff40743033e2131f38447543d7d",
}
ONE_TOPIC = "<p>You will build data pipelines.</p><p>Python and SQL on AWS.</p>"
TWO_TOPICS = "<p>You will build data pipelines and machine learning models.</p><p>Python and SQL on AWS.</p>"


class Archive(unittest.TestCase):
    def test_v11_rules_are_kept_byte_for_byte(self):
        for name, want in V11_HASHES.items():
            with self.subTest(name=name):
                self.assertEqual(P.sha256(J.rules_dir_for("1.1") / name), want)

    def test_versions_resolve_to_their_folders(self):
        self.assertEqual(J.rules_dir_for("1.2"), J.RULES_DIR)
        self.assertEqual(J.rules_dir_for("1.1"), J.RULES_DIR / "v1.1")
        with self.assertRaises(ValueError):
            J.rules_dir_for("0.9")


class ExactlyOneChange(unittest.TestCase):
    def test_v12_differs_from_v11_only_in_the_adopted_value(self):
        new = X.leaves(rules()["filter"])
        old = X.leaves(rules_v11()["filter"])
        diff = {k for k in set(new) | set(old) if new.get(k) != old.get(k)}
        self.assertEqual(diff, {("version",), ("_comment",), ("titles", "related_min_topics")})
        self.assertEqual((old.get(("version",)), new[("version",)]), ("1.1", "1.2"))
        self.assertEqual(new[("titles", "related_min_topics")], 2)

    def test_the_other_rules_files_are_unchanged(self):
        for name in ("boilerplate.json", "us_locations.json"):
            with self.subTest(name=name):
                self.assertEqual(P.sha256(J.RULES_DIR / name), V11_HASHES[name])

    def test_v12_is_v11_with_change_x2_applied(self):
        x2 = next(c for c in json.loads((ROOT / "experiments" / "candidates.json").read_text(encoding="utf-8"))["changes"]
                  if c["id"].startswith("X2"))
        applied = X.apply_change(rules_v11(), x2)["filter"]
        current = rules()["filter"]
        strip = lambda f: {k: v for k, v in X.leaves(f).items() if k not in (("version",), ("_comment",))}
        self.assertEqual(strip(applied), strip(current))

    def test_rejected_and_deferred_changes_were_not_applied(self):
        f = rules()["filter"]
        self.assertEqual(f["scoring"]["threshold"], 65)  # X1 rejected
        self.assertNotIn("may also have", f["experience"]["preferred_heading_words"])  # X3 not adopted


class RelatedRoleRule(unittest.TestCase):
    def test_v12_needs_two_topic_categories_for_a_related_title(self):
        one = evaluate(title="Software Engineer, Payments", body=ONE_TOPIC)
        self.assertEqual((one["role"], one["decision"]), ("none", "rejected"))
        self.assertIn("no matching role", one["hard_exclusions"])
        two = evaluate(title="Software Engineer, Payments", body=TWO_TOPICS)
        self.assertEqual(two["role"], "related")

    def test_v11_accepted_one_topic(self):
        self.assertEqual(evaluate(title="Software Engineer, Payments", body=ONE_TOPIC, rules=rules_v11())["role"], "related")

    def test_target_titles_are_not_affected(self):
        self.assertEqual(evaluate(title="Data Engineer", body=ONE_TOPIC)["role"], "target")


if __name__ == "__main__":
    unittest.main()
