"""Runs every boundary case through the real permission policy and prints a Markdown
table: the case, the student's prediction (read verbatim from BOUNDARY-PREDICTIONS.md),
what actually happened, and whether they match.

Every file is a stand-in inside a temporary folder; every request is checked by the
policy but never sent (N5 runs the loop with a simulated 301). Approvals are SIMULATED.

Usage (from the js2-loop-tools-diff folder):
  python3 policy/boundary_table.py > policy/BOUNDARY-RESULTS.md
"""

import os
import re
import subprocess
import sys
import tempfile
from pathlib import Path

PROJECT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT))

from jobwatch import loop, net  # noqa: E402
from jobwatch.errors import PolicyDenied  # noqa: E402
from jobwatch.policy import Approval, Policy  # noqa: E402

ANTHROPIC = "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs?content=true"
APPROVED = {ANTHROPIC, "https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true",
            "https://api.ashbyhq.com/posting-api/job-board/linear",
            "https://boards-api.greenhouse.io/v1/boards/jobwatch-no-such-board-js2/jobs?content=true"}
GOOD = Approval("R2", "state/state.json")

REQUESTS = [
    ("N1", "GET the configured Anthropic endpoint", "GET", ANTHROPIC),
    ("N2", "POST to that same address", "POST", ANTHROPIC),
    ("N3", "GET https://example.com/jobs", "GET", "https://example.com/jobs"),
    ("N4", "GET the Anthropic endpoint over http", "GET", ANTHROPIC.replace("https://", "http://")),
    ("N6", "GET an Ashby posting's own jobUrl", "GET",
     "https://jobs.ashbyhq.com/linear/d3bc1ced-3ce4-4086-a050-555055dbb1ff"),
    ("N7", "GET Stripe's board (allowed host, not configured)", "GET",
     "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"),
    ("X9", "GET the Anthropic path without ?content=true", "GET",
     "https://boards-api.greenhouse.io/v1/boards/anthropic/jobs"),
    ("X10", "GET with an allowed name before an @", "GET",
     "https://boards-api.greenhouse.io@example.com/v1/boards/anthropic/jobs?content=true"),
    ("X11", "GET a host that starts with an allowed name", "GET",
     "https://boards-api.greenhouse.io.example.com/v1/boards/anthropic/jobs?content=true"),
]

FILES = [
    ("F1", "read persona/alex_morgan.json", "read", "persona/alex_morgan.json", None),
    ("F2", "read state/state.json", "read", "state/state.json", None),
    ("F3", "read a file outside the project (~/Documents/resume.pdf stand-in)", "read", "<outside>/resume.pdf", None),
    ("F4", "write runs/R2/trace.json, no approval", "write", "runs/R2/trace.json", None),
    ("F5", "write runs/R1/trace.json, no approval", "write", "runs/R1/trace.json", None),
    ("F6", "write runs/R2/../R1/trace.json", "write", "runs/R2/../R1/trace.json", None),
    ("F7", "write runs-evil/R2/trace.json", "write", "runs-evil/R2/trace.json", None),
    ("F8", "write through runs/R2/out (symlink to outside)", "write", "runs/R2/out/trace.json", None),
    ("F9", "write through runs/R2/link (symlink to runs/R2/sub)", "write", "runs/R2/link/trace.json", None),
    ("F10", "write state/state.json, no approval", "write", "state/state.json", None),
    ("F11", "write state/state.json, approval for R1", "write", "state/state.json", Approval("R1", "state/state.json")),
    ("F12", "write state/state.json, approval naming state/other.json", "write", "state/state.json",
     Approval("R2", "state/other.json")),
    ("F13", "write state/state.json, approval for R2 and state/state.json", "write", "state/state.json", GOOD),
    ("F14", "write state/.state.json.tmp, the same approval", "write", "state/.state.json.tmp", GOOD),
    ("X1", "write runs/R2/sub/../trace.json (lands inside R2)", "write", "runs/R2/sub/../trace.json", None),
    ("X2", "write persona/alex_morgan.json (readable file)", "write", "persona/alex_morgan.json", GOOD),
    ("X3", "delete runs/R2/trace.json", "delete", "runs/R2/trace.json", GOOD),
    ("X4", "write state/state.json, approval = True", "write", "state/state.json", True),
    ("X5", "write state/notes.txt with the state approval", "write", "state/notes.txt", GOOD),
    ("X6", "read runs/R1/trace.json (saved evidence)", "read", "runs/R1/trace.json", None),
    ("X7", "create the folder runs/R2", "write", "runs/R2", None),
    ("X12", "read notes.txt inside the project", "read", "notes.txt", None),
    ("X13", "write runs/R2-evil/trace.json", "write", "runs/R2-evil/trace.json", None),
    ("X14", "read runs-evil/R2/trace.json", "read", "runs-evil/R2/trace.json", None),
]


