"""My scripted MCP client gives up on a server that never answers, instead of hanging (found with claude mcp serve)."""
import os
import sys
import tempfile
import unittest

from agent import config, mcp_client


class NoAnswer(unittest.TestCase):
    def test_a_silent_server_is_recorded_as_no_answer(self):
        with tempfile.TemporaryDirectory() as tmp:
            silent = os.path.join(tmp, "silent.py")
            with open(silent, "w") as f:  # CONSTRUCTED: reads requests and never answers
                f.write("import sys, time\nfor line in sys.stdin:\n    time.sleep(0.01)\n")
            rows, path = mcp_client.run_script([sys.executable, silent], tmp, [("ping", mcp_client.request(1, "ping"))],
                                               "test-silent", answer_timeout=1, timeout=5)
        try:
            self.assertEqual(rows[0][2], "(no answer within 1 s)")
        finally:
            os.unlink(path)


class NeverExits(unittest.TestCase):
    def test_a_server_that_ignores_the_end_of_its_input_is_stopped(self):
        import time
        with tempfile.TemporaryDirectory() as tmp:
            stuck = os.path.join(tmp, "stuck.py")
            with open(stuck, "w") as f:  # CONSTRUCTED: never answers and never exits on its own
                f.write("import sys, time\nsys.stdin.read()\ntime.sleep(60)\n")
            start = time.monotonic()
            rows, path = mcp_client.run_script([sys.executable, stuck], tmp, [("ping", mcp_client.request(1, "ping"))],
                                               "test-stuck", answer_timeout=1, timeout=2)
            took = time.monotonic() - start
        try:
            self.assertLess(took, 15)
            self.assertEqual(rows[0][2], "(no answer within 1 s)")
        finally:
            os.unlink(path)


if __name__ == "__main__":
    unittest.main()
