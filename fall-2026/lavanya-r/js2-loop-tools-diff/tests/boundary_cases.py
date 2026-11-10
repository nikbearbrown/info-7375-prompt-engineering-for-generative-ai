"""The 14 boundary cases from PREDICTIONS.md, plus extras, with the outcome
GATE.md section 5 requires. Used by tests/test_policy_boundary.py and by
review/boundary_table.py (which prints predicted vs actual).

`expected` is what GATE.md says, NOT my prediction: where the two differ
(case 3), the prediction was wrong, and PREDICTIONS.md says so.
"""

import os
import pathlib
import tempfile

from agent.policy import ALLOW, ASK, REFUSE, Policy

CASES = [
    # n, op, target, expected
    (1, "url", "https://boards-api.greenhouse.io/v1/boards/databricks/jobs", ALLOW),
    (2, "url", "https://boards-api.greenhouse.io.evil.example/v1/boards/x/jobs", REFUSE),
    (3, "url", "http://api.lever.co/v0/postings/palantir", REFUSE),
    (4, "url", "https://www.linkedin.com/jobs/", REFUSE),
    (5, "write", "runs/trace.json", ALLOW),
    (6, "write", "runs/../GATE.md", REFUSE),
    (7, "write", "runs-evil/x.json", REFUSE),
    (8, "write", "runs/link/x.json", REFUSE),        # runs/link -> outside dir
    (9, "write", "{OUTSIDE}/x.json", REFUSE),
    (10, "read", "../js1-contract-and-watch/state/databricks-seen_ids.json", ALLOW),
    (11, "write", "../js1-contract-and-watch/state/databricks-seen_ids.json", REFUSE),
    (12, "write", "state/greenhouse-databricks.json", ASK),   # file exists
    (13, "write_no_approval", "state/greenhouse-databricks.json", REFUSE),
    (14, "action", "apply", REFUSE),
]

EXTRA = [
    ("url", "https://api.lever.co@evil.example/v0/postings/x", REFUSE),   # userinfo trick
    ("url", "https://api.ashbyhq.com:8443/posting-api/job-board/x", REFUSE),
    ("url", "https://evilgreenhouse.io/v1/boards/x/jobs", REFUSE),
    ("url", "https://API.LEVER.CO/v0/postings/palantir", ALLOW),        # hosts are case-insensitive
    ("url_post", "https://api.lever.co/v0/postings/palantir", REFUSE),
    ("action", "email", REFUSE),
    ("action", "message", REFUSE),
    ("action", "login", REFUSE),
    ("action", "delete_file", REFUSE),
    ("action", "fetch_board", ALLOW),
    ("write", "state/new-board.json", ALLOW),       # new state file: no approval needed
    ("write", "runs/a/b/c.json", ALLOW),
    ("write", "runs", REFUSE),                      # the folder itself
    ("write", "runs/finallink", REFUSE),            # final component is a symlink to outside
    ("read", "{OUTSIDE}/secret.txt", REFUSE),
    ("read", "GATE.md", ALLOW),
]


def sandbox():
    """A throwaway copy of the folder layout: <tmp>/lavanya-r/js2 (root),
    <tmp>/lavanya-r/js1-contract-and-watch, and <tmp>/outside."""
    tmp = pathlib.Path(tempfile.mkdtemp(prefix="js2-boundary-"))
    root = tmp / "lavanya-r" / "js2-loop-tools-diff"
    js1 = tmp / "lavanya-r" / "js1-contract-and-watch"
    outside = tmp / "outside"
    for d in (root / "runs", root / "state", root / "runs-evil",
              js1 / "state", outside):
        d.mkdir(parents=True)
    (root / "GATE.md").write_text("gate\n")
    (root / "state" / "greenhouse-databricks.json").write_text("{}\n")
    (js1 / "state" / "databricks-seen_ids.json").write_text("{}\n")
    (outside / "secret.txt").write_text("not mine\n")
    os.symlink(outside, root / "runs" / "link")
    os.symlink(outside / "planted.json", root / "runs" / "finallink")
    return tmp, Policy(root), outside


def outcome(policy, outside, op, target):
    target = target.replace("{OUTSIDE}", str(outside))
    if op == "url":
        return policy.decide_url(target).outcome
    if op == "url_post":
        return policy.decide_url(target, "POST").outcome
    if op == "read":
        return policy.decide_read(target).outcome
    if op == "write":
        return policy.decide_write(target).outcome
    if op == "write_no_approval":
        d = policy.decide_write(target).outcome
        return REFUSE if d == ASK else d       # no approver == no
    if op == "action":
        return policy.decide_action(target).outcome
    raise ValueError(op)
