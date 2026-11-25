"""The protocol probe stub. Written by Claude Code (claude-opus-5-5), 2026-11-25. SEEDED input."""
import io
import json

import js3kit  # noqa: F401
from jobwatch import mcp_probe


def test_probe_logs_every_line_verbatim_and_never_replies(tmp_path, capsys):
    mcp_probe.main(str(tmp_path), stdin=io.StringIO('{"jsonrpc":"2.0","id":0,"method":"SEEDED"}\nnot json\n'))
    (f,) = list((tmp_path / "evidence" / "mcp" / "probe").glob("*.jsonl"))
    recs = [json.loads(x) for x in f.read_text().splitlines()]
    assert [r["line"] for r in recs if r["dir"] == "in"] == ['{"jsonrpc":"2.0","id":0,"method":"SEEDED"}', "not json"]
    assert capsys.readouterr().out == ""
