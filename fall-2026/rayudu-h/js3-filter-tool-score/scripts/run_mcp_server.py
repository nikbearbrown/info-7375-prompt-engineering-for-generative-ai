"""Launch the JS3 tool server from anywhere (an MCP client starts it as a subprocess).

    python scripts/run_mcp_server.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from js3.mcp_server import serve  # noqa: E402

serve(root=ROOT)
