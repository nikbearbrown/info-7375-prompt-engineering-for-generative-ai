"""Example-list topic hits (relevance is not entailment) and the before-initialize probe finding."""
import json
import unittest

from jobfilter.preinit_probe import answered_before_initialize
from jobfilter.serve_tool import build_server
from jobfilter.such_as import analyse, is_example_hit


def hit(alias, snippet):
    return {"alias": alias, "snippet": snippet}


class ExampleLists(unittest.TestCase):
    def test_item_in_such_as_list_is_flagged(self):
        self.assertTrue(is_example_hit(hit("redis", "task/event systems such as celery, kafka, sqs, rabbitmq, or redis. you")))

    def test_plain_requirement_is_not_flagged(self):
        self.assertFalse(is_example_hit(hit("python", "you are proficient in python and have experience with")))

    def test_next_bullet_after_list_is_not_flagged(self):
        # line breaks are lost in saved text; "docker" starts a new bullet, it is not in the such-as list
        self.assertFalse(is_example_hit(hit("docker", "technologies such as kafka, cassandra, elasticsearch and spark docker and kubernetes")))

    def test_sentence_break_ends_the_list(self):
        self.assertFalse(is_example_hit(hit("java", "tools such as git. we write java every day")))

    def test_alias_missing_from_snippet_is_not_flagged(self):
        self.assertFalse(is_example_hit(hit("redis", "such as celery, kafka")))

    def test_top_keep_klaviyo_rests_on_example_lists(self):
        row = next(r for r in analyse("v1.0") if r["key"] == "greenhouse/klaviyo/8041054003")
        self.assertEqual((row["score"], row["example_groups"]), (8, ["Kubernetes", "Redis"]))
        self.assertEqual((row["score_without"], row["groups_without"], row["would_keep"]), (6, 1, False))

    def test_committed_counts(self):
        rows = analyse("v1.0")
        self.assertEqual(len(rows), 18)
        self.assertEqual(sum(1 for r in rows if r["example_groups"]), 13)
        self.assertEqual(sum(1 for r in rows if not r["would_keep"]), 7)


class BeforeInitialize(unittest.TestCase):
    def test_own_server_answers_tools_list_before_initialize(self):
        # recorded finding, not desired behavior: server 1.1.0 does not enforce the MCP lifecycle
        s = build_server()
        reply = json.loads(s.handle_line('{"jsonrpc":"2.0","id":1,"method":"tools/list"}'))
        self.assertFalse(s.initialized)
        self.assertTrue(answered_before_initialize(reply))

    def test_helper_treats_errors_and_timeouts_as_not_answered(self):
        self.assertFalse(answered_before_initialize({"jsonrpc": "2.0", "id": 1, "error": {"code": -32002}}))
        self.assertFalse(answered_before_initialize({"timeout": "no reply"}))


if __name__ == "__main__":
    unittest.main()
