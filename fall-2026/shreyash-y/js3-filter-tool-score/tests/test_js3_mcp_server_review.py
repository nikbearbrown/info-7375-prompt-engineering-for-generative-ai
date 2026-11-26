"""Two server bugs found by the independent reviews of 2026-11-25 (after the server's first tests).
Written by Claude Code BEFORE the fix:
1. A message whose params, or a tools/call whose arguments, is not a JSON object crashed the server
   (AttributeError / TypeError, exit 1) instead of answering an error. TOOLSERVER.md claimed the server
   enforces the schema itself.
2. The transcript-folder check compared strings, so a sibling folder transcripts-evil/ was accepted:
   the same bug class as JS2's runs-evil (GATE.md section 7)."""
import io
import json
import pathlib
import subprocess
import sys
import unittest

from js3 import mcp_server

HERE = pathlib.Path(__file__).resolve().parent.parent


def talk(server, *lines):
    out = io.StringIO()
    server.serve(io.StringIO("".join(l + "\n" for l in lines)), out)
    return [json.loads(x) for x in out.getvalue().splitlines()]


class MalformedParams(unittest.TestCase):
    def test_params_that_are_not_an_object_get_invalid_params(self):
        s = mcp_server.Server(log_dir=None)
        (r,) = talk(s, '{"jsonrpc":"2.0","id":1,"method":"initialize","params":[1]}')
        self.assertEqual(r["error"]["code"], -32602)

    def test_arguments_that_are_not_an_object_are_a_tool_error(self):
        s = mcp_server.Server(log_dir=None)
        for args in ("5", '"klaviyo:7792539003"', "[1]", "null"):
            (r,) = talk(s, '{"jsonrpc":"2.0","id":2,"method":"tools/call","params":{"name":"score_posting","arguments":%s}}' % args)
            self.assertTrue(r["result"]["isError"], args)

    def test_the_server_keeps_running_after_a_bad_message(self):
        lines = ['{"jsonrpc":"2.0","id":1,"method":"initialize","params":[1]}', '{"jsonrpc":"2.0","id":2,"method":"ping"}']
        out = subprocess.run([sys.executable, "-m", "js3", "serve", "--no-log"], input="\n".join(lines) + "\n",
                             capture_output=True, text=True, cwd=HERE, timeout=60)
        self.assertEqual(out.returncode, 0, out.stderr[-300:])
        self.assertEqual([json.loads(l)["id"] for l in out.stdout.splitlines()], [1, 2])


class TranscriptFolder(unittest.TestCase):
    def test_a_sibling_folder_that_starts_with_transcripts_is_refused(self):
        evil = HERE / "transcripts-evil"
        try:
            with self.assertRaises(SystemExit):
                mcp_server.Server(log_dir=evil)
            self.assertFalse(evil.exists(), "nothing may be created outside transcripts/")
        finally:
            if evil.exists():
                for p in sorted(evil.rglob("*"), reverse=True):
                    p.unlink() if p.is_file() else p.rmdir()
                evil.rmdir()


if __name__ == "__main__":
    unittest.main()
