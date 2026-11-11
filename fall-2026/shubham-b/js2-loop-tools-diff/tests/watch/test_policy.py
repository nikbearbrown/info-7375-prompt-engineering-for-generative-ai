"""Boundary tests B01-B20 of the permission policy (GATE §6, §7).

Each test's name carries its GATE §7 number; its expected result is the prediction
written in GATE.md before these tests were run. B07 (redirect) and B20 (repeat) need the
fetcher and live in ``test_loop.py``.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from job_search_agent.policy import Decision, PermissionPolicy, Verdict, settle
from job_search_agent.watch import reset_board

HOSTS = ("boards-api.greenhouse.io", "api.ashbyhq.com")
GH_URL = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs?content=true"


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    (root / "data" / "watch").mkdir(parents=True)
    (root / "config").mkdir()
    (root / "config" / "watch.toml").write_text("# plan\n")
    (root / "private").mkdir()
    (root / "private" / "real.resume.json").write_text("{}")
    return root


@pytest.fixture
def policy(project: Path) -> PermissionPolicy:
    return PermissionPolicy(
        project_root=project, write_root=project / "data" / "watch", allowed_hosts=HOSTS
    )


def _deny(reason: str) -> Verdict:
    return Verdict(Decision.DENY, reason)


# --- hosts and methods --------------------------------------------------------


def test_b01_greenhouse_get_allowed(policy: PermissionPolicy) -> None:
    assert policy.check_request("GET", GH_URL).allowed


def test_b02_ashby_get_allowed(policy: PermissionPolicy) -> None:
    url = "https://api.ashbyhq.com/posting-api/job-board/ramp"
    assert policy.check_request("GET", url).allowed


def test_b03_host_off_the_allow_list(policy: PermissionPolicy) -> None:
    verdict = policy.check_request("GET", "https://jobs.lever.co/palantir")
    assert verdict == _deny("host")


@pytest.mark.parametrize(
    "url",
    [
        "https://boards-api.greenhouse.io.evil.example/",
        "https://evilboards-api.greenhouse.io/",
        "https://evil.example/boards-api.greenhouse.io",
    ],
)
def test_b04_allowed_name_as_prefix_or_substring(
    policy: PermissionPolicy, url: str
) -> None:
    assert policy.check_request("GET", url) == _deny("host")


def test_b05_plain_http(policy: PermissionPolicy) -> None:
    url = "http://boards-api.greenhouse.io/v1/boards/stripe/jobs"
    assert policy.check_request("GET", url) == _deny("scheme")


def test_b05_userinfo_and_port(policy: PermissionPolicy) -> None:
    assert policy.check_request("GET", "https://u:p@api.ashbyhq.com/x") == _deny(
        "userinfo"
    )
    assert policy.check_request("GET", "https://api.ashbyhq.com:8443/x") == _deny(
        "port"
    )


@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "PATCH"])
def test_b06_apply_endpoint_on_allowed_host(
    policy: PermissionPolicy, method: str
) -> None:
    url = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs/1"
    assert policy.check_request(method, url) == _deny("method")


# --- writes -------------------------------------------------------------------


def test_b08_write_inside_watch(policy: PermissionPolicy) -> None:
    assert policy.check_write("data/watch/loops/x/trace.jsonl").allowed


def test_b09_dotdot_escape(policy: PermissionPolicy) -> None:
    verdict = policy.check_write("data/watch/../live/state.json")
    assert verdict == _deny("outside_write_root")


def test_b10_prefix_trick_sibling(policy: PermissionPolicy, project: Path) -> None:
    (project / "data" / "watch-evil").mkdir()
    assert policy.check_write("data/watch-evil/x.json") == _deny("outside_write_root")


def test_b11_symlink_pointing_out(
    policy: PermissionPolicy, project: Path, tmp_path: Path
) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (project / "data" / "watch" / "link").symlink_to(outside, target_is_directory=True)
    assert policy.check_write("data/watch/link/x.json") == _deny("outside_write_root")


def test_b11_symlink_inside_watch_is_still_allowed(
    policy: PermissionPolicy, project: Path
) -> None:
    target = project / "data" / "watch" / "real"
    target.mkdir()
    (project / "data" / "watch" / "alias").symlink_to(target, target_is_directory=True)
    assert policy.check_write("data/watch/alias/x.json").allowed


def test_b11_absolute_path_outside(policy: PermissionPolicy) -> None:
    assert policy.check_write("/etc/x.json") == _deny("outside_write_root")


# --- read versus write --------------------------------------------------------


def test_b12_read_the_plan(policy: PermissionPolicy) -> None:
    assert policy.check_read("config/watch.toml").allowed


def test_b13_write_the_plan(policy: PermissionPolicy) -> None:
    assert policy.check_write("config/watch.toml") == _deny("outside_write_root")


def test_b13_write_gate_and_js1_state(policy: PermissionPolicy) -> None:
    for rel in ("GATE.md", "data/live/state.json", "src/job_search_agent/watch.py"):
        assert policy.check_write(rel) == _deny("outside_write_root")


def test_b14_read_private_resume(policy: PermissionPolicy, project: Path) -> None:
    assert policy.check_read("private/real.resume.json") == _deny("private")
    (project / ".env").write_text("X=1")
    assert policy.check_read(".env") == _deny("private")


def test_b14_read_private_through_a_symlink(
    policy: PermissionPolicy, project: Path
) -> None:
    (project / "data" / "watch" / "cv.json").symlink_to(
        project / "private" / "real.resume.json"
    )
    assert policy.check_read("data/watch/cv.json") == _deny("private")


def test_b15_read_outside_the_project(policy: PermissionPolicy) -> None:
    assert policy.check_read("/etc/hosts") == _deny("outside_project")
    assert policy.check_read("../outside.txt") == _deny("outside_project")


# --- the write that needs approval --------------------------------------------


def _state(project: Path) -> Path:
    path = project / "data/watch/boards/greenhouse-ramp/live/state.json"
    path.parent.mkdir(parents=True)
    path.write_text("{}")
    return path


def test_b16_delete_needs_approval(policy: PermissionPolicy, project: Path) -> None:
    verdict = policy.check_delete(_state(project))
    assert verdict == Verdict(Decision.NEEDS_APPROVAL, "delete")


def test_b16_delete_outside_is_denied_not_asked(policy: PermissionPolicy) -> None:
    assert policy.check_delete("data/live/state.json") == _deny("outside_write_root")


def test_b17_no_terminal_means_no(policy: PermissionPolicy, project: Path) -> None:
    state = _state(project)
    verdict, deleted = reset_board(policy, "greenhouse", "ramp", approver=None)
    assert verdict == _deny("not_approved")
    assert not deleted
    assert state.exists()


def test_b17_refused_approval(policy: PermissionPolicy, project: Path) -> None:
    state = _state(project)
    questions: list[str] = []

    def refuse(question: str) -> bool:
        questions.append(question)
        return False

    verdict, deleted = reset_board(policy, "greenhouse", "ramp", approver=refuse)
    assert (verdict, deleted) == (_deny("not_approved"), False)
    assert state.exists()
    assert "greenhouse/ramp" in questions[0]


def test_b18_approved_delete(policy: PermissionPolicy, project: Path) -> None:
    state = _state(project)
    verdict, deleted = reset_board(
        policy, "greenhouse", "ramp", approver=lambda _: True
    )
    assert verdict == Verdict(Decision.ALLOW, "approved")
    assert deleted
    assert not state.exists()


def test_settle_leaves_other_verdicts_alone() -> None:
    for verdict in (Verdict(Decision.ALLOW), _deny("host")):
        assert settle(verdict, approver=lambda _: True, question="?") == verdict


# --- never-actions ------------------------------------------------------------


@pytest.mark.parametrize("action", ["apply", "email", "message", "login"])
def test_b19_never_actions(policy: PermissionPolicy, action: str) -> None:
    verdict = policy.check_action(action)
    assert verdict == _deny("never")
    assert settle(verdict, approver=lambda _: True, question="?") == verdict


def test_b19_tools_and_unknown_actions(policy: PermissionPolicy) -> None:
    for tool in ("fetch", "read", "write", "delete"):
        assert policy.check_action(tool).allowed
    assert policy.check_action("submit_form") == _deny("unknown_action")


def test_write_root_must_be_inside_the_project(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="inside the project"):
        PermissionPolicy(
            project_root=tmp_path / "p", write_root=tmp_path, allowed_hosts=HOSTS
        )
