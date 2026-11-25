"""Records a real transcript of my scripted client (unchanged) talking to another student's tool server.

The other server: Lavanya Rajesh's "js3-postings" (fall-2026/lavanya-r/js3-filter-tool-score/mcp/server.py in the
course repository, folder at commit d32b8bc, 2026-11-25). I read server.py and agent/corpus.py before running it.
It runs from a copy made with `git archive` outside this folder; nothing of it is copied into my folder.

    python3 scripts/transcript_other_server.py /path/to/the/copy/of/lavanya-r/js3-filter-tool-score
"""
import os
import sys

HERE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, HERE)

from agent import mcp_client as c  # noqa: E402

SCRIPT = c.opening() + [
    ("call: an ordinary search", c.request(3, "tools/call", {"name": "search_postings", "arguments":
        {"query": "backend engineer", "limit": 3}})),
    ("call: a word that is also something else", c.request(4, "tools/call", {"name": "search_postings", "arguments":
        {"query": "Helm", "limit": 5}})),
    ("call: regex characters in the query", c.request(5, "tools/call", {"name": "search_postings", "arguments":
        {"query": ".*", "limit": 2}})),
    ("call: an undeclared argument (a path)", c.request(6, "tools/call", {"name": "search_postings", "arguments":
        {"query": "python", "path": "../../.ssh/id_rsa"}})),
    ("call: limit above the declared maximum", c.request(7, "tools/call", {"name": "search_postings", "arguments":
        {"query": "python", "limit": 1000}})),
    ("call: a board that is not in its corpus", c.request(8, "tools/call", {"name": "search_postings", "arguments":
        {"query": "python", "board": "../../etc"}})),
    ("call: an undeclared tool", c.request(9, "tools/call", {"name": "apply_to_job", "arguments": {"job_id": "x"}})),
    ("call: before checking the count it declares", c.request(10, "tools/call", {"name": "search_postings",
        "arguments": {"query": "the", "limit": 1}})),
    ("an undeclared method", c.request(11, "resources/list")),
    ("initialize again, with a newer protocol version", c.request(12, "initialize", {"protocolVersion": "2025-11-25",
        "capabilities": {}, "clientInfo": {"name": "js3-scripted-client", "version": "1.0"}})),
    ("not JSON", "{this is not json"),
]

if __name__ == "__main__":
    other = os.path.abspath(sys.argv[1])
    rows, path = c.run_script([sys.executable, "-B", os.path.join(other, "mcp", "server.py")], other, SCRIPT, "other-lavanya-r")
    for note, sent, got in rows:
        print(f"{note:48} -> {(got or '(notification: no answer)')[:170]}")
    print(f"client transcript: {os.path.relpath(path, HERE)}")
