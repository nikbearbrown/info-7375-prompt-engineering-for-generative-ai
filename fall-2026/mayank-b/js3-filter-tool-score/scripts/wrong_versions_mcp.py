"""Planted wrong MCP servers: each one must FAIL the lifecycle table that the real server passes.

    python3 -I scripts/wrong_versions_mcp.py [--corpus <run dir>]   # exit 0 only if every wrong version is caught

WF6   sets `ready` inside initialize (skips notifications/initialized). Chapter 8: this change leaves all six
      of the lesson's tests passing; the row that catches it is tools/list after initialize, before the
      notification (step 3 of the table in transcripts/EXPECTED-A.md).
M2    answers an unknown posting id with a protocol error (-32602) instead of a result with isError true,
      collapsing "the task found nothing" into "the request was malformed" (step 7).
M3    accepts a second initialize and resets readiness (silent session reset; steps 15-16).

The wrong versions are subclasses of the real Server that override one method each; nothing is copied.
These are planted test doubles, never run as an MCP server for any client.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT / "src"))
sys.path.insert(0, str(PROJECT / "scripts"))

from jsa3 import corpus as corpus_mod  # noqa: E402
from jsa3 import mcp_server  # noqa: E402
import mcp_record  # noqa: E402

FIXTURE = PROJECT / "tests" / "fixtures" / "mcp-run"


class ReadyOnInitialize(mcp_server.Server):
    """WF6."""

    def _initialize(self, ident, params):
        reply = super()._initialize(ident, params)
        if "result" in reply:
            self.ready = True
        return reply


class UnknownIdAsProtocolError(mcp_server.Server):
    """M2."""

    def _call(self, ident, params):
        reply = super()._call(ident, params)
        if reply.get("result", {}).get("isError"):
            return mcp_server._err(ident, mcp_server.INVALID_PARAMS, "Unknown posting id")
        return reply


class ReinitializeResets(mcp_server.Server):
    """M3."""

    def _initialize(self, ident, params):
        if self.initialized:
            self.initialized = self.ready = False
        return super()._initialize(ident, params)


WRONG = {"WF6": ReadyOnInitialize, "M2": UnknownIdAsProtocolError, "M3": ReinitializeResets}


def check(cls, corpus, cfg, pid):
    """-> the step numbers where `cls` disagrees with the predicted table (empty = passes)."""
    results = mcp_record.run_in_process(lambda: cls(corpus, cfg), "own", pid)
    return [r["n"] for r in results if r["verdict"] != "match"]


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", default=str(FIXTURE))
    args = ap.parse_args(argv)
    corpus = corpus_mod.load(args.corpus)
    cfg = json.loads((PROJECT / "config" / "filter.json").read_text(encoding="utf-8"))
    pid, _ = mcp_record.pick_posting(corpus, cfg)
    ok = True
    real = check(mcp_server.Server, corpus, cfg, pid)
    print(f"real Server: failing steps {real or 'none'}")
    ok &= not real
    for name, cls in WRONG.items():
        failing = check(cls, corpus, cfg, pid)
        print(f"{name} {cls.__name__}: failing steps {failing or 'none (NOT CAUGHT)'}")
        ok &= bool(failing)
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
