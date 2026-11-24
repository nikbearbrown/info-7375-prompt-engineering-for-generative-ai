"""Job-Search Agent 2: several public job boards, one failure policy, new posting IDs only.

GATE.md and evidence/PERMISSION-BOUNDARIES.md are the spec. Build step 1 holds only the
permission layer: providers, request policy, file gate, approval, and transport.
"""

from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
