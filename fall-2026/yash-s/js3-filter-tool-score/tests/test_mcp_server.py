"""The tool server: protocol behavior, what it declares, and what it can touch.
Every posting and saved result here is CONSTRUCTED for a test."""
import ast
import contextlib
import hashlib
import io
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from helpers import GOOD_BODY, ROOT, J, P, posting, rules
import mcp_client
import mcp_server as M

SAVED = {"about": "constructed results for a test", "results": [
    {"board": "OpenAI", "id": "a", "title": "Applied AI Engineer", "location": "SF", "url": "u", "decision": "review",
     "score": 80, "hard_exclusions": [], "review_reasons": ["experience unknown"]},
    {"board": "Anthropic", "id": "b", "title": "Data Engineer", "location": "SF", "url": "u", "decision": "review",
     "score": 80, "hard_exclusions": [], "review_reasons": ["experience unknown"]},
    {"board": "Databricks", "id": "c", "title": "Senior Data Engineer", "location": "SF", "url": "u",
     "decision": "rejected", "score": 90, "hard_exclusions": ["seniority word 'Senior' in title"], "review_reasons": []},
] + [{"board": "OpenAI", "id": f"z{i:02d}", "title": "Recruiter", "location": "SF", "url": "u", "decision": "rejected",
      "score": i, "hard_exclusions": ["excluded title word 'Recruiter'"], "review_reasons": []} for i in range(30)]}


def send(server, msg):
    return server.handle_line(msg if isinstance(msg, str) else json.dumps(msg))


