"""Our MCP client (tools/mcp_client.py), the Claude Code run (tools/mcp_claude_run.py), and the committed transcripts.

The server answers here come from our real server on CONSTRUCTED saved answers in a temporary copy of the repo, from
the copied lesson 8 reference server, or from a CONSTRUCTED stand-in server written by a test. No test runs Claude
Code: the Claude Code tests hand the run a CONSTRUCTED stream of events through a stand-in runner, and
tests/__init__.py points JOB_AGENT_CLAUDE at a path that does not exist.
"""

import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from job_agent import claude_judge

from .loop_helpers import REPO
from .test_mcp_server import CHILD_ENV, INIT, KEPT_ID, REJECTED_ID, UNKNOWN_ID, fixture_repo


def load(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


client = load("mcp_client")
claude_run = load("mcp_claude_run")
STAMP = "2026-11-21T000000Z"
COMMITTED = REPO / "js3" / "mcp" / "transcripts"


def own_plan():
    return client.own_plan(kept=("ashby-openai", KEPT_ID), rejected=("ashby-openai", REJECTED_ID),
                           unknown=("ashby-openai", UNKNOWN_ID))


def read_jsonl(path: Path) -> list:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line]


def answered_once(test, log: list) -> None:
    """Every request the client sent was answered exactly once, in its session, unless the server had ended."""
    steps = {(e["session"], e["step"]): e for e in log if e["type"] == "step"}
    for entry in log:
        if entry["type"] != "line" or entry["dir"] != "client->server":
            continue
        message = client._parse(entry["text"].encode("utf-8"))
        if not (isinstance(message, dict) and "id" in message):
            continue
        answers = [e for e in log if e["type"] == "line" and e["dir"] == "server->client" and e["session"] ==
                   entry["session"] and (client._parse(e["text"].encode("utf-8")) or {}).get("id") == message["id"]]
        if steps[(entry["session"], entry["step"])]["actual"] in ("ends", "not sent"):
            test.assertEqual(answers, [])
        else:
            test.assertEqual(len(answers), 1, (entry["session"], entry["step"]))


