"""Boundary tests for the file policy (PLAN §3.3; JS2-ready)."""

from __future__ import annotations

import json
import os
from pathlib import Path

import pytest

from job_search_agent.config import load_config
from job_search_agent.errors import ConfigError, PathRejected, RunLocked
from job_search_agent.fsio import (
    OutputRoot,
    ReadPolicy,
    create_output_root,
    is_within,
    relative_within,
)
from job_search_agent.models import ExitCode
from tests.conftest import REPO_ROOT, RESUME_FIXTURE_REL


def _reason(excinfo: pytest.ExceptionInfo[PathRejected]) -> str:
    return excinfo.value.reason


def test_write_inside_root_ok(tmp_root: OutputRoot) -> None:
    path = tmp_root.write_bytes_atomic("live/runs/r1/raw.json", b"{}")
    assert path == tmp_root.root / "live" / "runs" / "r1" / "raw.json"
    assert path.read_bytes() == b"{}"
    assert tmp_root.read_bytes("live/runs/r1/raw.json") == b"{}"
    assert tmp_root.exists("live/runs/r1/raw.json")
    assert not tmp_root.exists("live/runs/r2/raw.json")


def test_create_output_root_creates_a_missing_data_dir(tmp_path: Path) -> None:
    with pytest.raises(PathRejected):
        OutputRoot(tmp_path / "fresh" / "data")
    root = create_output_root(tmp_path / "fresh" / "data")
    assert root.root == (tmp_path / "fresh" / "data").resolve()
    assert create_output_root(tmp_path / "fresh" / "data").root == root.root


@pytest.mark.parametrize("rel", ["../x", "a/../../x", "a/..", ".."])
def test_dotdot_rejected(tmp_root: OutputRoot, rel: str) -> None:
    with pytest.raises(PathRejected) as info:
        tmp_root.write_bytes_atomic(rel, b"x")
    assert _reason(info) == "dotdot"
    assert list(tmp_root.root.parent.glob("x")) == []


@pytest.mark.parametrize("rel", ["/etc/passwd", "~/x", "C:/x", "//host/x"])
def test_absolute_path_rejected(tmp_root: OutputRoot, rel: str) -> None:
    with pytest.raises(PathRejected) as info:
        tmp_root.resolve_for_write(rel)
    assert _reason(info) == "absolute"


@pytest.mark.parametrize(
    ("rel", "reason"),
    [("", "empty"), ("a//b", "not_canonical"), ("./a", "not_canonical"),
     ("a/", "not_canonical"), ("a\\b", "backslash")],
)  # fmt: skip
def test_malformed_rel_rejected(tmp_root: OutputRoot, rel: str, reason: str) -> None:
    with pytest.raises(PathRejected) as info:
        tmp_root.resolve_for_write(rel)
    assert _reason(info) == reason


def test_prefix_sibling_rejected(tmp_path: Path) -> None:
    data = tmp_path / "data"
    evil = tmp_path / "data-evil"
    data.mkdir()
    evil.mkdir()
    assert not is_within(evil / "x", data)
    assert str(evil / "x").startswith(str(data))  # the naive check would pass
    policy = ReadPolicy(tmp_path, roots=("data",))
    with pytest.raises(PathRejected):
        policy.check(evil / "x")
    with pytest.raises(PathRejected) as info:
        OutputRoot(data).write_bytes_atomic("../data-evil/x", b"x")
    assert _reason(info) == "dotdot"
    assert not (evil / "x").exists()


def test_symlink_component_rejected(tmp_root: OutputRoot) -> None:
    (tmp_root.root / "real").mkdir()
    (tmp_root.root / "link").symlink_to(tmp_root.root / "real")
    for call in (
        lambda: tmp_root.write_bytes_atomic("link/f.json", b"x"),
        lambda: tmp_root.resolve_for_write("link/f.json"),
        lambda: tmp_root.append_jsonl("link/e.jsonl", {}),
        lambda: tmp_root.make_empty_dir("link/tmp"),
        lambda: tmp_root.read_bytes("link/f.json"),
    ):
        with pytest.raises(PathRejected) as info:
            call()
        assert _reason(info) == "symlink"
    assert list((tmp_root.root / "real").iterdir()) == []


def test_symlink_leaf_rejected(tmp_root: OutputRoot, tmp_path: Path) -> None:
    victim = tmp_path / "victim.txt"
    victim.write_bytes(b"keep")
    (tmp_root.root / "state.json").symlink_to(victim)
    with pytest.raises(PathRejected) as info:
        tmp_root.write_json_atomic("state.json", {"a": 1})
    assert _reason(info) == "symlink"
    with pytest.raises(PathRejected):
        tmp_root.append_jsonl("state.json", {"a": 1})
    assert victim.read_bytes() == b"keep"


def test_symlink_escape_rejected(tmp_root: OutputRoot, tmp_path: Path) -> None:
    outside = tmp_path / "outside"
    outside.mkdir()
    (tmp_root.root / "live").symlink_to(outside)
    with pytest.raises(PathRejected):
        tmp_root.write_bytes_atomic("live/state.json", b"{}")
    with pytest.raises(PathRejected):
        tmp_root.make_empty_dir("live/tmp")
    assert list(outside.iterdir()) == []


