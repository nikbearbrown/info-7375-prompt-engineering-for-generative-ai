"""The runtime trace (tools/mcp_runtime_trace.py and its boot, tools/mcp_trace_boot.py): an audit hook around a server.

Every script traced here is a CONSTRUCTED throwaway written to a temporary folder, never a server file, except where
a test runs our real server on the CONSTRUCTED saved answers of tests/test_mcp_server.fixture_repo. No test reaches
the network: the planted socket is created and closed without connecting, and the one planted connection (to
127.0.0.1) runs only under sandbox-exec, which refuses it.
"""

import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from .loop_helpers import REPO
from .test_mcp_server import ANSWERED, CHILD_ENV, SESSION, fixture_repo, RUN_ID


def load(name):
    spec = importlib.util.spec_from_file_location(name, REPO / "tools" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


trace = load("mcp_runtime_trace")
boot = load("mcp_trace_boot")
BOOT = str(REPO / "tools" / "mcp_trace_boot.py")
SENTINEL = "jsa-trace-sentinel-" + os.urandom(6).hex()  # planted in the traced process; it must never come out
TRUE = shutil.which("true", path="/usr/bin:/bin") or "/usr/bin/true"
MODULES = ["__init__", "errors", "evidence", "filter", "filter_run", "mcp_server", "providers", "resume", "rule"]
PLANTED = """import os, socket, subprocess, sys
with open(os.path.join(sys.argv[1], "planted.txt"), "w") as handle:
    handle.write("x")
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.close()
os.environ["JSA_PLANTED"] = sys.argv[2]
subprocess.run([sys.argv[3]], env={"JSA_PLANTED": sys.argv[2]}, check=True)
print("done")
"""


def traced(boot_args, cwd, log, env=None, stdin=b"", prefix=(), flags=()):
    """python3 -B [flags] tools/mcp_trace_boot.py LOG BOOT_ARGS..., as tools/mcp_runtime_trace.py starts it."""
    return subprocess.run(list(prefix) + [sys.executable, "-B", *flags, BOOT, str(log), *boot_args], cwd=str(cwd),
                          env=env or dict(CHILD_ENV), input=stdin, capture_output=True, timeout=60)


def everything_written(summary, md, log) -> str:
    return json.dumps(summary) + md + Path(log).read_text(encoding="ascii")


class PlantedTest(unittest.TestCase):
    """A CONSTRUCTED script that writes a file, makes a socket and starts a program, traced by the boot."""

    @classmethod
    def setUpClass(cls):
        cls.root = Path(tempfile.mkdtemp(prefix="job-agent-trace-"))
        script = cls.root / "planted.py"
        script.write_text(PLANTED, encoding="utf-8")
        cls.log = cls.root / "planted.events.jsonl"
        env = dict(CHILD_ENV, JSA_TRACE_SECRET_TOKEN=SENTINEL)
        cls.done = traced([str(script), str(cls.root), SENTINEL, TRUE], cls.root, cls.log, env=env, flags=("-I",))
        cls.summary = trace.summarize({"planted": cls.log}, cls.root)
        cls.md = trace.render_summary(dict(cls.summary, run="planted", about="a planted script", tree="a temp folder",
                                           server_file="planted.py", server_sha256="-", command=["-"], client={
                                               "steps": 0, "as_the_plan_expects": 0}, answers={
                                               "lines_from_the_server": 0, "exit_codes": {}}))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_the_script_ran_and_its_stdout_is_its_own(self):
        self.assertEqual((self.done.returncode, self.done.stdout, self.done.stderr), (0, b"done\n", b""))

    def test_a_planted_write_is_caught(self):
        writes = [(w["path"], w["mode"]) for w in self.summary["writes"]]
        self.assertEqual(writes, [("<repo>/planted.txt", "w")])
        self.assertIn("O_CREAT", self.summary["writes"][0]["flags"])

    def test_a_planted_socket_is_caught(self):
        self.assertEqual([(s["event"], s["family"], s["type"]) for s in self.summary["sockets"]],
                         [("socket.__new__", 2, 1)])
        self.assertIn("socket", self.summary["modules"]["network_or_process"])

    def test_a_planted_process_is_caught_with_its_file_name_only(self):
        popen = [p for p in self.summary["processes"] if p["event"] == "subprocess.Popen"]
        self.assertEqual([p["program"] for p in popen], ["true"])
        self.assertIn("subprocess", self.summary["modules"]["network_or_process"])

    def test_a_planted_environment_value_never_appears_in_any_output(self):
        self.assertGreaterEqual(self.summary["other_events"]["server"].get("os.putenv", 0), 1)  # seen, by name
        self.assertNotIn(SENTINEL, everything_written(self.summary, self.md, self.log))
        folder = self.root / "out"
        folder.mkdir()
        (folder / "summary.md").write_text(self.md, encoding="utf-8")
        self.assertEqual(trace.privacy_problems(folder, [SENTINEL]), [])

    def test_no_hook_error_and_every_line_readable(self):
        self.assertEqual((self.summary["hook_errors"], self.summary["unreadable_lines"],
                          self.summary["sessions_without_a_record"]), (0, 0, []))


class ClassifyTest(unittest.TestCase):
    def test_reads_and_writes_are_told_apart(self):
        reads = [("r", os.O_RDONLY), ("r", os.O_RDONLY | os.O_CLOEXEC), (None, os.O_RDONLY), ("rb", None)]
        writes = [("w", None), ("a", None), ("x", None), ("r+", None), (None, os.O_WRONLY),
                  (None, os.O_RDWR), (None, os.O_RDONLY | os.O_CREAT), (None, os.O_TRUNC),
                  (None, os.O_WRONLY | os.O_APPEND | os.O_CREAT | getattr(os, "O_NOFOLLOW", 0))]
        self.assertEqual([trace.is_write(m, f) for m, f in reads], [False] * len(reads))
        self.assertEqual([trace.is_write(m, f) for m, f in writes], [True] * len(writes))

    def test_a_constructed_record_is_filed_by_category_with_placeholders(self):
        with tempfile.TemporaryDirectory() as tmp:
            tree = Path(tmp) / "repo"
            log = Path(tmp) / "x.events.jsonl"
            home = str(Path.home())
            events = [
                {"n": "_start", "cwd": str(tree), "stdlib": "/py/lib", "python_dirs": ["/py"]},
                {"n": "_modules", "p": "startup", "m": ["sys"]},
                {"n": "open", "p": "server", "path": f"{tree}/job_agent/__pycache__/filter.cpython-312.pyc",
                 "mode": "r", "flags": os.O_RDONLY},
                {"n": "open", "p": "server", "path": f"{tree}/job_agent/filter.py", "mode": "r", "flags": 0},
                {"n": "open", "p": "server", "path": "FILTER.md", "mode": "r", "flags": 0},
                {"n": "open", "p": "server", "path": "/py/lib/json/__pycache__/decoder.cpython-312.pyc", "mode": "r",
                 "flags": 0},
                {"n": "open", "p": "server", "path": f"{home}/elsewhere.txt", "mode": "r", "flags": 0},
                {"n": "open", "p": "server", "path": f"{tree}/out.txt", "mode": None,
                 "flags": os.O_WRONLY | os.O_CREAT},
                {"n": "os.remove", "p": "server", "paths": [f"{tree}/old.txt"]},
                {"n": "os.listdir", "p": "server", "paths": [f"{tree}/runs"]},
                {"n": "import", "p": "server", "m": "json"},
                {"n": "import", "p": "server", "m": "nt"},
                {"n": "os.putenv", "p": "server"},
                {"n": "_modules", "p": "server", "m": ["sys", "json"]},
            ]
            log.write_text("".join(json.dumps(e) + "\n" for e in events), encoding="ascii")
            s = trace.summarize({"one": log}, tree)
        reads = s["reads"]["server"]
        self.assertEqual(reads["code"]["files"], ["<repo>/job_agent/filter.py"])  # the cache file is its source
        self.assertEqual(reads["filter"]["opens"], {"<repo>/FILTER.md": 1})  # a relative path, from the cwd
        self.assertEqual(reads["python"]["files"], ["<python>/json/decoder.py"])
        self.assertEqual(reads["outside"]["opens"], {"~/elsewhere.txt": 1})
        self.assertEqual(reads["runs"]["listings"], {"<repo>/runs (os.listdir)": 1})
        self.assertEqual([(w["path"], w["flags"][:2]) for w in s["writes"]],
                         [("<repo>/out.txt", ["O_WRONLY", "O_CREAT"])])
        self.assertEqual(s["file_changes"], [{"event": "os.remove", "paths": ["<repo>/old.txt"], "phase": "server",
                                              "count": 1}])
        self.assertEqual((s["modules"]["server"], s["modules"]["not_loaded"]), (["json"], ["nt"]))
        self.assertEqual(s["other_events"]["server"], {"os.putenv": 1})
        self.assertNotIn(home + "/", json.dumps(s))

    def test_a_json_string_inside_an_answer_is_compared_field_by_field(self):
        def answer(sha):
            text = json.dumps({"tool": "score_posting", "filter": {"version": "1.0", "sha256": sha}})
            return json.dumps({"jsonrpc": "2.0", "id": 3, "result": {"content": [{"type": "text", "text": text}]}})
        left = {"main": {"lines": [[1, "{}"], [4, answer("a" * 64)]], "exit_code": 0}}
        right = {"main": {"lines": [[1, "{}"], [4, answer("b" * 64)]], "exit_code": 0}}
        [d] = trace.answer_differences(left, right)
        self.assertEqual((d["session"], d["step"], d["id"], d["path"], d["left"], d["right"]),
                         ("main", 4, 3, "$.result.content[0].text (its JSON).filter.sha256", "a" * 64, "b" * 64))
        self.assertEqual(trace.answer_differences(left, left), [])

    def test_the_boot_writes_json_without_the_json_module(self):
        for text in ("plain", 'quote " and \\ backslash', "tab\tnewline\n", "café ​ \U0001f600", ""):
            self.assertEqual(json.loads(boot.quote(text)), text)
        self.assertEqual(json.loads(boot.value(("127.0.0.1", 9))), ["127.0.0.1", 9])
        self.assertEqual(boot.program(["/usr/bin/git", "-C", "x"]), "git")
        self.assertEqual(boot.program("ls -la /tmp"), "ls")

    def test_the_privacy_check_finds_the_home_folder(self):
        with tempfile.TemporaryDirectory() as tmp:
            (Path(tmp) / "a.md").write_text("see " + str(Path.home()) + "/x", encoding="utf-8")
            self.assertEqual(len(trace.privacy_problems(Path(tmp))), 1 + (len(Path.home().name) >= 5))


class ServerTest(unittest.TestCase):
    """Our real server, traced in a fixture copy with CONSTRUCTED saved answers (one session, every kind of line)."""

    @classmethod
    def setUpClass(cls):
        cls.root = fixture_repo(Path(tempfile.mkdtemp(prefix="job-agent-trace-server-")))
        cls.stdin = b"".join(line + b"\n" for line in SESSION)
        cls.log = cls.root / "server.events.jsonl"
        cls.done = traced(["-m", "job_agent.mcp_server"], cls.root, cls.log, stdin=cls.stdin)
        cls.plain = subprocess.run([sys.executable, "-B", "-m", "job_agent.mcp_server"], cwd=str(cls.root),
                                   env=dict(CHILD_ENV), input=cls.stdin, capture_output=True, timeout=60)
        cls.summary = trace.summarize({"one": cls.log}, cls.root)
        probe = ("import json, sys\nbefore = set(sys.modules)\nimport platform\n"
                 "print(json.dumps(sorted(set(sys.modules) - before)))\n")
        loads = subprocess.run([sys.executable, "-B", "-I", "-c", probe], capture_output=True, timeout=60)
        cls.platform_loads = sorted(m for m in json.loads(loads.stdout) if trace.watched(m))

    @classmethod
    def tearDownClass(cls):
        shutil.rmtree(cls.root, ignore_errors=True)

    def test_the_traced_server_answers_on_stdout_with_json_rpc_lines_only(self):
        self.assertEqual((self.done.returncode, self.done.stderr), (0, b""))
        lines = self.done.stdout.decode("utf-8").splitlines()
        self.assertEqual(len(lines), ANSWERED)
        for line in lines:
            message = json.loads(line)
            self.assertEqual(message["jsonrpc"], "2.0")
            self.assertEqual(len({"result", "error"} & set(message)), 1)
            self.assertIn("id", message)

    def test_the_hook_changes_no_answer(self):
        self.assertEqual(self.done.stdout, self.plain.stdout)

    def test_the_summary_of_a_known_small_run(self):
        s, reads = self.summary, self.summary["reads"]["server"]
        self.assertEqual((s["writes"], s["file_changes"], s["sockets"], s["network"], s["processes"], s["ctypes"]),
                         ([], [], [], [], [], {}))
        board = f"<repo>/runs/{RUN_ID}/boards/ashby-openai"
        # three calls read their sources (a kept, a rejected and an unknown posting); the others are refused first
        self.assertEqual(reads["filter"]["opens"], {"<repo>/FILTER.md": 6})
        self.assertEqual(reads["persona"]["opens"], {"<repo>/persona/jane-doe.json": 3})
        self.assertEqual(reads["runs"]["opens"], {f"{board}/attempt-1.json.gz": 3, f"{board}/attempt-1.meta.json": 6})
        self.assertEqual(reads["code"]["files"], [f"<repo>/job_agent/{m}.py" for m in MODULES])
        self.assertNotIn("outside", reads)
        self.assertNotIn("descriptor", reads)
        # what the standard library's platform module loads on this Python (subprocess on 3.9; nothing on 3.12)
        self.assertEqual(s["modules"]["network_or_process"], self.platform_loads)
        self.assertEqual((s["hook_errors"], s["unreadable_lines"]), (0, 0))

    def test_with_transcript_the_only_write_is_the_transcript(self):
        log = self.root / "transcript.events.jsonl"
        done = traced(["-m", "job_agent.mcp_server", "--transcript", "js3/mcp/transcripts/t.jsonl"], self.root, log,
                      stdin=self.stdin)
        self.assertEqual((done.returncode, done.stdout), (0, self.plain.stdout))
        s = trace.summarize({"one": log}, self.root)
        target = "<repo>/js3/mcp/transcripts/t.jsonl"
        self.assertEqual([(w["path"], w["through_descriptor"], w["count"]) for w in s["writes"]],
                         [(target, False, 1), (target, True, 1)])
        self.assertIn("O_NOFOLLOW", s["writes"][0]["flags"])
        self.assertEqual(s["file_changes"], [])


class SandboxTest(unittest.TestCase):
    def test_sandbox_exec_denies_a_planted_connection_and_the_hook_records_it(self):
        check = trace.sandbox_check(sys.executable)
        if not check.get("available"):
            self.skipTest(f"sandbox-exec cannot run here: {check.get('error')}")
        self.assertEqual(check["planted_connect_to_127.0.0.1_port_9"], "PermissionError 1")
        with tempfile.TemporaryDirectory() as tmp:
            script = Path(tmp) / "connect.py"
            script.write_text("import socket\ns = socket.socket()\ntry:\n    s.connect(('127.0.0.1', 9))\n"
                              "except PermissionError:\n    print('denied')\n", encoding="utf-8")
            log = Path(tmp) / "connect.events.jsonl"
            done = traced([str(script)], tmp, log, prefix=(trace.SANDBOX_EXEC, "-p", trace.NO_NETWORK), flags=("-I",))
            s = trace.summarize({"one": log}, Path(tmp))
        self.assertEqual((done.returncode, done.stdout), (0, b"denied\n"))
        self.assertIn({"event": "socket.connect", "count": 1, "address": ["127.0.0.1", 9]}, s["sockets"])


@unittest.skipUnless(list((REPO / "js3" / "mcp" / "runtime").glob("*/manifest.json")), "no committed runtime trace")
class CommittedTraceTest(unittest.TestCase):
    """The committed runtime evidence is whole and holds nothing private."""

    def test_every_committed_trace(self):
        for manifest_path in sorted((REPO / "js3" / "mcp" / "runtime").glob("*/manifest.json")):
            folder = manifest_path.parent
            self.assertEqual(trace.privacy_problems(folder), [], folder.name)
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            for interpreter in manifest["interpreters"]:
                for run in interpreter["runs"]:
                    if "skipped" in run:
                        continue
                    for name in run["files"]:
                        self.assertTrue((folder / interpreter["folder"] / name).exists(), name)
                    self.assertEqual(run["as_the_plan_expects"], run["steps"], run["label"])
                    if not run["traced"]:
                        continue
                    s = json.loads((folder / interpreter["folder"] / f"{run['label']}.summary.json").read_text())
                    self.assertEqual((s["sockets"], s["network"], s["processes"], s["file_changes"]), ([], [], [], []))
                    self.assertEqual(s["sessions_without_a_record"], [])
                    written = {w["path"] for w in s["writes"]}
                    self.assertEqual(written, {"<repo>/" + trace.TRANSCRIPT} if run["transcript"] else set())


if __name__ == "__main__":
    unittest.main()