def predictions():
    text = (PROJECT / "policy" / "BOUNDARY-PREDICTIONS.md").read_text(encoding="utf-8")
    block = text.split("## The student's predictions (verbatim)", 1)[1]
    found = {}
    for line in block.splitlines():
        match = re.match(r"\* (N\d+|F\d+) (allow|refuse) — (.*)", line)
        if match:
            found[match.group(1)] = (match.group(2), match.group(3))
    return found


def build_tree(base):
    root = base / "project"
    for folder in ("persona", "state", "runs/R1", "runs/R2/sub", "runs-evil/R2"):
        (root / folder).mkdir(parents=True, exist_ok=True)
    (base / "outside").mkdir()
    (base / "outside" / "resume.pdf").write_bytes(b"stand-in")
    for name in ("persona/alex_morgan.json", "state/state.json", "runs/R1/trace.json",
                 "runs-evil/R2/trace.json", "notes.txt"):
        (root / name).write_text("{}", encoding="utf-8")
    os.symlink(root / "runs" / "R2" / "sub", root / "runs" / "R2" / "link")
    os.symlink(base / "outside", root / "runs" / "R2" / "out")
    return root


def outcome(call):
    try:
        call()
        return "allow"
    except PolicyDenied as error:
        return f"refuse ({error.rule})"


def redirect_case(base):
    """N5: the Anthropic endpoint answers 301 to example.com. Simulated; nothing is sent."""
    root = base / "redirect-project"
    (root / "persona").mkdir(parents=True)
    (root / "persona" / "alex_morgan.json").write_bytes((PROJECT / "persona" / "alex_morgan.json").read_bytes())
    requested = []

    def fetch(url, deadline):
        requested.append(url)
        if url == ANTHROPIC:
            return net.Response(301, b"moved", "text/plain", "https://example.com/jobs")
        body = b'{"jobs": [{"id": 1, "title": "t", "location": {"name": "x"}, "content": "c"}]}' \
            if "greenhouse" in url else \
            b'{"apiVersion": "1", "jobs": [{"jobUrl": "u", "title": "t", "location": "x", "descriptionHtml": "c"}]}'
        return net.Response(200, body, "application/json", None)

    result = loop.run(root=root, run_id="R2", requested=["greenhouse/anthropic", "greenhouse/databricks", "ashby/linear"],
                      fetch=fetch)
    anthropic = next(b for b in result["boards"] if b["board"] == "greenhouse/anthropic")
    followed = "https://example.com/jobs" in requested
    verdict = "refuse (redirect not followed)" if not followed else "allow (FOLLOWED)"
    detail = f"board {anthropic['outcome']}; run {result['status']}; example.com requested: {followed}"
    return verdict, detail


def main():
    said = predictions()
    commit = subprocess.run(["git", "-C", str(PROJECT), "rev-parse", "--short", "HEAD"],
                            capture_output=True, text=True).stdout.strip() or "unknown"
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp).resolve()
        root = build_tree(base)
        for case, what, method, url in REQUESTS:
            rows.append((case, what, outcome(lambda: Policy(root, "R2", APPROVED).check_request(method, url)), ""))
        verdict, detail = redirect_case(base)
        rows.insert(4, ("N5", "follow a 301 from the Anthropic endpoint to example.com", verdict, detail))
        for case, what, operation, path, approval in FILES:
            target = path.replace("<outside>", str(base / "outside"))
            rows.append((case, what, outcome(lambda: Policy(root, "R2", APPROVED, approval).check_file(operation, target)), ""))

    lines = [
        "# Boundary results — the permission policy, run",
        "",
        f"Generated by `python3 policy/boundary_table.py` at commit `{commit}`. Each case ran through the real "
        "`jobwatch.policy.Policy` (N5 through `jobwatch.loop.run` with a simulated 301), in a temporary folder of "
        "stand-in files, with SIMULATED approvals; no request was sent. The predictions are the student's, copied "
        "from [BOUNDARY-PREDICTIONS.md](BOUNDARY-PREDICTIONS.md) (committed before any policy code, `f871ccb`). "
        "X cases were added by Claude Code; their expected results were written into `tests/test_policy.py` "
        "before the policy code existed (`7db4ab4`).",
        "",
        "| Case | The agent tries to… | Student's prediction | Actual (rule that fired) | Match | Note |",
        "|---|---|---|---|---|---|",
    ]
    for case, what, actual, note in rows:
        if case in said:
            verdict, reason = said[case]
            predicted = f"{verdict}: {reason}"
            match = "yes" if actual.split(" ")[0] == verdict else "**NO**"
        else:
            predicted, match = "— (Claude Code's case)", "—"
        lines.append(f"| {case} | {what} | {predicted} | {actual} | {match} | {note} |")
    lines.append("")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
