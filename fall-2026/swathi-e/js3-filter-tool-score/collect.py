"""LIVE collection run for JS3: the JS2 loop, unchanged, with Greenhouse descriptions.

    python3 collect.py     # network: the four GATE.md boards, one request each

It calls loop.run_loop with job_filter.JS3_URLS (Greenhouse ?content=true; Ashby
as before), the same boards, budgets, permission policy and live transport. Raw
responses and the trace are saved under runs/<time>/ and state/seen_ids.json is
updated, exactly as in JS2. The deliberate bad board still fails with a 404, so
the run ends "incomplete" (exit code 1). The filter is not run here: run_filter.py
reads the saved raw responses afterwards.
"""
from pathlib import Path
import sys
import time

import job_filter
import loop
import policy as policy_module

HERE = Path(__file__).resolve().parent


def main():
    pol = policy_module.Policy(HERE)
    result = loop.run_loop(loop.BOARDS, loop.BUDGETS, policy=pol, transport=loop.live_transport(pol),
                           clock=time.monotonic, sleep=time.sleep, urls=job_filter.JS3_URLS)
    print("LIVE collection run (JS3, descriptions included)")
    loop.print_summary(result)
    return 0 if result.exit == "finished" else 1


if __name__ == "__main__":
    sys.exit(main())
