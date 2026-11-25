"""The shortlist's reply validator and build loop, with a CONSTRUCTED caller (no Claude call is made)."""
import json
import unittest

from agent import filter as filt, shortlist
from tests.jobs import PERSONA, SPEC, job

GOOD = {"claims": [
    {"about": "role", "claim": "A backend role", "quote": "Software Engineer, Backend"},
    {"about": "experience", "claim": "No years asked", "quote": ""},
    {"about": "location", "claim": "Remote in the US", "quote": "Remote, US"},
    {"about": "skills", "claim": "Uses Kafka", "quote": "Python, Kafka and Redis"}]}


def envelope(reply):
    return json.dumps({"type": "result", "result": reply if isinstance(reply, str) else json.dumps(reply)})


class Validator(unittest.TestCase):
    def test_good_reply(self):
        claims, _ = shortlist.parse_reply(envelope(GOOD))
        self.assertEqual(len(claims), 4)

    def test_prose_around_json_is_invalid(self):
        with self.assertRaises(shortlist.InvalidReply):
            shortlist.parse_reply(envelope("Here you go: " + json.dumps(GOOD)))

    def test_three_claims_is_invalid(self):
        with self.assertRaises(shortlist.InvalidReply):
            shortlist.parse_reply(envelope({"claims": GOOD["claims"][:3]}))

    def test_two_role_claims_is_invalid(self):
        bad = {"claims": GOOD["claims"][:1] * 2 + GOOD["claims"][2:]}
        with self.assertRaises(shortlist.InvalidReply):
            shortlist.parse_reply(envelope(bad))

    def test_extra_field_is_invalid(self):
        bad = {"claims": [dict(GOOD["claims"][0], score=9)] + GOOD["claims"][1:]}
        with self.assertRaises(shortlist.InvalidReply):
            shortlist.parse_reply(envelope(bad))


class Build(unittest.TestCase):
    def setUp(self):
        self.jobs = {"constructed:board:k1": job(id="k1"), "constructed:board:r1": job(id="r1", location="London, UK")}
        self.decisions = [filt.decide(j, "constructed:board", PERSONA, SPEC).to_dict() for j in self.jobs.values()]
        self.saved = []

    def run_build(self, reply):
        return shortlist.build(self.decisions, self.jobs, SPEC, PERSONA, "{title}", lambda k, t: self.saved.append(k),
                               caller=lambda prompt: envelope(reply))

    def test_only_kept_postings_are_asked_about(self):
        entries = self.run_build(GOOD)
        self.assertEqual([e["key"] for e in entries], ["constructed:board:k1"])

    def test_reply_saved_before_parsing_and_invalid_reply_not_fixed(self):
        entries = self.run_build("not json")
        self.assertEqual(self.saved, ["constructed:board:k1"])
        self.assertEqual((entries[0]["valid"], entries[0]["claims"]), (False, []))

    def test_empty_experience_quote_makes_the_machine_abstain(self):
        entry = self.run_build(GOOD)[0]
        self.assertTrue(entry["machine_abstains"])


if __name__ == "__main__":
    unittest.main()
