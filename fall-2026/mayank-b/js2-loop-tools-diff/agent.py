#!/usr/bin/env python3
"""Entry point: python3 agent.py run [--plan config/boards.json] | python3 agent.py approve <run-id> --approve-state <run-id> [--ack <ats>/<slug>]"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from jsa.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
