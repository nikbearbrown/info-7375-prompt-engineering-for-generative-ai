"""Parsers for the three systems, and the code's numbers against GATE.md."""
import os
import re
import unittest

from helpers import ROOT, ashby_body, gh_body, lever_body

import adapters
import loop
import policy

GATE = open(os.path.join(ROOT, "GATE.md"), encoding="utf-8").read()


class Parsers(unittest.TestCase):
    def test_each_system_parses_to_the_same_shape(self):
        for system, body in (("greenhouse", gh_body(7)), ("ashby", ashby_body(7)), ("lever", lever_body(7))):
            with self.subTest(system=system):
                [p] = adapters.parse({"system": system}, body)
                self.assertEqual(set(p), {"id", "title", "location", "url"})
                self.assertEqual(p["id"], "7")

    def test_ashby_plain_text_404_body_is_a_parse_error(self):
        with self.assertRaises(adapters.ParseError):
            adapters.parse({"system": "ashby"}, b"Not Found")

    def test_wrong_shapes_are_parse_errors_never_empty_lists(self):
        for system, body in (("greenhouse", b'{"meta": {}}'), ("ashby", b'[]'), ("lever", b'{"ok": false}'),
                             ("greenhouse", b'{"jobs": [{"title": "no id"}]}')):
            with self.subTest(system=system, body=body), self.assertRaises(adapters.ParseError):
                adapters.parse({"system": system}, body)

    def test_board_tokens_must_be_plain_names(self):
        for token in ("abacus/../x", "a?b=c", "", "UPPER", "a b"):
            with self.subTest(token=token), self.assertRaises(ValueError):
                adapters.board_url({"system": "greenhouse", "token": token})


class GateNumbers(unittest.TestCase):
    """A budget changes only by a dated GATE.md entry: the code must match the file."""

    def number(self, pattern):
        return int(re.search(pattern, GATE).group(1))

    def test_budgets_match_gate(self):
        self.assertEqual(loop.BUDGETS["boards"], self.number(r"\*\*Boards:\*\* at most (\d+)"))
        self.assertEqual(loop.BUDGETS["requests"], self.number(r"\*\*HTTP requests:\*\* at most (\d+)"))
        self.assertEqual(loop.BUDGETS["seconds"], self.number(r"\*\*Time:\*\* at most (\d+) seconds"))

    def test_retry_delay_and_size_limit_match_gate(self):
        self.assertEqual(loop.RETRY_DELAY, self.number(r"retry once after (\d+) seconds"))
        self.assertEqual(policy.MAX_WRITE_BYTES, self.number(r"any single write over (\d+) MB") * 1024 * 1024)

    def test_allowed_hosts_match_gate(self):
        network = GATE.split("- **Network:**", 1)[1].split("- **Reads:**", 1)[0]
        self.assertEqual(policy.ALLOWED_HOSTS, set(re.findall(r"`([a-z0-9.-]+\.(?:io|co|com))`", network)))


if __name__ == "__main__":
    unittest.main()
