import json

from agent.watch import run
from tests.fixtures import RELEVANT
from tests.test_watch import args_for, boards, explode


def test_inconsistent_total_does_not_succeed_or_change_state(tmp_path):

    # Establish a valid baseline containing one posting.
    (baseline_file,) = boards(tmp_path, [RELEVANT])

    baseline_exit = run(
        args_for(tmp_path, baseline_file, "baseline"),
        judge_fn=explode,
    )

    assert baseline_exit == 0, "The valid baseline must succeed."

    # Preserve the complete state file for comparison.
    state_path = tmp_path / "state.json"
    state_before = state_path.read_bytes()

    # Match probe P2: one supplied posting, but a declared total of 40.
    inconsistent_file = tmp_path / "inconsistent.json"
    inconsistent_file.write_text(
        json.dumps({
            "jobs": [RELEVANT],
            "meta": {"total": 40},
        }),
        encoding="utf-8",
    )

    inconsistent_exit = run(
        args_for(tmp_path, inconsistent_file, "inconsistent"),
        judge_fn=explode,
    )

    state_after = state_path.read_bytes()

    # GATE sections 1 and 4 classify this as incomplete acquisition.
    assert inconsistent_exit == 3, (
        "GATE sections 1 and 4 require incomplete (exit 3) when "
        "meta.total declares 40 jobs but the response contains only 1; "
        f"the agent returned {inconsistent_exit}."
    )

    # Failed acquisition must not modify the previously valid state.
    assert state_after == state_before, (
        "Rejecting an inconsistent board response must leave the entire "
        "existing state file unchanged, including its run history."
    )
