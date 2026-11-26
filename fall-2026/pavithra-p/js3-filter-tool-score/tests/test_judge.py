"""Claude as a second scorer (agent/judge.py): the context builder, the reply validator and the score. CONSTRUCTED."""
import json
import unittest

from agent import judge
from tests.jobs import job


def envelope(reply):
    return json.dumps({"result": reply if isinstance(reply, str) else json.dumps(reply)})


class Context(unittest.TestCase):
    def test_title_context_has_no_description(self):
        text = judge.posting_context(job(content="<p>Secret detail</p>"), "title")
        self.assertIn("Title: Software Engineer, Backend", text)
        self.assertNotIn("Secret detail", text)

    def test_full_context_has_the_description(self):
        self.assertIn("Secret detail", judge.posting_context(job(content="<p>Secret detail</p>"), "full"))

    def test_the_prompt_is_the_same_apart_from_the_posting(self):
        a = judge.build_prompt("A {posting} B", job(), "title")
        self.assertTrue(a.startswith("A Title:") and a.endswith(" B"))


class Parse(unittest.TestCase):
    def test_good_reply(self):
        self.assertEqual(judge.parse(envelope({"verdict": "no", "reason": "senior role"})), ("no", "senior role"))

    def test_other_verdict_or_extra_field_or_prose_is_invalid(self):
        for bad in ({"verdict": "maybe", "reason": "x"}, {"verdict": "yes", "reason": "x", "score": 1}, "Sure! yes"):
            with self.assertRaises(judge.InvalidVerdict):
                judge.parse(envelope(bad))


class Score(unittest.TestCase):
    def test_false_keeps_false_rejects_and_invalid(self):
        labels = {"a": ("yes", ""), "b": ("no", ""), "c": ("no", ""), "d": ("cannot tell", "")}
        s = judge.score({"a": None, "b": "yes", "c": "no", "d": "yes"}, labels)
        self.assertEqual((s["judged"], s["agree"], s["false_keeps"], s["false_rejects"], s["invalid"]),
                         (3, 1, ["b"], ["a"], 1))


if __name__ == "__main__":
    unittest.main()
