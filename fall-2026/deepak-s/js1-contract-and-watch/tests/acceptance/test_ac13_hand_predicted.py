"""Case 13. Cases and expected verdicts drafted with Claude (chat), hand-checked and adopted by Deepak on 2026-10-29; code typed by Claude Code from his answers on 2026-10-29, before any implementation."""
from datetime import timedelta

from conftest import BOARD_URL, FIXED_NOW, FakeOpener, board_body, job, latest_report, run_args, run_cli

# Constructed postings (title, location) and the verdicts predicted by hand before any code existed.
PREDICTED = [
    (job(1301, "Machine Learning Engineer, Payments", "New York, NY"), "relevant"),
    (job(1302, "Senior Staff Machine Learning Engineer", "Remote in the US"), "not_relevant"),  # exclusion beats role
    (job(1303, "AI Engineer", "Toronto, Canada"), "not_relevant"),  # role matches, location doesn't
]


def test_ac13_rule_gives_the_hand_predicted_verdicts(workdir):
    for jobs, now in (([], FIXED_NOW), ([j for j, _ in PREDICTED], FIXED_NOW + timedelta(minutes=1))):
        opener = FakeOpener({BOARD_URL: (200, board_body(jobs), {"Content-Type": "application/json"})})
        assert run_cli(run_args(), opener=opener, now=now) == 0

    verdicts = {r["posting_id"]: r["record"]["verdict"] for r in latest_report(workdir)["records"]}
    assert verdicts == {str(j["id"]): v for j, v in PREDICTED}
