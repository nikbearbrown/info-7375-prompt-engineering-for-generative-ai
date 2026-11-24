"""SCORE-REPORT.md: section 2 is reproduced verbatim by checks/score_report.py, and the values
and code line references in section 1 match the code."""

import contextlib
import importlib.util
import io

import pytest

from agent import PROJECT_DIR, sheets
from agent import filter as flt

REPORT = (PROJECT_DIR / "SCORE-REPORT.md").read_text(encoding="utf-8")
BEGIN, END = "<!-- BEGIN checks/score_report.py output -->\n", "<!-- END checks/score_report.py output -->"
FILTER_LINES = (PROJECT_DIR / "agent" / "filter.py").read_text(encoding="utf-8").splitlines()
SHEETS_LINES = (PROJECT_DIR / "agent" / "sheets.py").read_text(encoding="utf-8").splitlines()


# Lines the report cites as part of a range rather than on their own.
CITED_AS = {57: "agent/filter.py:55–57", 259: "agent/filter.py:257–259"}


BEGIN_2B = "<!-- BEGIN checks/score_report.py --section 2b output -->\n"
END_2B = "<!-- END checks/score_report.py --section 2b output -->"


def _run(*argv):
    spec = importlib.util.spec_from_file_location("score_report", PROJECT_DIR / "checks" / "score_report.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        assert module.main(list(argv)) == 0
    return buf.getvalue()


@pytest.fixture(scope="module")
def script_output():
    return _run("--section", "2")


@pytest.fixture(scope="module")
def section_2b_output():
    return _run("--section", "2b")


def test_section_2_is_the_script_output_verbatim(script_output):
    committed = REPORT[REPORT.index(BEGIN) + len(BEGIN):REPORT.index(END)]
    assert committed == script_output


def test_default_section_is_2(script_output):
    assert _run() == script_output


def test_section_2b_is_the_script_output_verbatim(section_2b_output):
    committed = REPORT[REPORT.index(BEGIN_2B) + len(BEGIN_2B):REPORT.index(END_2B)]
    assert committed == section_2b_output


def test_section_2b_headline_figures(section_2b_output):
    assert "8 changed + 8 controls = 16 rows; labels 7 keep, 7 reject, 2 cannot_tell." in section_2b_output
    assert "| v0.1 | 1/8 | 5/8 | 6/16 |" in section_2b_output
    assert "| v0.2 | 6/8 | 5/8 | 11/16 |" in section_2b_output
    for row in ("| C1 | 6 | 5 | 0 | 1 |", "| C2 | 0 | 0 | 0 | 0 |", "| C3 | 1 | 0 | 0 | 1 |",
                "| C4 | 1 | 0 | 1 | 0 |", "| C5 | 0 | 0 | 0 | 0 |", "| C6 | 1 | 1 | 0 | 0 |",
                "| v0.2 (combined) | 7 | 5 | 0 | 2 |"):
        assert row in section_2b_output


def test_section_2b_controls_never_move(section_2b_output):
    lines = [ln for ln in section_2b_output.splitlines() if ln.startswith("| v0.")]
    assert lines and all(ln.split(" | ")[2] == "5/8" for ln in lines[:8])


def test_section_2_headline_figures(script_output):
    assert "Held-out labels (blind, commit f97f528a): 4 keep, 24 reject, 2 cannot_tell; 30 rows." in script_output
    assert "| v0.1 | — | 24 | 80.0% | 62.7% – 90.5% | — | — |" in script_output
    assert "| v0.2 | C1–C6 combined | 24 | 80.0% | 62.7% – 90.5% | 0 | 0 / 0 |" in script_output


@pytest.mark.parametrize("line, prefix", [
    (46, "MIN_TEXT_CHARS = 200"), (47, "KEEP_THRESHOLD = 2"), (48, "TERM_CAP = 3"),
    (49, "NEAR_THRESHOLD = (1, 3)"), (51, "G1_ROLES = ("), (54, "G2_EXCLUDED = ("), (55, "TOPIC_WORDS = ("),
    (57, "TOPIC_WORDS_V02 = "), (62, "G5_PHRASES = ("), (67, "US_MARKERS = ("), (92, "US_CONTAINING_REGIONS = ("),
    (94, "_REMOTE_WORDS = "), (95, "_PLACEHOLDERS = "), (101, "_G4_PATTERN = re.compile("),
    (247, "_N_C6 = "), (257, "SPELLED = {"), (259, "_MAX_KIND = "), (271, "PREFERRED_WORDS = ("),
    (275, "HEADING_MAX_WORDS = 8"), (329, '    cutoff = 2 if "C3" in rules else 3'),
])
def test_section_1_filter_line_references(line, prefix):
    assert FILTER_LINES[line - 1].startswith(prefix)
    cited = CITED_AS.get(line, f"agent/filter.py:{line}")
    assert cited in REPORT


@pytest.mark.parametrize("line, prefix", [(31, "SEED = 7375"), (32, "NEAR_MAX = 15"),
                                          (33, "AUDIT_TARGETS = "), (34, "HELDOUT_SIZE = 30")])
def test_section_1_sheets_line_references(line, prefix):
    assert SHEETS_LINES[line - 1].startswith(prefix)


def test_section_1_values_match_the_code():
    assert ", ".join(flt.G1_ROLES) in REPORT
    assert ", ".join(flt.G2_EXCLUDED) in REPORT
    assert "v0.1: " + ", ".join(flt.TOPIC_WORDS) in REPORT
    assert flt.TOPIC_WORDS_V02 == tuple(w for w in flt.TOPIC_WORDS if w != "platform")
    for phrase in flt.G5_PHRASES:
        assert phrase in REPORT
    for word in flt.PREFERRED_WORDS + flt.US_CONTAINING_REGIONS + flt.US_CITIES + flt.US_CITY_SHORT_FORMS:
        assert word in REPORT
    assert len(flt.US_STATE_NAMES) == 50 and len(flt.US_STATE_ABBREVIATIONS) == 49 and "CA" not in flt.US_STATE_ABBREVIATIONS
    assert list(flt.SPELLED) == ["one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten"]
    assert (flt.MIN_TEXT_CHARS, flt.KEEP_THRESHOLD, flt.TERM_CAP, flt.NEAR_THRESHOLD, flt.HEADING_MAX_WORDS) == \
        (200, 2, 3, (1, 3), 8)
    assert (sheets.SEED, sheets.NEAR_MAX, sheets.AUDIT_TARGETS, sheets.HELDOUT_SIZE) == \
        (7375, 15, (("reject", 30), ("keep", 10), ("cannot_tell", 10)), 30)


def test_section_1_g4_cutoffs_behave_as_stated():
    filler = " Our team builds products." * 10
    assert flt.check_g4("Requires 3+ years." + filler)["result"] == "pass"   # v0.1 cutoff 3
    assert flt.check_g4("Requires 4+ years." + filler)["result"] == "fail"
    assert flt.check_g4_rules("Requires 3+ years." + filler, {"C3"})["result"] == "fail"   # v0.2 cutoff 2
    assert flt.check_g4_rules("Requires 2+ years." + filler, {"C3"})["result"] == "pass"