def test_nul_byte_rejected(tmp_root: OutputRoot) -> None:
    with pytest.raises(PathRejected) as info:
        tmp_root.write_bytes_atomic("a\x00b", b"x")
    assert _reason(info) == "nul"
    assert "\x00" not in str(info.value)


def test_atomic_write_preserves_old_on_failure(
    tmp_root: OutputRoot, monkeypatch: pytest.MonkeyPatch
) -> None:
    tmp_root.write_bytes_atomic("live/state.json", b"old")

    def failing_replace(*_args: object, **_kwargs: object) -> None:
        raise OSError("disk full")

    monkeypatch.setattr("job_search_agent.fsio.os.replace", failing_replace)
    with pytest.raises(OSError, match="disk full"):
        tmp_root.write_bytes_atomic("live/state.json", b"new")
    assert (tmp_root.root / "live" / "state.json").read_bytes() == b"old"
    assert os.listdir(tmp_root.root / "live") == ["state.json"]


def test_atomic_write_leaves_no_temp(tmp_root: OutputRoot) -> None:
    for content in (b"one", b"two"):
        tmp_root.write_bytes_atomic("live/state.json", content)
    assert os.listdir(tmp_root.root / "live") == ["state.json"]
    assert (tmp_root.root / "live" / "state.json").read_bytes() == b"two"


def test_atomic_write_fsyncs_file_and_directory(
    tmp_root: OutputRoot, monkeypatch: pytest.MonkeyPatch
) -> None:
    synced: list[int] = []
    real_fsync = os.fsync

    def spy(fd: int) -> None:
        synced.append(fd)
        real_fsync(fd)

    monkeypatch.setattr("job_search_agent.fsio.os.fsync", spy)
    tmp_root.write_bytes_atomic("a.json", b"{}")
    assert len(synced) == 2  # the temp file, then its directory


def test_write_onto_directory_rejected(tmp_root: OutputRoot) -> None:
    (tmp_root.root / "d").mkdir()
    with pytest.raises(PathRejected) as info:
        tmp_root.write_bytes_atomic("d", b"x")
    assert _reason(info) == "is_dir"


def test_write_json_sort_keys_flag(tmp_root: OutputRoot) -> None:
    obj = {"posting_id": "1", "title": "t", "location": "x", "a": "ü"}
    sorted_path = tmp_root.write_json_atomic("sorted.json", obj)
    ordered_path = tmp_root.write_json_atomic("ordered.json", obj, sort_keys=False)
    sorted_text = sorted_path.read_text(encoding="utf-8")
    ordered_text = ordered_path.read_text(encoding="utf-8")
    assert list(json.loads(sorted_text)) == ["a", "location", "posting_id", "title"]
    assert list(json.loads(ordered_text)) == list(obj)
    assert ordered_text.endswith("}\n")
    assert '\n  "posting_id": "1"' in ordered_text
    assert "ü" in ordered_text
    with pytest.raises(ValueError, match="JSON compliant"):
        tmp_root.write_json_atomic("nan.json", {"x": float("nan")})
    assert not (tmp_root.root / "nan.json").exists()


def test_append_jsonl(tmp_root: OutputRoot) -> None:
    tmp_root.append_jsonl("runs/r/events.jsonl", {"b": 1, "a": "x\ny"})
    tmp_root.append_jsonl("runs/r/events.jsonl", {"b": 2, "a": "z"}, sort_keys=False)
    lines = (tmp_root.root / "runs/r/events.jsonl").read_text().splitlines()
    assert lines == ['{"a":"x\\ny","b":1}', '{"b":2,"a":"z"}']


def test_make_empty_dir(tmp_root: OutputRoot) -> None:
    path = tmp_root.make_empty_dir("tmp/judge-1")
    assert path.is_dir()
    assert tmp_root.make_empty_dir("tmp/judge-1") == path  # still empty: fine
    (path / "leftover").write_text("x")
    with pytest.raises(PathRejected) as info:
        tmp_root.make_empty_dir("tmp/judge-1")
    assert _reason(info) == "not_empty"
    (tmp_root.root / "file").write_text("x")
    with pytest.raises(PathRejected) as info:
        tmp_root.make_empty_dir("file")
    assert _reason(info) == "not_dir"


def test_root_must_exist(tmp_path: Path) -> None:
    with pytest.raises(PathRejected) as info:
        OutputRoot(tmp_path / "missing")
    assert _reason(info) == "root_missing"
    assert repr(OutputRoot(tmp_path)).startswith("OutputRoot(<")
    assert str(tmp_path) not in repr(OutputRoot(tmp_path))


def test_read_policy_allows_persona_and_evidence() -> None:
    policy = ReadPolicy(REPO_ROOT)
    fixture = policy.check(RESUME_FIXTURE_REL)
    assert fixture == (REPO_ROOT / RESUME_FIXTURE_REL).resolve()
    assert policy.repo_rel(REPO_ROOT / RESUME_FIXTURE_REL) == RESUME_FIXTURE_REL
    assert policy.check("evidence/handcheck").is_dir()
    assert policy.check("config/agent.toml").is_file()
    assert policy.read_bytes("config/agent.toml").startswith(b"#")


