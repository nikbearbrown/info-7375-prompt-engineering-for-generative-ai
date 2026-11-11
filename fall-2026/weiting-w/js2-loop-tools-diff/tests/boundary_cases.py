"""The 19 boundary cases of GATE.md §5.5, as data.

One source for both the test (`tests/test_policy_boundaries.py`) and the report
(`tools/boundary_table.py`), so the "predicted" column in
`reports/boundary-tests.md` cannot drift away from the predictions I committed
in GATE.md before running anything.

`predicted` is written exactly as the gate wrote it: `"allow"`, or
`"deny:<ExceptionClassName>"`.
"""

from __future__ import annotations

GH = "https://boards-api.greenhouse.io/v1/boards/reddit/jobs"

CASES = [
    # --- network: the three allowed hosts, one per applicant-tracking system
    dict(n=1, kind="net", method="GET", url=GH,
         desc="allowed Greenhouse host", predicted="allow"),
    dict(n=2, kind="net", method="GET", url="https://api.lever.co/v0/postings/matterport",
         desc="allowed Lever host (this token 404s; the policy decides on host, "
              "scheme, port and method only, never on whether a board exists)",
         predicted="allow"),
    dict(n=3, kind="net", method="GET",
         url="https://api.ashbyhq.com/posting-api/job-board/ramp",
         desc="allowed Ashby host", predicted="allow"),

    # --- network: refusals
    dict(n=4, kind="net", method="GET",
         url="https://boards.greenhouse.io/v1/boards/reddit/jobs",
         desc="a real Greenhouse host that is not the one on the allow-list",
         predicted="deny:DisallowedHost"),
    dict(n=5, kind="net", method="GET",
         url="https://boards-api.greenhouse.io.evil.example/v1/boards/reddit/jobs",
         desc="suffix trick: allowed host as a prefix of someone else's domain",
         predicted="deny:DisallowedHost"),
    dict(n=6, kind="net", method="GET",
         url="https://evil.example/?u=https://boards-api.greenhouse.io/",
         desc="allowed host appearing in the query string",
         predicted="deny:DisallowedHost"),
    dict(n=7, kind="net", method="GET",
         url="http://boards-api.greenhouse.io/v1/boards/reddit/jobs",
         desc="plain http to an allowed host",
         predicted="deny:DisallowedScheme"),
    dict(n=8, kind="net", method="GET",
         url="https://boards-api.greenhouse.io:8443/v1/boards/reddit/jobs",
         desc="allowed host on an unexpected port",
         predicted="deny:DisallowedPort"),
    dict(n=9, kind="net", method="POST", url=GH,
         desc="a write-shaped request to an allowed host",
         predicted="deny:MethodNotAllowed"),

    # --- filesystem: writes
    dict(n=10, kind="write", path="evidence/raw/greenhouse-reddit.json",
         desc="a new file inside the output root", predicted="allow"),
    dict(n=11, kind="write", path="evidence/../../etc/passwd",
         desc="`..` traversal out of the output root",
         predicted="deny:PathEscapes"),
    dict(n=12, kind="write", path="evidence-evil/x.json",
         desc="prefix trick: a sibling directory whose name starts with the "
              "output root's name. A startswith() check would allow this",
         predicted="deny:PathEscapes"),
    dict(n=13, kind="write", path="evidence/link/x.json", needs="symlink",
         desc="a symlink inside the output root pointing outside it",
         predicted="deny:PathEscapes"),
    dict(n=14, kind="write", path="evidence",
         desc="the output root itself", predicted="deny:PathEscapes"),

    # --- filesystem: reads, which are a separate permission
    dict(n=15, kind="read", path="data/resume.persona.json",
         desc="the validated persona resume", predicted="allow"),
    dict(n=16, kind="read", path="data/resume.real.json",
         desc="a real resume, carried over from JS1's refusal R2",
         predicted="deny:RefusedRealResume"),
    dict(n=17, kind="read", path="../../etc/passwd",
         desc="a read outside every readable subtree",
         predicted="deny:PathEscapes"),

    # --- approval
    dict(n=18, kind="write", path="evidence/raw/already-there.json", needs="existing",
         desc="overwriting saved raw evidence without approval",
         predicted="deny:NeedsApproval"),
    dict(n=19, kind="write", path="evidence/raw/already-there.json", needs="existing",
         approve=True,
         desc="the same overwrite, with --approve-overwrite",
         predicted="allow"),
]

assert len(CASES) == 19
assert [c["n"] for c in CASES] == list(range(1, 20))
