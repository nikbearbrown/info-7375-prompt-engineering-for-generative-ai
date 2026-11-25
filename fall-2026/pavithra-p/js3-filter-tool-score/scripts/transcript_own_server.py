"""Records a real transcript of my scripted client talking to my own server (agent/toolserver.py through serve.py).

    python3 scripts/transcript_own_server.py
"""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from agent import mcp_client as c  # noqa: E402

SCRIPT = c.opening() + [
    ("call: a close call (the HELM posting)", c.request(3, "tools/call", {"name": "score_posting", "arguments":
        {"board": "ashby:ramp", "job_id": "d8925f84-562f-470c-a5bd-4f6c20009361"}})),
    ("call: a kept posting", c.request(4, "tools/call", {"name": "score_posting", "arguments":
        {"board": "greenhouse:figma", "job_id": "5802956004"}})),
    ("call: the board that failed in this run", c.request(5, "tools/call", {"name": "score_posting", "arguments":
        {"board": "lever:no-such-board", "job_id": "1"}})),
    ("call: a job id that is not in the run", c.request(6, "tools/call", {"name": "score_posting", "arguments":
        {"board": "ashby:ramp", "job_id": "not-a-real-id"}})),
    ("call: an undeclared argument (a path)", c.request(7, "tools/call", {"name": "score_posting", "arguments":
        {"board": "ashby:ramp", "job_id": "x", "path": "../../.ssh/id_rsa"}})),
    ("call: an undeclared tool", c.request(8, "tools/call", {"name": "apply_to_job", "arguments": {"job_id": "x"}})),
    ("an undeclared method", c.request(9, "resources/list")),
    ("not JSON", "{this is not json"),
    ("ping", c.request(10, "ping")),
]

if __name__ == "__main__":
    rows, path = c.run_script([sys.executable, os.path.join(HERE, "serve.py")], HERE, SCRIPT, "own")
    for note, sent, got in rows:
        print(f"{note:45} -> {(got or '(notification: no answer)')[:150]}")
    print(f"client transcript: {os.path.relpath(path, HERE)} (the server writes its own: transcripts/server-*.jsonl)")
