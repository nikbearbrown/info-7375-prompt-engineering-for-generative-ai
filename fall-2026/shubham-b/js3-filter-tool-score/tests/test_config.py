"""Config loading, overrides and path checks."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

from job_search_agent.config import ConfigOverrides, load_config
from job_search_agent.errors import ConfigError
from tests.conftest import PINNED_RESUME_SHA256, REPO_ROOT, RESUME_FIXTURE_REL

REPO_CONFIG = REPO_ROOT / "config" / "agent.toml"

MINIMAL = """\
[data]
dir = "data"
state_file = "{state_file}"

[board]
provider = "greenhouse"
token = "stripe"

[http]
allowed_hosts = ["boards-api.greenhouse.io"]
timeout_s = 30.0
max_bytes = 1000
max_redirects = 3
user_agent = "test"

[resume]
path = "persona/x.json"
{pin}

[model]
backend = "none"
executable = "claude"
model_id = "claude-sonnet-5-5"
timeout_s = 180.0
prompt_version = "v1"
"""


def _write(
    tmp_path: Path, *, state_file: str = "live/state.json", pin: str = ""
) -> Path:
    config_dir = tmp_path / "config"
    config_dir.mkdir()
    path = config_dir / "agent.toml"
    path.write_text(MINIMAL.format(state_file=state_file, pin=pin), encoding="utf-8")
    return path


def test_repo_config_loads_with_plan_values() -> None:
    config = load_config(REPO_CONFIG)
    assert config.project_root == REPO_ROOT
    assert config.data_dir == REPO_ROOT / "data"
    assert config.state_path == REPO_ROOT / "data" / "live" / "state.json"
    assert config.state_rel(seeded=False) == "live/state.json"
    assert config.state_rel(seeded=True) == "seeded/state.json"
    assert config.repo_rel("live/state.json") == "data/live/state.json"
    assert (config.board.provider, config.board.token) == ("greenhouse", "stripe")
    assert config.http.allowed_hosts == ["boards-api.greenhouse.io"]
    assert config.resume.path == RESUME_FIXTURE_REL
    assert config.resume.pinned_sha256 == PINNED_RESUME_SHA256
    assert config.model.backend == "claude-cli"
    assert config.model.model_id == "claude-sonnet-5-5"
    assert config.model.timeout_s == 180
    assert config.model.prompt_version == "v1"


def test_pinned_digest_matches_committed_fixture_bytes() -> None:
    # The pin is a literal in config and in this test; this only checks it was typed
    # correctly. The gate itself never computes its expected value at runtime.
    digest = hashlib.sha256((REPO_ROOT / RESUME_FIXTURE_REL).read_bytes()).hexdigest()
    assert digest == PINNED_RESUME_SHA256


@pytest.mark.parametrize(
    "state_file",
    [
        "../state.json",
        "../../elsewhere/state.json",
        "/elsewhere/state.json",
        ".",
        "live/../..",
    ],
)
def test_state_path_outside_data_dir_refused(tmp_path: Path, state_file: str) -> None:
    with pytest.raises(ConfigError, match="state_file"):
        load_config(_write(tmp_path, state_file=state_file))


def test_data_dir_outside_project_refused(tmp_path: Path) -> None:
    path = _write(tmp_path)
    with pytest.raises(ConfigError, match="data.dir"):
        load_config(path, overrides=ConfigOverrides(data_dir="../outside"))


def test_overrides_applied(tmp_path: Path) -> None:
    config = load_config(
        _write(tmp_path),
        overrides=ConfigOverrides(data_dir="data/scratch", model_backend="claude-cli"),
    )
    assert config.data_dir == tmp_path.resolve() / "data" / "scratch"
    assert config.state_rel(seeded=False) == "live/state.json"
    assert config.repo_rel("live/x.json") == "data/scratch/live/x.json"
    assert config.model.backend == "claude-cli"


def test_missing_pin_is_none_not_config_error(tmp_path: Path) -> None:
    assert load_config(_write(tmp_path)).resume.pinned_sha256 is None


def test_malformed_pin_refused(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="pinned_sha256"):
        load_config(_write(tmp_path, pin='pinned_sha256 = "ABC"'))


def test_unknown_key_refused(tmp_path: Path) -> None:
    path = _write(tmp_path)
    path.write_text(path.read_text() + "\n[extra]\nx = 1\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="extra"):
        load_config(path)


def test_missing_file_and_bad_toml(tmp_path: Path) -> None:
    with pytest.raises(ConfigError, match="not found"):
        load_config(tmp_path / "nope.toml")
    bad = tmp_path / "bad.toml"
    bad.write_text("[data\n", encoding="utf-8")
    with pytest.raises(ConfigError, match="TOML"):
        load_config(bad)
