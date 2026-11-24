import json
import subprocess
import sys
from pathlib import Path

import pytest

from js3 import sample_for_audit as sfa

REPO = Path(__file__).resolve().parent.parent


def _fake_results():
    def row(i, title, passed, reason):
        return {
            "id": i,
            "title": title,
            "passed": passed,
            "reason": reason,
            "matched_words": {"role": [], "topic": [], "reject": []},
        }

    rejects = [row(i, f"Sales Role {i}", False, "no_match") for i in range(40)]
    near = [row(100 + i, f"Software Engineer {i}", False, "no_match") for i in range(15)]
    passed = [row(200, "Data Engineer", True, "title_match")]
    return {"databricks": rejects + near + passed, "stripe": [], "spotify": []}


@pytest.fixture
def paths(tmp_path):
    results = tmp_path / "filter_results.json"
    results.write_text(json.dumps(_fake_results()), encoding="utf-8")
    return results, tmp_path / "audit_sample.json", tmp_path / "audit_sheet.md"


def test_first_run_writes_both_files(paths):
    results, sample, sheet = paths
    sfa.main(results, sample, sheet)
    assert sample.exists() and sheet.exists()
    assert "| My verdict |" in sheet.read_text()


def test_rerun_with_unchanged_files_is_allowed(paths):
    results, sample, sheet = paths
    sfa.main(results, sample, sheet)
    before = (sample.read_bytes(), sheet.read_bytes())
    sfa.main(results, sample, sheet)
    assert (sample.read_bytes(), sheet.read_bytes()) == before


def test_rerun_refuses_to_overwrite_populated_sheet(paths):
    results, sample, sheet = paths
    sfa.main(results, sample, sheet)
    filled = sheet.read_text().replace("| no_match | | |", "| no_match | correct | sales role |", 1)
    sheet.write_text(filled)
    sample_before = sample.read_bytes()

    with pytest.raises(sfa.OverwriteRefused):
        sfa.main(results, sample, sheet)

    assert sheet.read_text() == filled          # verdicts preserved
    assert sample.read_bytes() == sample_before  # nothing else written either


def test_refusal_writes_nothing_when_only_sample_differs(paths):
    results, sample, sheet = paths
    sfa.main(results, sample, sheet)
    sample.write_text("{}\n")
    sheet.unlink()

    with pytest.raises(sfa.OverwriteRefused):
        sfa.main(results, sample, sheet)

    assert not sheet.exists()
    assert sample.read_text() == "{}\n"


def test_cli_exits_nonzero_and_keeps_the_real_populated_sheet(tmp_path):
    # Run the real script against copies of the real files, never the originals.
    out = tmp_path / "output"
    out.mkdir()
    for name in ("filter_results.json", "audit_sample.json", "audit_sheet.md"):
        (out / name).write_bytes((REPO / "output" / name).read_bytes())
    sheet_before = (out / "audit_sheet.md").read_bytes()

    code = (
        "import sys; from pathlib import Path; from js3 import sample_for_audit as s\n"
        "o = Path(sys.argv[1])\n"
        "try:\n"
        "    s.main(o / 'filter_results.json', o / 'audit_sample.json', o / 'audit_sheet.md')\n"
        "except s.OverwriteRefused as e:\n"
        "    print(e, file=sys.stderr); sys.exit(1)\n"
    )
    proc = subprocess.run(
        [sys.executable, "-B", "-c", code, str(out)],
        cwd=REPO, capture_output=True, text=True,
    )
    assert proc.returncode == 1
    assert "refusing to overwrite" in proc.stderr
    assert (out / "audit_sheet.md").read_bytes() == sheet_before


def test_draw_still_reproduces_the_committed_sample():
    results = json.loads((REPO / "output" / "filter_results.json").read_text())
    sample, _, _ = sfa.build(results)
    committed = json.loads((REPO / "output" / "audit_sample.json").read_text())
    assert sample == committed
