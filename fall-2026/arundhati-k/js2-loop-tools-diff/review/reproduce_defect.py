"""Reproduce the review-packet defect, offline.

Defect: the board-name rule carried over from JS1 (^[a-z0-9-]{1,64}$) rejects real Ashby board names that
contain capitals or spaces, e.g. "Jasper AI" (live: https://api.ashbyhq.com/posting-api/job-board/Jasper%20AI
returned HTTP 200 with 7 postings on 2026-11-10; "jasper-ai" and "jasperai" returned 404). Because the
rejection happens in the config check, adding that one board turns the whole run into exit "error" and
none of the other boards are fetched.

    python3 review/reproduce_defect.py      (from the js2-loop-tools-diff folder)
Exit status 1 while the defect is present, 0 once it is fixed.
"""

import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from jsagent2 import providers  # noqa: E402
from jsagent2.loop import run_loop  # noqa: E402
from jsagent2.policy import Policy  # noqa: E402

try:
    url = providers.url_for("ashby", "Jasper AI")
    print(f"url_for('ashby', 'Jasper AI') -> {url}")
except ValueError as e:
    url = None
    print(f"url_for('ashby', 'Jasper AI') -> ValueError: {e}")

calls = []


def stub(u, timeout):  # constructed responses: every board returns one posting
    calls.append(u)
    return 200, b'{"jobs": [{"id": 1, "title": "x"}]}'


root = Path(tempfile.mkdtemp())
(root / "out").mkdir()
boards = [{"name": "Stripe", "ats": "greenhouse", "slug": "stripe"},
          {"name": "Notion", "ats": "ashby", "slug": "notion"},
          {"name": "Jasper AI", "ats": "ashby", "slug": "Jasper AI"}]
budgets = {"max_boards": 5, "max_requests": 8, "max_seconds": 120, "request_timeout_seconds": 30, "retry_delay_seconds": 2}
res = run_loop(boards, budgets, Policy(root), stub, run_id="repro")
print(f"run with Stripe + Notion + Jasper AI -> exit={res.exit!r} reason={res.reason!r} requests sent={len(calls)}")
ok = url is not None and res.exit == "finished" and len(calls) == 3
print("DEFECT FIXED" if ok else "DEFECT PRESENT")
sys.exit(0 if ok else 1)
