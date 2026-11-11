"""CONTRACT Wrong version 1 — a verdict attached to the wrong posting.

Two postings with opposite expected verdicts go through one real run; if labels were matched by
position instead of posting_id, the counts and format would still look right, so the test checks
each id's own verdict, in both input orders.
"""

import pytest
from fakes import GOOD, SENIOR, board, by_id, job, run_once


@pytest.mark.parametrize("order", ["good_first", "senior_first"])
def test_each_posting_id_gets_its_own_verdict(paths, order):
    good, senior = job(101, **GOOD), job(202, **SENIOR)
    jobs = [good, senior] if order == "good_first" else [senior, good]
    run_once(paths, board(job(1)), n=0)          # baseline: only id 1 seen
    verdicts = by_id(run_once(paths, board(job(1), *jobs), n=1))

    assert set(verdicts) == {101, 202}
    assert verdicts[101]["verdict"] == "relevant"
    assert verdicts[202]["verdict"] == "not_relevant"
    # The reason must be about *this* posting's title, not the other one's.
    assert verdicts[202]["justification"][-1]["result"] == "match: senior"
    assert verdicts[101]["justification"][0]["result"] == "no match"