class ClientOnOurServerTest(unittest.TestCase):
    def setUp(self):
        self.root = fixture_repo(Path(tempfile.mkdtemp(prefix="job-agent-mcp-client-")))
        self.addCleanup(shutil.rmtree, self.root, ignore_errors=True)

    def test_every_answer_is_the_expected_one_and_the_server_record_agrees(self):
        result = client.run("own", repo=self.root, plan=own_plan(), stamp=STAMP)
        self.assertTrue(result["ok"], [o for o in result["outcomes"] if not o["match"]])
        self.assertEqual((result["summary"]["matched"], result["summary"]["steps"]), (31, 31))
        self.assertTrue(result["comparison"]["match"], result["comparison"]["details"])
        self.assertEqual(result["comparison"]["sessions"], 5)
        folder = self.root / "js3" / "mcp" / "transcripts"
        self.assertEqual(sorted(p.name for p in folder.iterdir()),
                         [f"{STAMP}-own-client.jsonl", f"{STAMP}-own-client.md", f"{STAMP}-own-server.jsonl"])
        log = read_jsonl(folder / f"{STAMP}-own-client.jsonl")
        answered_once(self, log)
        self.assertEqual(log[0]["command"][:4], ["python3", "-B", "-m", "job_agent.mcp_server"])
        md = (folder / f"{STAMP}-own-client.md").read_text(encoding="utf-8")
        self.assertIn("**31 of 31 answers were the expected ones.**", md)
        self.assertIn("It matches this record line for line.", md)
        self.assertNotIn(str(self.root.resolve()), md + (folder / f"{STAMP}-own-client.jsonl").read_text())

    def test_a_transcript_is_never_overwritten(self):
        plan = [{"name": "main", "about": "a short session", "steps": client.handshake(1)}]
        client.run("own", repo=self.root, plan=plan, stamp=STAMP)
        with self.assertRaises(FileExistsError):
            client.run("own", repo=self.root, plan=plan, stamp=STAMP)

    def test_a_wrong_expectation_is_recorded_as_a_mismatch(self):
        plan = [{"name": "main", "about": "a wrong expectation", "steps": [
            *client.handshake(1), client.step("tools/list", client.request(2, "tools/list"), "error -32601")]}]
        result = client.run("own", repo=self.root, plan=plan, stamp=STAMP)
        self.assertFalse(result["ok"])
        self.assertEqual([(o["actual"], o["match"]) for o in result["outcomes"]][-1], ("result", False))
        md = (self.root / "js3" / "mcp" / "transcripts" / f"{STAMP}-own-client.md").read_text(encoding="utf-8")
        self.assertIn("**Mismatch.**", md)

    def test_a_server_that_answers_a_notification_or_ends_early_is_caught(self):
        stand_in = self.root / "stand_in_server.py"  # CONSTRUCTED: answers every line, notifications included
        stand_in.write_text("import json, sys\nfor line in sys.stdin:\n    m = json.loads(line)\n"
                            "    if m.get('method') == 'stop':\n        sys.exit(1)\n"
                            "    print(json.dumps({'jsonrpc': '2.0', 'id': m.get('id'), 'result': {}}), flush=True)\n",
                            encoding="utf-8")
        plan = [{"name": "main", "about": "a constructed server", "steps": [
            *client.handshake(1), client.step("tools/list", client.request(2, "tools/list"), "result"),
            client.step("stop", client.request(3, "stop"), "result"),
            client.step("tools/list", client.request(4, "tools/list"), "result")]}]
        result = client.run("other", repo=self.root, out=self.root / "out", plan=plan, stamp=STAMP,
                            command=[sys.executable, "-B", str(stand_in)])
        actual = [(o["label"], o["actual"], o["match"]) for o in result["outcomes"]]
        self.assertEqual(actual, [("initialize", "result", True), ("notifications/initialized", "answered", False),
                                  ("tools/list", "result", True), ("stop", "ends", False),
                                  ("tools/list", "not sent", False)])


@unittest.skipUnless((REPO / client.OTHER_SERVER).exists(), "the copied reference server is not in this copy")
class ClientOnTheReferenceServerTest(unittest.TestCase):
    def test_the_reference_server_does_what_its_source_says(self):
        out = Path(tempfile.mkdtemp(prefix="job-agent-mcp-other-"))
        self.addCleanup(shutil.rmtree, out, ignore_errors=True)
        result = client.run("other", repo=REPO, out=out, stamp=STAMP)
        self.assertTrue(result["ok"], [o for o in result["outcomes"] if not o["match"]])
        self.assertEqual(result["summary"]["matched"], 30)
        ends = {e["session"]: e["stderr"] for e in read_jsonl(out / f"{STAMP}-other-client.jsonl")
                if e["type"] == "session_end"}
        self.assertIn("UnicodeDecodeError", ends["bytes"])
        self.assertIn("RecursionError", ends["deep"])
        self.assertNotIn(str(REPO), ends["bytes"])


