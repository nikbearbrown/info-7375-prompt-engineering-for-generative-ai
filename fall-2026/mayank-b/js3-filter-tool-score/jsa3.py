#!/usr/bin/env python3
"""JS3 entry point: python3 jsa3.py {filter,draw,audit-sheet,audit-summary,boilerplate,shortlist,measure} ... (see src/jsa3/cli.py)"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
from jsa3.cli import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
