#!/usr/bin/env python3
"""Entry point for the JS2 loop, reused for the JS3 fetch: python3 agent.py run --label content"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from jsa.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
