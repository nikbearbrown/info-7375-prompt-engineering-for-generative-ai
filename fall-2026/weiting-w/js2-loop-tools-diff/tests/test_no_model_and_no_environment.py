"""GATE.md §5.4, as a test rather than a promise.

§5.4 claims the package never applies, emails, messages, logs in, or submits a
form, and that it reads no environment variable at all. Those are claims about
*what is absent*, which is the kind of claim that quietly stops being true. So
they are checked by reading the package's own source.

The environment-variable clause is here because §5.4 originally said the
package reads `ANTHROPIC_API_KEY` for a Claude judge carried over from JS1. The
judge was never carried over. Correcting the gate in the direction of the
stronger claim is exactly when a test should be written, not when one can be
skipped.
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

PKG = Path(__file__).resolve().parents[1] / "agent"
SOURCES = sorted(PKG.rglob("*.py"))


def test_there_are_sources_to_read():
    assert len(SOURCES) >= 15


@pytest.mark.parametrize("needle", ["os.environ", "os.getenv", "getenv(", "environb"])
def test_the_package_reads_no_environment_variable(needle):
    offenders = [p.name for p in SOURCES if needle in p.read_text(encoding="utf-8")]
    assert offenders == [], f"{needle} appears in {offenders}"


@pytest.mark.parametrize(
    "module",
    ["smtplib", "email.mime", "selenium", "playwright", "webbrowser", "requests_oauthlib"],
)
def test_the_package_imports_nothing_that_could_send_or_log_in(module):
    pattern = re.compile(rf"^\s*(?:import|from)\s+{re.escape(module)}", re.MULTILINE)
    offenders = [p.name for p in SOURCES if pattern.search(p.read_text(encoding="utf-8"))]
    assert offenders == [], f"{module} imported in {offenders}"


def test_no_http_method_other_than_get_appears_as_a_request_method():
    """A write-shaped method must not be reachable, not merely refused."""
    for path in SOURCES:
        source = path.read_text(encoding="utf-8")
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            for line in source.splitlines():
                if method not in line:
                    continue
                # Allowed: naming the method in a refusal, a message, or a test
                # expectation. Not allowed: handing it to something that sends.
                assert not re.search(r"(?:method|Request)\s*=\s*[\"']" + method, line), (
                    f"{path.name}: {line.strip()}"
                )


def test_no_model_is_called_anywhere_in_the_package():
    """JS1 had a Claude judge. This package has none, and §5.4 now says so."""
    needles = ["anthropic", "openai", "claude_judge", "api_key"]
    offenders = {}
    for path in SOURCES:
        lowered = path.read_text(encoding="utf-8").lower()
        hits = [n for n in needles if n in lowered]
        if hits:
            offenders[path.name] = hits
    assert offenders == {}, (
        f"GATE.md §5.4 says no model is called; found {offenders}"
    )
