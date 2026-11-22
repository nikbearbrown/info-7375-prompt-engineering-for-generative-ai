"""Launch the JS3 tool server from anywhere (an MCP client starts it as a subprocess).

    python scripts/run_mcp_server.py                 # serves this folder's snapshots
    python scripts/run_mcp_server.py --root DIR      # serves another folder (it needs FILTER.md and runs/*-live/);
                                                     # used only by scripts/injection_test.py on a SEEDED copy
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from js3.mcp_server import serve  # noqa: E402

root = Path(sys.argv[sys.argv.index("--root") + 1]).resolve() if "--root" in sys.argv else ROOT
serve(root=root)
