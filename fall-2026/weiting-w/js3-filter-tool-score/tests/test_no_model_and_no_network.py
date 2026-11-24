"""FILTER.md §5 and reports/what-moves-the-score.md §5, as source checks.

"Nothing here trains anything, nothing calls a model, nothing reaches the
network" are claims about what is *absent*, and absence is the kind of claim
that quietly stops being true the next time somebody adds an import. So they
are checked by reading every module this project ships.

`tools/explain_shortlist.py` is the one that matters: it renders a prompt and
must never grow the ability to send it.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
SHIPPED = sorted(
    p for d in ("jobfilter", "toolserver", "tools", "inherited")
    for p in (ROOT / d).rglob("*.py")
)


def test_there_are_modules_to_read():
    assert len(SHIPPED) >= 20


@pytest.mark.parametrize("needle", ["os.environ", "os.getenv", "getenv("])
def test_no_module_reads_an_environment_variable(needle):
    bad = [p.name for p in SHIPPED if needle in p.read_text(encoding="utf-8")]
    assert bad == [], f"{needle} appears in {bad}"


@pytest.mark.parametrize("needle", ["anthropic", "openai", "api_key", "claude_judge"])
def test_no_module_calls_a_model(needle):
    bad = [
        p.name for p in SHIPPED
        if needle in p.read_text(encoding="utf-8").lower()
        and p.name != "test_no_model_and_no_network.py"
    ]
    assert bad == [], f"{needle} appears in {bad}"


@pytest.mark.parametrize(
    "module", ["socket", "urllib", "http", "requests", "httpx", "ssl", "ftplib"]
)
def test_no_module_imports_anything_that_reaches_the_network(module):
    pattern = re.compile(rf"^\s*(?:import|from)\s+{module}\b", re.MULTILINE)
    bad = [p.name for p in SHIPPED if pattern.search(p.read_text(encoding="utf-8"))]
    assert bad == [], f"{module} imported in {bad}"


def test_the_prompt_renderer_only_prints():
    """It must never grow the ability to send what it renders."""
    src = (ROOT / "tools" / "explain_shortlist.py").read_text(encoding="utf-8")
    for needle in ("post(", "urlopen", "client", "completion", "messages.create"):
        assert needle not in src, f"explain_shortlist.py mentions {needle}"
    assert "print(" in src


@pytest.mark.parametrize("module", ["torch", "sklearn", "tensorflow", "keras", "xgboost"])
def test_no_module_imports_a_machine_learning_library(module):
    """Checked as an IMPORT, not as a mention.

    `pytorch` and `tensorflow` are signal words in S4 -- they appear in
    jobfilter/score.py as strings in a word list, which is the opposite of a
    dependency. The first version of this test looked for the bare substring
    and failed on its own word list, which is a neat illustration of the false
    friend problem the filter is about.
    """
    pattern = re.compile(rf"^\s*(?:import|from)\s+{module}\b", re.MULTILINE)
    bad = [p.name for p in SHIPPED if pattern.search(p.read_text(encoding="utf-8"))]
    assert bad == [], f"{module} imported in {bad}"


def test_nothing_calls_a_fit_method():
    for p in SHIPPED:
        assert ".fit(" not in p.read_text(encoding="utf-8"), p.name


def test_the_only_fitted_number_is_the_threshold():
    """FILTER.md §5: everything else is inherited or hand-set."""
    from jobfilter import score as scorer

    assert isinstance(scorer.THRESHOLD, int)
    # the weights are literals in the table, not loaded from anywhere
    src = (ROOT / "jobfilter" / "score.py").read_text(encoding="utf-8")
    assert "json.load" not in src and "pickle" not in src
