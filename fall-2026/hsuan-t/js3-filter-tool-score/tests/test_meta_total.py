"""JS2 Step 8 (review packet, R31-R32): a Greenhouse list whose length disagrees with its own
`meta.total` must not end `ok`.

Why this file exists: the Step 7 demo (demo/finished_wrong/) shows the agent ending `finished` with
"0 new" on a list that is 86 postings short of the board's own count. Only the separate
checks/total_check.py caught it. These tests pin the behaviour Isaac chose (JS2 D21) and were
committed failing, BEFORE Claude's patch, so the patch is judged against them and not the reverse.

Expected behaviour, decided by Isaac before any patch (D21):
- jobs != meta.total, either direction -> the board ends `failed` with new code 203 (validate stage,
  not retried, board scope), no job count, state untouched, run not `finished`.
- no meta.total at all (Ashby never has one) -> can't check, the board is handled as before.

Drafted by Claude at Isaac's request; expected outcomes are Isaac's (D21).
"""

import json
from pathlib import Path

import pytest
from fakes import board, board_row, job
from test_loop import four_boards, run_all

from job_agent.loop import codes, exits

SEEDED = Path(__file__).parent.parent / "demo/finished_wrong/out/evidence/raw/seeded/stripe_missing_new_postings.json"


def greenhouse_body(jobs: list[dict], meta) -> bytes:
    """A Greenhouse response with a chosen `meta`; fakes.board() always makes meta.total = len(jobs)."""
    doc = {"jobs": jobs}
    if meta is not None:
        doc["meta"] = meta
    return json.dumps(doc).encode()


@pytest.mark.parametrize("n_jobs, total", [(1, 2), (2, 1)], ids=["list-shorter", "list-longer"])
def test_list_length_not_equal_to_meta_total_fails_the_board(paths, n_jobs, total):
    run_all(paths, four_boards(), n=0)                       # baseline: stripe has seen job 1
    stripe_before = paths.state("stripe").read_text()

    body = greenhouse_body([job(i) for i in range(1, n_jobs + 1)], {"total": total})
    outcome, doc = run_all(paths, four_boards(stripe=[body]), n=1)

    row = board_row(doc)
    assert (row["status"], row["code"], row["fetched"], row["new"]) == ("failed", "203", None, None)
    assert paths.state("stripe").read_text() == stripe_before   # a list we can't trust changes nothing
    assert outcome.exit == exits.INCOMPLETE                      # stripe failed, the other boards ok
    assert not [v for v in doc["verdicts"] if v["board"] == "stripe"]


def test_code_203_is_a_board_scoped_validation_error_with_no_retry():
    c = codes.CODES["203"]
    assert (c.stage, c.retryable, c.scope) == ("validate", False, "board")


@pytest.mark.parametrize("meta", [None, {}], ids=["no-meta", "meta-without-total"])
def test_missing_meta_total_is_not_checked(paths, meta):
    outcome, doc = run_all(paths, four_boards(stripe=[greenhouse_body([job(1), job(2)], meta)]))
    row = board_row(doc)
    assert (row["status"], row["code"], row["fetched"]) == ("ok", None, 2)


def test_equal_total_is_still_ok(paths):
    _, doc = run_all(paths, four_boards(stripe=[board(job(1), job(2))]))
    assert board_row(doc)["status"] == "ok"


def test_step7_seeded_response_now_fails_instead_of_finishing(paths):
    """The real Step 7 input: 680 jobs, meta.total 766. Before the patch the agent said `finished`, 0 new."""
    body = SEEDED.read_bytes()
    data = json.loads(body)
    assert (len(data["jobs"]), data["meta"]["total"]) == (680, 766)   # the file is what the demo says

    outcome, doc = run_all(paths, four_boards(stripe=[body]))
    row = board_row(doc)
    assert (row["status"], row["code"], row["fetched"]) == ("failed", "203", None)
    assert outcome.exit != exits.FINISHED
