"""The claims step without calling Claude: the prompt, the reply parser and the quote check.
Every reply here is CONSTRUCTED, not Claude output."""

import json
import unittest

from jobwatch import claims, screen

ITEM = screen.Item(board="greenhouse/anthropic", key="42", title="Software Engineer, Model Serving",
                   location="San Francisco, CA",
                   description="&lt;p&gt;Five years preferred.&lt;/p&gt;&lt;p&gt;You will build model serving systems.&lt;/p&gt;",
                   captured_at="2026-11-24T22:36:19Z")


def reply(payload):
    return json.dumps({"type": "result", "is_error": False, "result": payload})


class PromptTest(unittest.TestCase):
    def test_the_prompt_carries_the_posting_as_saved(self):
        system, user = claims.build_prompt(ITEM)
        self.assertIn("Reply with JSON only", system)
        self.assertIn("Title: Software Engineer, Model Serving", user)
        self.assertIn("Five years preferred. You will build model serving systems.", user)
        self.assertIn("I cannot tell whether this role offers sponsorship.", user)
        self.assertNotIn("{text}", user)

    def test_the_command_has_no_tools_settings_or_servers(self):
        seen = {}

        def runner(command, **kw):
            seen.update(command=command, cwd=kw["cwd"], input=kw["input"])
            return type("Done", (), {"returncode": 0, "stdout": reply('{"claims": []}'), "stderr": ""})()

        claims.claude_code_send(runner=runner)("SYSTEM", "USER")
        command = seen["command"]
        self.assertEqual(command[:2], ["claude", "-p"])
        for flag, value in (("--tools", ""), ("--setting-sources", ""), ("--model", "claude-opus-5-5"),
                            ("--output-format", "json"), ("--system-prompt", "SYSTEM")):
            self.assertEqual(command[command.index(flag) + 1], value)
        for flag in ("--strict-mcp-config", "--disable-slash-commands", "--no-session-persistence"):
            self.assertIn(flag, command)
        self.assertEqual(seen["input"], "USER")


class ParseAndCheckTest(unittest.TestCase):
    def test_a_reply_in_a_code_fence_is_read(self):
        text = '```json\n{"claims": [{"kind": "work", "claim": "It builds model serving systems.", ' \
               '"quote": "You will build model serving systems.", "source_field": "description"}]}\n```'
        self.assertEqual(len(claims.parse_reply(reply(text))), 1)

    def test_a_wrong_shape_is_refused(self):
        for bad in ('{"claims": [{"kind": "salary", "claim": "x"}]}', '{"items": []}', 'not json'):
            with self.assertRaises(claims.ClaimsError):
                claims.parse_reply(reply(bad))
        with self.assertRaises(claims.ClaimsError):
            claims.parse_reply(json.dumps({"is_error": True, "result": "limit"}))

    def test_quotes_are_checked_against_the_field_they_name(self):
        rows = claims.checked(ITEM, [
            {"kind": "qualification", "claim": "Five years are required.", "quote": "Five years preferred.",
             "source_field": "description"},
            {"kind": "work", "claim": "It builds model serving.", "quote": "Five years required.",
             "source_field": "description"},
            {"kind": "location", "claim": "It is in San Francisco.", "quote": "San Francisco, CA",
             "source_field": "location"},
            {"kind": "sponsorship", "claim": "I cannot tell whether this role offers sponsorship.",
             "quote": None, "source_field": None},
        ])
        self.assertEqual([r["quote_check"] for r in rows], ["quote found", "quote not found", "quote found", "no quote"])


if __name__ == "__main__":
    unittest.main()
