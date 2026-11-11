"""Finished-but-wrong demonstration (GATE.md sections 7 and 8, Bug 1).

run_wrong_demo runs the real loop on two canned boards, no network: one with
postings and one whose response is {"jobs": []}. The only change from a
normal run is buggy_parse, which accepts the empty board as zero jobs, so the
run exits "finished" when it should exit "incomplete". The raw evidence and
the trace are kept, and independent_check.check_trace flags the run.
"""

import json
import os

from js2 import fetch, loop, policy

GOOD_BODY = b'{"jobs": [{"id": 101, "title": "Demo Engineer"}, {"id": 102, "title": "Demo Analyst"}]}'
EMPTY_BODY = b'{"jobs": []}'

DEMO_BOARDS = [
    {"name": "demo-good", "ats": "greenhouse", "token": "demo-good"},
    {"name": "demo-empty", "ats": "greenhouse", "token": "demo-empty"},
]
DEMO_BODIES = {"demo-good": GOOD_BODY, "demo-empty": EMPTY_BODY}

NOTES = ("WRONG-DEMO: deliberately finished-but-wrong. buggy_parse treats the empty "
         "demo-empty response as a successful check with zero jobs (GATE.md Bug 1), so "
         "this trace says finished although one board returned no postings. Kept as "
         "evidence; independent_check.check_trace must flag it.")


def buggy_parse(ats, data):
    # INTENTIONAL BUG for assignment demonstration: an empty or invalid board is
    # reported as a successful check with zero jobs instead of raising
    # loop.InvalidBoardResponse.
    jobs = data.get("jobs", []) if isinstance(data, dict) else []
    return [str(j.get("id")) for j in jobs if isinstance(j, dict)]


def run_wrong_demo(output_dir):
    """Run the buggy demo, writing raw/ and traces/ under output_dir.

    Writes still go through policy, so output_dir must be inside
    policy.ALLOWED_OUTPUT or nothing is written.

    Returns the loop trace plus exit_status (the loop's exit status string)
    and trace_path (absolute path of the written trace, or None if the
    write was blocked).
    """
    output_dir = os.path.abspath(output_dir)

    def canned(token, timeout):
        body = DEMO_BODIES[token]
        raw_path = os.path.join(output_dir, "raw", "%s-greenhouse-%s-WRONG-DEMO.json" % (fetch.utc_stamp(), token))
        decision = policy.write_bytes(raw_path, body)
        return {
            "ats": "greenhouse",
            "token": token,
            "url": fetch.greenhouse_url(token),
            "status_code": 200,
            "bytes": len(body),
            "data": json.loads(body),
            "raw_path": raw_path if decision is True else None,
            "raw_write_decision": decision,
        }

    trace = loop.run(boards=DEMO_BOARDS, fetchers={"greenhouse": canned}, output_dir=output_dir,
                     label="WRONG-DEMO", notes=NOTES, parse=buggy_parse)
    trace["exit_status"] = trace["status"]
    return trace
