"""Scripted MCP client for tool/server.py: one normal and one adversarial session.

Standard library only. It starts the server as a subprocess, speaks
newline-delimited JSON-RPC 2.0 on its stdin/stdout, and prints a short
summary of each exchange. The server writes the transcripts itself; this
client never opens them.

Run from the js3-filter-tool-score directory:

    python3 tool/client.py

Exit code 0 means every response matched what the contract and its
amendment say; 1 means at least one did not (each mismatch is printed).
"""

import json
import os
import select
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent.parent  # used as cwd only; never printed
SERVER = Path("tool") / "server.py"
TIMEOUT = 10.0
PROTOCOL_VERSION = "2025-11-25"
CLIENT_INFO = {"name": "js3-scripted-client", "version": "1.0.0"}

SHORTLISTED = ("databricks", "6865698002")
REJECTED = ("stripe", "8172508")
CANNOT_TELL = ("stripe", "5601881")
PLAID = ("plaid", "5d8abedc-018a-4b42-ae1f-0e70b34f2007")

problems = []


def check(ok, what):
    print(f"    {'ok  ' if ok else 'FAIL'} {what}")
    if not ok:
        problems.append(what)


class Session:
    def __init__(self, label):
        self.label = label
        self.proc = subprocess.Popen([sys.executable, str(SERVER)], cwd=str(HERE), stdin=subprocess.PIPE,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        self.buffer = b""
        self.next_id = 0

    def send_raw(self, text):
        self.proc.stdin.write(text.encode("utf-8") + b"\n")
        self.proc.stdin.flush()

    def send(self, method, params=None, notify=False):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            msg["id"] = self.next_id
            self.next_id += 1
        self.send_raw(json.dumps(msg))
        return msg.get("id")

    def call(self, board, posting_id, name="score_posting"):
        return self.send("tools/call", {"name": name, "arguments": {"board": board, "posting_id": posting_id}})

    def receive(self):
        deadline = time.monotonic() + TIMEOUT
        fd = self.proc.stdout.fileno()
        while b"\n" not in self.buffer:
            left = deadline - time.monotonic()
            if left <= 0 or not select.select([fd], [], [], left)[0]:
                raise TimeoutError("no response from the server")
            chunk = os.read(fd, 65536)
            if not chunk:
                raise EOFError("the server closed stdout")
            self.buffer += chunk
        line, self.buffer = self.buffer.split(b"\n", 1)
        return json.loads(line)

    def request(self, method, params=None):
        id_ = self.send(method, params)
        response = self.receive()
        check(response.get("id") == id_, f"{method}: response id {id_}")
        return response

    def finish(self):
        """End of input: close stdin and wait for the server to exit."""
        self.proc.stdin.close()
        rest = self.proc.stdout.read()
        code = self.proc.wait(timeout=TIMEOUT)
        stderr = self.proc.stderr.read().decode("utf-8", "replace")
        self.proc.stdout.close()
        self.proc.stderr.close()
        check(rest == b"", "no further stdout after end of input")
        check(code == 0, f"server exit code {code}")
        names = [line.split(": ", 1)[1] for line in stderr.splitlines() if line.startswith("transcript: ")]
        check(len(names) == 1, "server reported one transcript on stderr")
        print(f"  transcript: {names[0] if names else '(none)'}")
        return names[0] if names else None


def initialize(session):
    response = session.request("initialize", {"protocolVersion": PROTOCOL_VERSION, "capabilities": {},
                                              "clientInfo": CLIENT_INFO})
    check(response.get("result", {}).get("protocolVersion") == PROTOCOL_VERSION,
          f"initialize: protocolVersion {PROTOCOL_VERSION}")
    session.send("notifications/initialized", notify=True)


def tool_text(response):
    content = response.get("result", {}).get("content") or [{}]
    return content[0].get("text", "")


def normal():
    print("Session 1: normal")
    s = Session("normal")
    initialize(s)
    tools = s.request("tools/list").get("result", {}).get("tools", [])
    check([t.get("name") for t in tools] == ["score_posting"], "tools/list: exactly score_posting")
    for (board, posting_id), expected in ((SHORTLISTED, "shortlisted"), (REJECTED, "rejected"),
                                          (CANNOT_TELL, "I cannot tell"), (PLAID, None)):
        s.call(board, posting_id)
        response = s.receive()
        result = response.get("result", {})
        record = result.get("structuredContent", {}).get("record", {})
        verdict = record.get("verdict")
        print(f"  score_posting {board} {posting_id}: isError {result.get('isError')}, verdict {verdict!r}, "
              f"score {record.get('score')}")
        check(result.get("isError") is False, f"{board} {posting_id}: isError false")
        if expected is not None:
            check(verdict == expected, f"{board} {posting_id}: verdict {expected!r}")
    check(s.request("ping").get("result") == {}, "ping: empty result")
    return s.finish()


def adversarial():
    print("Session 2: adversarial")
    s = Session("adversarial")
    initialize(s)

    response = s.request("tools/call", {"name": "read_file", "arguments": {"path": "../../etc/passwd"}})
    print(f"  unknown tool read_file: error {response.get('error')}")
    check(response.get("error", {}).get("code") == -32602, "unknown tool: -32602")

    s.call("stripe", "../../etc/passwd")
    response = s.receive()
    print(f"  path-like posting_id: isError {response['result'].get('isError')}, text {tool_text(response)!r}")
    check(response["result"].get("isError") is True and "root:" not in tool_text(response),
          "path-like posting_id: isError true, no file contents")

    s.call("databricks", "1234567890")
    response = s.receive()
    print(f"  unknown posting: isError {response['result'].get('isError')}, text {tool_text(response)!r}")
    check(response["result"].get("isError") is True and "unknown posting" in tool_text(response),
          "unknown posting: isError true")

    s.send_raw('{"jsonrpc": "2.0", "id": 900, "method": "ping"')
    response = s.receive()
    print(f"  malformed JSON: id {response.get('id')}, error {response.get('error')}")
    check(response.get("id") is None and response.get("error", {}).get("code") == -32700, "malformed JSON: -32700")

    response = s.request("initialize", {"protocolVersion": PROTOCOL_VERSION, "capabilities": {},
                                        "clientInfo": CLIENT_INFO})
    print(f"  second initialize: error {response.get('error')}")
    check(response.get("error") == {"code": -32600, "message": "already initialized"},
          "second initialize: -32600 already initialized")

    # The two argument calls above count toward the limit; wait for them to leave the window.
    time.sleep(1.1)
    ids = [s.call(*SHORTLISTED) for _ in range(25)]
    responses = [s.receive() for _ in ids]
    flags = [r.get("result", {}).get("isError") for r in responses]
    refused = [r for r in responses if r.get("result", {}).get("isError")]
    print(f"  burst of 25 calls: {flags.count(False)} served, {len(refused)} refused"
          + (f"; first refusal text {tool_text(refused[0])!r}" if refused else ""))
    check([r.get("id") for r in responses] == ids, "burst: response ids in order")
    check(flags == [False] * 20 + [True] * 5, "burst: calls 1-20 served, 21-25 refused")
    check(all("rate limit exceeded" in tool_text(r) for r in refused), "burst: refusals say rate limit exceeded")

    time.sleep(1.1)
    s.call(*SHORTLISTED)
    response = s.receive()
    print(f"  call after the window: isError {response['result'].get('isError')}")
    check(response["result"].get("isError") is False, "after the window: served again")
    return s.finish()


def main():
    names = [normal(), adversarial()]
    print("Transcripts written by the server:")
    for name in names:
        print(f"  {name}")
    if problems:
        print(f"{len(problems)} mismatch(es)")
        return 1
    print("All responses matched the contract.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
