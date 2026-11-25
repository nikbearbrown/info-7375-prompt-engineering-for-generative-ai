"""Launcher for the JS3 tool server, runnable from any working directory (an MCP client starts it by path)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from jobfilter.serve_tool import main  # noqa: E402

raise SystemExit(main())
