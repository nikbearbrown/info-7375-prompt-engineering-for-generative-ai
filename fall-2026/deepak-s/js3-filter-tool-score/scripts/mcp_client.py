"""A scripted stdio client for MCP-style servers, stdlib only (Phase 5 tests and the Phase 5e run).

    client = StdioClient(argv, cwd, env, transcript_path)
    client.send(obj_or_raw_line)            # one line to the server's stdin (logged "out")
    client.request(method, params, id_)     # send, then wait for the response with that id
    client.close()                          # close stdin, wait for exit

Every line the client writes and every line it reads from the server's stdout is appended,
verbatim, with the UTC time and the direction ("out" = client to server, "in" = server to client),
to `transcript_path` (JSON lines). The server's stderr is captured separately.
"""
import json
import queue
import subprocess
import threading
from datetime import datetime, timezone


def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.%fZ")


class StdioClient:
    def __init__(self, argv, cwd, env, transcript_path, timeout=30):
        self.timeout = timeout
        self.transcript = open(transcript_path, "a", encoding="utf-8")
        self.log("note", "client start: " + " ".join(argv))
        self.proc = subprocess.Popen(argv, cwd=cwd, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                     stderr=subprocess.PIPE, text=True, bufsize=1)
        self.lines = queue.Queue()
        self.stderr = []
        threading.Thread(target=self._read, daemon=True).start()
        threading.Thread(target=self._read_err, daemon=True).start()

    def log(self, direction, line):
        self.transcript.write(json.dumps({"t": now(), "dir": direction, "line": line}, ensure_ascii=False) + "\n")
        self.transcript.flush()

    def _read(self):
        for line in self.proc.stdout:
            line = line.rstrip("\n")
            self.log("in", line)
            self.lines.put(line)
        self.lines.put(None)

    def _read_err(self):
        for line in self.proc.stderr:
            self.stderr.append(line)

    def send(self, msg):
        line = msg if isinstance(msg, str) else json.dumps(msg, separators=(",", ":"))
        self.log("out", line)
        self.proc.stdin.write(line + "\n")
        self.proc.stdin.flush()

    def next_message(self, timeout=None):
        line = self.lines.get(timeout=timeout or self.timeout)
        return None if line is None else json.loads(line)

    def wait_for(self, id_, timeout=None):
        while True:
            msg = self.next_message(timeout)
            if msg is None:
                raise EOFError("server closed stdout")
            if msg.get("id") == id_ and ("result" in msg or "error" in msg):
                return msg

    def request(self, method, params=None, id_=1, timeout=None):
        msg = {"jsonrpc": "2.0", "id": id_, "method": method}
        if params is not None:
            msg["params"] = params
        self.send(msg)
        return self.wait_for(id_, timeout)

    def silent_for(self, seconds):
        """True if the server writes nothing for `seconds` (used to show a notification gets no reply)."""
        try:
            self.lines.get(timeout=seconds)
            return False
        except queue.Empty:
            return True

    def close(self):
        try:
            self.proc.stdin.close()
        except OSError:
            pass
        code = self.proc.wait(timeout=self.timeout)
        self.log("note", f"server exit code {code}")
        self.transcript.close()
        return code