class ClaudeCodeRunTest(unittest.TestCase):
    """tools/mcp_claude_run.py with a stand-in runner: the lock-down of the command, and the checks of a run."""

    def test_the_command_allows_our_one_tool_and_nothing_else(self):
        config = claude_run.mcp_config(Path("/r/js3/mcp/transcripts/t.jsonl"), python="/usr/bin/python3",
                                       repo=Path("/r"))
        argv = claude_run.command(Path("/x/claude"), config)
        pairs = list(zip(argv, argv[1:]))
        for pair in (("--tools", ""), ("--permission-mode", "dontAsk"), ("--permission-prompts", "none"),
                     ("--allowedTools", claude_run.TOOL)):
            self.assertIn(pair, pairs)
        after = argv[argv.index("--allowedTools") + 2]
        self.assertTrue(after.startswith("--"))  # the tool list holds one name only
        for flag in ("--print", "--strict-mcp-config", "--restricted", "--no-session-persistence",
                     "--disable-slash-commands"):
            self.assertIn(flag, argv)
        self.assertFalse([a for a in argv if "dangerously" in a or "bypass" in a.lower()])
        servers = json.loads(argv[argv.index("--mcp-config") + 1])["mcpServers"]
        self.assertEqual(list(servers), ["job-search-agent"])
        self.assertEqual(servers["job-search-agent"]["args"],
                         ["-B", "-m", "job_agent.mcp_server", "--transcript", "/r/js3/mcp/transcripts/t.jsonl"])
        self.assertEqual(claude_run.TOOL, "mcp__job-search-agent__score_posting")
        env = claude_judge.environment(Path("/x/claude"), {"ANTHROPIC_API_KEY": "k", "HOME": "/h", "PATH": "/p"})
        self.assertNotIn("ANTHROPIC_API_KEY", env)

    def test_a_constructed_stream_is_checked_against_the_server_record(self):
        root = fixture_repo(Path(tempfile.mkdtemp(prefix="job-agent-mcp-claude-")))
        self.addCleanup(shutil.rmtree, root, ignore_errors=True)
        passed = claude_run.run("ashby-openai", KEPT_ID, runner=StandIn(root), binary=Path("/nonexistent/claude"),
                                repo=root, stamp=STAMP)
        self.assertEqual([c["check"] for c in passed["record"]["checks"] if not c["passed"]], [])
        folder = root / "js3" / "mcp" / "transcripts"
        names = sorted(p.name for p in folder.iterdir())
        self.assertEqual(names, sorted(f"{STAMP}-claude-code-{k}" for k in (
            "server.jsonl", "server.md", "init.json", "events.jsonl", "answer.md", "run.json")))
        init = json.loads((folder / f"{STAMP}-claude-code-init.json").read_text(encoding="utf-8"))
        self.assertEqual(init["cwd"], claude_run.TEMP_PLACEHOLDER)
        for name in names:
            self.assertNotIn(str(root.resolve()), (folder / name).read_text(encoding="utf-8"), name)
        self.assertIn("The posting is kept.", (folder / f"{STAMP}-claude-code-answer.md").read_text())
        tampered = claude_run.run("ashby-openai", KEPT_ID, runner=StandIn(root, tamper=True),
                                  binary=Path("/nonexistent/claude"), repo=root, stamp="2026-11-21T000001Z")
        failed = [c["check"] for c in tampered["record"]["checks"] if not c["passed"]]
        self.assertEqual(failed, ["the tool result Claude Code passed on is the text the server sent"])


class StandIn:
    """Stands in for Claude Code: starts our real server from the --mcp-config it is given, as a client would, and
    prints a CONSTRUCTED stream of events around the server's real answer (or a tampered copy of it)."""

    def __init__(self, root: Path, tamper: bool = False):
        self.root, self.tamper = root, tamper

    def __call__(self, argv, stdin, cwd, env, timeout=None):
        server = json.loads(argv[argv.index("--mcp-config") + 1])["mcpServers"]["job-search-agent"]
        arguments = {"board": "ashby-openai", "posting_id": KEPT_ID}
        lines = [{"jsonrpc": "2.0", "id": 0, "method": "initialize", "params": INIT},
                 {"jsonrpc": "2.0", "method": "notifications/initialized"},
                 {"jsonrpc": "2.0", "id": 1, "method": "tools/list"},
                 {"jsonrpc": "2.0", "id": 2, "method": "tools/call",
                  "params": {"name": "score_posting", "arguments": arguments}}]
        done = subprocess.run([server["command"], *server["args"]], cwd=cwd, env={**CHILD_ENV, **server["env"]},
                              input="".join(json.dumps(m) + "\n" for m in lines).encode("utf-8"), capture_output=True,
                              timeout=60)
        answer = json.loads(done.stdout.decode("utf-8").splitlines()[-1])
        served = answer["result"]["content"][0]["text"]
        events = [
            {"type": "system", "subtype": "init", "cwd": cwd, "tools": [claude_run.TOOL],
             "mcp_servers": [{"name": "job-search-agent", "status": "connected"}], "apiKeySource": "none",
             "permissionMode": "dontAsk", "claude_code_version": "constructed"},
            {"type": "assistant", "message": {"model": "constructed", "content": [
                {"type": "tool_use", "id": "t1", "name": claude_run.TOOL, "input": arguments}]}},
            {"type": "user", "message": {"content": [{"type": "tool_result", "tool_use_id": "t1", "content": [
                {"type": "text", "text": served + (" tampered" if self.tamper else "")}]}]}},
            {"type": "assistant", "message": {"model": "constructed", "content": [
                {"type": "text", "text": "The posting is kept."}]}},
            {"type": "result", "subtype": "success", "is_error": False, "result": "The posting is kept.",
             "num_turns": 2, "permission_denials": []}]
        return {"stdout": "".join(json.dumps(e) + "\n" for e in events).encode("utf-8"), "stderr": b"",
                "exit_code": 0, "timed_out": False, "seconds": 1.0}