def started():
    s = M.Server(rules(), SAVED)
    send(s, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-06-18"}})
    send(s, {"jsonrpc": "2.0", "method": "notifications/initialized"})
    return s


def call(server, name, args, id_=9):
    return send(server, {"jsonrpc": "2.0", "id": id_, "method": "tools/call", "params": {"name": name, "arguments": args}})


def payload(reply):
    return json.loads(reply["result"]["content"][0]["text"])


class Lifecycle(unittest.TestCase):
    def test_initialize_answers_with_the_clients_version_when_supported(self):
        s = M.Server(rules(), SAVED)
        r = send(s, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-03-26"}})
        self.assertEqual(r["result"]["protocolVersion"], "2025-03-26")
        self.assertEqual(r["result"]["capabilities"], {"tools": {"listChanged": False}})
        self.assertEqual(r["result"]["serverInfo"]["name"], "yash-js3-job-filter")

    def test_an_unknown_version_gets_the_newest_this_server_supports(self):
        s = M.Server(rules(), SAVED)
        r = send(s, {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {"protocolVersion": "2025-11-25"}})
        self.assertEqual(r["result"]["protocolVersion"], M.PROTOCOL_VERSIONS[0])

    def test_tools_before_initialize_are_refused_but_ping_works(self):
        s = M.Server(rules(), SAVED)
        self.assertEqual(send(s, {"jsonrpc": "2.0", "id": 1, "method": "tools/list"})["error"]["code"], -32002)
        self.assertEqual(send(s, {"jsonrpc": "2.0", "id": 2, "method": "ping"})["result"], {})

    def test_notifications_and_responses_get_no_reply(self):
        s = started()
        self.assertIsNone(send(s, {"jsonrpc": "2.0", "method": "notifications/cancelled", "params": {"requestId": 3}}))
        self.assertIsNone(send(s, {"jsonrpc": "2.0", "id": 5, "result": {}}))


class Declared(unittest.TestCase):
    def test_exactly_two_tools_both_declared_read_only_and_closed_world(self):
        tools = send(started(), {"jsonrpc": "2.0", "id": 2, "method": "tools/list"})["result"]["tools"]
        self.assertEqual([t["name"] for t in tools], ["score_posting", "search_saved_postings"])
        for t in tools:
            self.assertIs(t["annotations"]["readOnlyHint"], True)
            self.assertIs(t["annotations"]["destructiveHint"], False)
            self.assertIs(t["annotations"]["openWorldHint"], False)
            self.assertIs(t["inputSchema"]["additionalProperties"], False)

    def test_no_tool_takes_a_path_url_or_command(self):
        for t in M.TOOLS:
            for name in t["inputSchema"]["properties"]:
                self.assertNotRegex(name.lower(), r"path|file|url|command|cmd|dir")


class Tools(unittest.TestCase):
    def test_score_posting_matches_the_filter_exactly(self):
        got = payload(call(started(), "score_posting",
                           {"title": "Data Engineer", "location": "San Francisco", "description": GOOD_BODY}))
        want = J.evaluate(posting(), rules())
        self.assertEqual((got["decision"], got["score"], got["points"]), (want["decision"], want["score"], want["points"]))

    def test_plain_text_keeps_its_headings(self):
        text = "About the role\nBuild data pipelines.\nPreferred qualifications:\n5+ years of experience."
        got = payload(call(started(), "score_posting", {"title": "Data Engineer", "description": text}))
        self.assertEqual(got["experience_status"], "unknown")  # the 5+ years sits under a preferred heading

    def test_search_filters_sorts_and_caps_the_limit(self):
        s = started()
        got = payload(call(s, "search_saved_postings", {"decision": "review"}))
        self.assertEqual([(p["board"], p["id"]) for p in got["postings"]], [("Anthropic", "b"), ("OpenAI", "a")])
        self.assertEqual(payload(call(s, "search_saved_postings", {}))["returned"], 10)
        self.assertEqual(payload(call(s, "search_saved_postings", {"limit": 20}))["returned"], 20)
        self.assertTrue(call(s, "search_saved_postings", {"limit": 21})["result"]["isError"])
        got = payload(call(s, "search_saved_postings", {"title_contains": "data engineer", "min_score": 85}))
        self.assertEqual([p["id"] for p in got["postings"]], ["c"])

    def test_bad_arguments_are_tool_errors_not_crashes(self):
        s = started()
        for args in ({"limit": True}, {"limit": "5"}, {"board": "LinkedIn"}, {"path": "/etc/passwd"}):
            with self.subTest(args=args):
                r = call(s, "search_saved_postings", args)
                self.assertTrue(r["result"]["isError"])
        self.assertTrue(call(s, "score_posting", {"title": "x"})["result"]["isError"])  # description missing
        self.assertTrue(call(s, "score_posting", {"title": "x", "description": "y" * 100001})["result"]["isError"])


class ProtocolErrors(unittest.TestCase):
    def test_error_codes(self):
        s = started()
        self.assertEqual(call(s, "apply_to_job", {})["error"]["code"], -32602)
        self.assertEqual(send(s, {"jsonrpc": "2.0", "id": 3, "method": "resources/list"})["error"]["code"], -32601)
        self.assertEqual(send(s, "{not json")["error"]["code"], -32700)
        self.assertEqual(send(s, "[]")["error"]["code"], -32600)
        self.assertEqual(send(s, {"jsonrpc": "2.0", "id": None, "method": "ping"})["error"]["code"], -32600)
        self.assertEqual(send(s, {"jsonrpc": "1.0", "id": 4, "method": "ping"})["error"]["code"], -32600)

    def test_deeply_nested_json_is_a_parse_error_not_a_crash(self):
        # Regression test: on 2026-11-25 this input stopped the server (RecursionError).
        self.assertEqual(send(started(), "[" * 5000)["error"]["code"], -32700)

    def test_one_failing_message_does_not_stop_the_server(self):
        s, out = started(), io.StringIO()
        real, calls = s.handle_line, []

        def flaky(line):
            calls.append(line)
            if len(calls) == 1:
                raise RuntimeError("boom")
            return real(line)
        s.handle_line = flaky
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            M.serve(s, io.StringIO('{"jsonrpc":"2.0","id":1,"method":"ping"}\n{"jsonrpc":"2.0","id":2,"method":"ping"}\n'), out)
        self.assertIn("RuntimeError: boom", err.getvalue())  # the trace goes to stderr, never to the client
        self.assertNotIn("boom", out.getvalue())
        replies = [json.loads(x) for x in out.getvalue().splitlines()]
        self.assertEqual(replies[0]["error"]["code"], -32603)
        self.assertEqual(replies[1], {"jsonrpc": "2.0", "id": 2, "result": {}})


FORBIDDEN_MODULES = {"socket", "urllib", "http", "ftplib", "smtplib", "ssl", "subprocess", "requests", "asyncio",
                     "telnetlib", "xmlrpc", "multiprocessing", "ctypes", "shutil", "webbrowser", "imaplib", "poplib"}


def imported_modules(path):
    tree = ast.parse(Path(path).read_text(encoding="utf-8"))
    names = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names |= {a.name.split(".")[0] for a in node.names}
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module.split(".")[0])
    return names


class WhatItCanTouch(unittest.TestCase):
    def test_server_and_the_code_it_runs_import_nothing_that_reaches_out(self):
        for f in ("mcp_server.py", "job_filter.py", "postings.py"):
            with self.subTest(f=f):
                self.assertFalse(imported_modules(ROOT / f) & FORBIDDEN_MODULES)

    def test_the_only_file_write_is_the_transcript(self):
        tree = ast.parse((ROOT / "mcp_server.py").read_text(encoding="utf-8"))
        writers = []
        for cls in [n for n in tree.body if isinstance(n, ast.ClassDef)] + [tree]:
            for node in ast.walk(cls):
                if isinstance(node, ast.Call):
                    f = node.func
                    name = f.id if isinstance(f, ast.Name) else f.attr if isinstance(f, ast.Attribute) else ""
                    mode = node.args[1].value if name == "open" and len(node.args) > 1 and isinstance(node.args[1], ast.Constant) else ""
                    if name in ("write_text", "write_bytes", "unlink", "rmdir", "rename", "replace", "system", "popen") or \
                            (name == "open" and any(c in str(mode) for c in "wax+")):
                        writers.append((getattr(cls, "name", "module"), name))
        self.assertEqual(sorted(set(w for w in writers if w[0] != "module")), [("Transcript", "open")])

    def test_transcript_and_results_must_stay_inside_this_folder(self):
        with self.assertRaises(SystemExit):
            M.Transcript(Path(tempfile.gettempdir()))
        with self.assertRaises(SystemExit):
            M.load_saved(Path(tempfile.gettempdir()) / "results.json")

    @unittest.skipUnless((P.DEFAULT_JS2 / "persona" / P.PERSONA_NAME).exists(), "needs the JS2 persona file")
    def test_a_real_session_changes_nothing_but_its_own_transcript(self):
        with tempfile.TemporaryDirectory() as tmp:
            tmp = Path(tmp)
            proj = tmp / "proj"
            proj.mkdir()
            for f in ROOT.glob("*.py"):
                shutil.copy2(f, proj / f.name)
            shutil.copytree(ROOT / "rules", proj / "rules")
            (tmp / "js2-loop-tools-diff").symlink_to(P.DEFAULT_JS2.resolve(), target_is_directory=True)
            run = proj / "runs" / "constructed"
            run.mkdir(parents=True)
            (run / "results.json").write_text(json.dumps(SAVED["results"]), encoding="utf-8")

            def snapshot():
                return {str(p.relative_to(proj)): hashlib.sha256(p.read_bytes()).hexdigest()
                        for p in proj.rglob("*") if p.is_file()}
            before = snapshot()
            steps = [{"tool": "score_posting", "arguments": {"title": "Data Engineer", "description": GOOD_BODY}},
                     {"tool": "search_saved_postings", "arguments": {"decision": "review"}},
                     {"tool": "score_posting", "arguments": {"title": "x", "description": "y", "path": "../../x"}},
                     {"raw": "[" * 5000}, {"request": "ping"}]
            summary = mcp_client.run(["python3", "mcp_server.py", "--results", "runs/constructed/results.json"],
                                     steps, tmp / "client.jsonl", cwd=proj)
            after = snapshot()
            self.assertEqual({k: v for k, v in after.items() if k in before}, before)  # nothing changed
            new = sorted(set(after) - set(before))
            self.assertEqual(len(new), 1)
            self.assertRegex(new[0], r"^mcp/transcripts/server-session-.*\.jsonl$")
            self.assertEqual(summary[-1][1]["result"], {})  # still answering after the deep-nesting probe
            dirs = [json.loads(x)["dir"] for x in (proj / new[0]).read_text(encoding="utf-8").splitlines()]
            self.assertEqual(dirs.count("client->server"), 2 + 1 + len(steps))  # initialize, initialized, list, steps
            self.assertEqual(dirs.count("server->client"), 2 + len(steps))


if __name__ == "__main__":
    unittest.main()
