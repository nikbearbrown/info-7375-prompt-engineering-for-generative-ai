"""Starts the JS3 tool server (agent/toolserver.py) by file path, so an MCP client can launch it from any folder."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from agent.toolserver import main  # noqa: E402

main()
