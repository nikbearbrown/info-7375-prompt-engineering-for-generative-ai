"""The Step 7 independent check (checks/total_check.py) is itself code, so it gets tests: a check
that never says MISMATCH, or that passes a board it can't check, would make the demo prove nothing.

It is loaded from its file path because checks/ is deliberately not part of the job_agent package.
"""

import importlib.util
import json
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
_spec = importlib.util.spec_from_file_location("total_check", REPO / "checks" / "total_check.py")
total_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(total_check)


def write(folder: Path, name: str, body: dict) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    (folder / name).write_text(json.dumps(body))
    return folder / name


def test_a_list_shorter_than_its_total_is_a_mismatch_and_exits_1(tmp_path, capsys):
    write(tmp_path, "stripe_content.json", {"jobs": [{"id": 1}, {"id": 2}], "meta": {"total": 3}})
    assert total_check.main([str(tmp_path)]) == 1
    assert "| 2 | 3 | MISMATCH |" in capsys.readouterr().out


def test_a_list_equal_to_its_total_passes(tmp_path):
    write(tmp_path, "stripe_content.json", {"jobs": [{"id": 1}], "meta": {"total": 1}})
    assert total_check.main([str(tmp_path)]) == 0


def test_a_response_without_a_total_is_not_checkable_rather_than_passed(tmp_path, capsys):
    write(tmp_path, "openai_content.json", {"jobs": [{"id": "a"}]})
    assert total_check.main([str(tmp_path)]) == 0
    assert "can't check" in capsys.readouterr().out


def test_header_and_error_files_in_a_run_folder_are_skipped(tmp_path):
    write(tmp_path, "stripe_content.json", {"jobs": [], "meta": {"total": 0}})
    (tmp_path / "stripe_content.headers.txt").write_text("HTTP 200")
    (tmp_path / "striqe_attempt1_error.txt").write_text('{"status":404}')
    assert total_check.response_files(tmp_path) == [tmp_path / "stripe_content.json"]


def test_the_check_does_not_use_the_agent():
    """Independence (brief: "not the agent's own report"): no import of job_agent at all."""
    assert "job_agent" not in (REPO / "checks" / "total_check.py").read_text().split('"""', 2)[2]