@pytest.mark.parametrize(
    "path",
    [
        str(Path.home() / ".claude" / "settings.json"),
        "../outside.json",
        "persona/../pyproject.toml",
        "src/job_search_agent/resume.py",
        "CONTRACT.md",
        "~/.ssh/id_rsa",
        "/etc/passwd",
    ],
)
def test_read_policy_rejects_home_and_parent(path: str) -> None:
    with pytest.raises(PathRejected) as info:
        ReadPolicy(REPO_ROOT).check(path)
    assert _reason(info) == "outside_read_roots"
    assert path not in str(info.value)


def test_read_policy_resolves_symlinks(tmp_path: Path) -> None:
    (tmp_path / "persona").mkdir()
    secret = tmp_path / "secret.json"
    secret.write_text("{}")
    (tmp_path / "persona" / "me.json").symlink_to(secret)
    with pytest.raises(PathRejected):
        ReadPolicy(tmp_path).check("persona/me.json")
    with pytest.raises(PathRejected) as info:
        ReadPolicy(tmp_path).check("persona/\x00x")
    assert _reason(info) == "nul"


def test_state_path_outside_data_dir_refused(tmp_path: Path) -> None:
    text = (REPO_ROOT / "config" / "agent.toml").read_text(encoding="utf-8")
    config = tmp_path / "agent.toml"
    for state_file in ("../state.json", "../../state.json", "/var/state.json"):
        config.write_text(
            text.replace('"live/state.json"', f'"{state_file}"', 1), encoding="utf-8"
        )
        with pytest.raises(ConfigError, match="state_file"):
            load_config(config, project_root=REPO_ROOT)
    data = tmp_path / "data"
    data.mkdir()
    with pytest.raises(PathRejected):
        OutputRoot(data).write_json_atomic("../state.json", {})
    assert not (tmp_path / "state.json").exists()


# --- review fix 3: the per-mode run lock ----------------------------------------


def test_lock_is_exclusive_per_file_and_released(tmp_root: OutputRoot) -> None:
    with tmp_root.lock("live/.lock"):
        with pytest.raises(RunLocked) as info, tmp_root.lock("live/.lock"):
            pass
        assert info.value.exit_code is ExitCode.LOCKED
        assert "/" not in str(info.value).replace("live/.lock", "")
        with tmp_root.lock("seeded/.lock"):
            pass  # the seeded lock is independent
    with tmp_root.lock("live/.lock"):
        pass  # released on exit
    assert (tmp_root.root / "live" / ".lock").is_file()


def test_lock_refuses_a_symlink(tmp_root: OutputRoot, tmp_path: Path) -> None:
    (tmp_root.root / "live").mkdir()
    target = tmp_path / "elsewhere"
    target.write_bytes(b"")
    (tmp_root.root / "live" / ".lock").symlink_to(target)
    with pytest.raises(PathRejected) as info, tmp_root.lock("live/.lock"):
        pass
    assert _reason(info) == "symlink"


# --- review fix 4: fsio owns containment ------------------------------------------


def test_relative_within_is_the_single_containment_check(tmp_path: Path) -> None:
    root = tmp_path / "proj"
    (root / "data").mkdir(parents=True)
    (tmp_path / "proj-evil").mkdir()
    assert relative_within("data/x.json", root) == "data/x.json"
    assert relative_within(root / "data", root) == "data"
    assert relative_within(root, root, allow_root=True) == "."
    for bad in (root, tmp_path / "proj-evil" / "x", "../x", "data/../../x"):
        with pytest.raises(PathRejected) as info:
            relative_within(bad, root)
        assert _reason(info) == "outside_root"
    (root / "data" / "link").symlink_to(tmp_path / "proj-evil")
    with pytest.raises(PathRejected):
        relative_within("data/link/x", root)
    assert relative_within("data/link/x", root, follow_symlinks=False) == "data/link/x"
    with pytest.raises(PathRejected) as info:
        relative_within("data/\x00", root)
    assert _reason(info) == "nul"


# --- review nit: data/ is private to the owner ------------------------------------


def test_files_and_dirs_under_data_are_owner_only(tmp_root: OutputRoot) -> None:
    old = os.umask(0o022)
    try:
        tmp_root.write_json_atomic("live/runs/r1/state.json", {"a": 1})
        tmp_root.append_jsonl("live/runs/r1/events.jsonl", {"e": 1})
        tmp_root.make_empty_dir("tmp/claude-x")
        with tmp_root.lock("live/.lock"):
            pass
    finally:
        os.umask(old)
    for rel in ("live/runs/r1/state.json", "live/runs/r1/events.jsonl", "live/.lock"):
        assert (tmp_root.root / rel).stat().st_mode & 0o777 == 0o600, rel
    for rel in ("live", "live/runs", "live/runs/r1", "tmp/claude-x"):
        assert (tmp_root.root / rel).stat().st_mode & 0o777 == 0o700, rel
