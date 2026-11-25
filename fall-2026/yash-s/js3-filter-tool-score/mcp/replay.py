"""Replay a recorded server-session transcript through the current server code and compare.

    python3 mcp/replay.py mcp/transcripts/server-session-<...>.jsonl

Sends every recorded client->server line to a fresh in-process Server, in order, and
checks that each reply is identical to the recorded server->client line. This shows
whether a transcript recorded earlier still describes the code as it is now.
Reads only the transcript and the files the server itself reads; writes nothing.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import job_filter as J  # noqa: E402
import mcp_server as M  # noqa: E402


def main(path):
    records = [json.loads(x) for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]
    server = M.Server(J.load_rules(), M.load_saved(M.DEFAULT_RESULTS))
    recorded = iter(r["raw"] for r in records if r["dir"] == "server->client")
    same = differ = 0
    for r in records:
        if r["dir"] != "client->server":
            continue
        reply = server.handle_line(r["raw"])
        if reply is None:
            continue
        now, then = json.dumps(reply, ensure_ascii=False), next(recorded, None)
        try:
            method = json.loads(r["raw"]).get("method", "?")
        except Exception:
            method = f"(malformed line: {r['raw'][:20]!r}…)"
        if now == then:
            same += 1
            print(f"identical  {method}")
        else:
            differ += 1
            print(f"DIFFERENT  {method}\n  then: {then[:300] if then else 'no reply recorded'}\n  now:  {now[:300]}")
    print(f"{same} identical, {differ} different")
    return 0 if differ == 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1]))
