"""scripts/run_blocked.py really blocks the network: a CONSTRUCTED script that tries to connect must fail."""
import os
import subprocess
import sys
import tempfile
import unittest

from agent import config


class RunBlocked(unittest.TestCase):
    def test_a_connection_attempt_fails_under_the_blocker(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = os.path.join(tmp, "tries_network.py")
            with open(script, "w") as f:
                f.write("import socket\ntry:\n    socket.create_connection(('example.com', 443), timeout=2)\n"
                        "    print('CONNECTED')\nexcept OSError as e:\n    print('BLOCKED', e)\n")
            out = subprocess.run([sys.executable, "-B", str(config.ROOT / "scripts" / "run_blocked.py"), script],
                                 capture_output=True, text=True, timeout=30).stdout
        self.assertIn("BLOCKED network blocked by run_blocked.py", out)


if __name__ == "__main__":
    unittest.main()
