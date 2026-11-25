"""A minimal MCP client, to record one real session with mcp_server.py over stdio.

    python3 mcp_client.py KEY [KEY ...]

It starts the server as a child process, runs the handshake (initialize, notifications/initialized),
lists the tools, calls score_posting for each KEY, then sends one deliberately bad call (an unknown tool)
so the transcript shows an error too. The server logs every message in both directions to
state/mcp/transcript_<UTC>.jsonl; this client prints the same exchange to stdout.
"""
import json
import os
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def main(keys):
    proc = subprocess.Popen([sys.executable, os.path.join(HERE, "mcp_server.py")], stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, text=True)
    next_id = iter(range(1, 1000))

    def send(method, params=None, notify=False):
        msg = {"jsonrpc": "2.0", "method": method}
        if params is not None:
            msg["params"] = params
        if not notify:
            msg["id"] = next(next_id)
        print(">>", json.dumps(msg))
        proc.stdin.write(json.dumps(msg) + "\n")
        proc.stdin.flush()
        if notify:
            return None
        reply = json.loads(proc.stdout.readline())
        print("<<", json.dumps(reply)[:400])
        return reply

    send("initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                        "clientInfo": {"name": "js3-mcp-client", "version": "1.0.0"}})
    send("notifications/initialized", notify=True)
    send("tools/list")
    for key in keys:
        send("tools/call", {"name": "score_posting", "arguments": {"key": key}})
    send("tools/call", {"name": "send_application", "arguments": {"key": keys[0]}})
    proc.stdin.close()
    return proc.wait()


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