@unittest.skipUnless(COMMITTED.exists() and list(COMMITTED.glob("*-client.jsonl")), "no committed transcripts")
class CommittedTranscriptTest(unittest.TestCase):
    """The committed transcripts are whole: every request answered once, and the two records of our server agree."""

    def test_the_committed_client_transcripts(self):
        for path in sorted(COMMITTED.glob("*-client.jsonl")):
            log = read_jsonl(path)
            summary = log[-1]
            self.assertEqual(summary["matched"], summary["steps"], path.name)
            answered_once(self, log)
            if log[0]["target"] == "own":
                comparison = client.compare_with_server_log(log, REPO / log[0]["server_transcript"])
                self.assertTrue(comparison["match"], (path.name, comparison["details"]))

    def test_the_committed_claude_code_run(self):
        """Recomputed from the saved files: the server answered every request once, and the tool result Claude
        Code passed on is the text the server sent. The two checks the run recorded as failed are the ones whose
        expectations the real client did not meet (an extra "source" field; server/discover before initialize)."""
        for path in sorted(COMMITTED.glob("*-claude-code-server.jsonl")):
            entries = read_jsonl(path)
            self.assertEqual((entries[0]["event"], entries[-1]["event"]), ("start", "end"))
            sent = [json.loads(e["text"]) for e in entries if e.get("dir") == "in"]
            answers = [json.loads(e["text"]) for e in entries if e.get("dir") == "out"]
            for message in sent:
                if "id" in message:
                    self.assertEqual(len([a for a in answers if a.get("id") == message["id"]]), 1, message)
            stem = path.name[:-len("-server.jsonl")]
            events = read_jsonl(path.with_name(stem + "-events.jsonl"))
            call = next(m for m in sent if m.get("method") == "tools/call")
            served = next(a for a in answers if a.get("id") == call["id"])["result"]["content"][0]["text"]
            passed_on = claude_run.blocks(events, "tool_result")
            self.assertEqual([claude_run._text(b) for b in passed_on], [served])
            init = json.loads(path.with_name(stem + "-init.json").read_text(encoding="utf-8"))
            self.assertEqual(init["tools"], [claude_run.TOOL])
            self.assertEqual([(s["name"], s["status"]) for s in init["mcp_servers"]], [("job-search-agent", "connected")])
            run = json.loads(path.with_name(stem + "-run.json").read_text(encoding="utf-8"))
            failed = {c["check"]: c["seen"] for c in run["checks"] if not c["passed"]}
            self.assertLessEqual(set(failed), {"Claude Code connected to our server, and to no other",
                                               "the server saw initialize, then notifications/initialized, then "
                                               "tools/list, then tools/call"})
            methods = [m.get("method") for m in sent]
            self.assertEqual([m for m in methods if m != "server/discover"][:4],
                             ["initialize", "notifications/initialized", "tools/list", "tools/call"])


if __name__ == "__main__":
    unittest.main()
