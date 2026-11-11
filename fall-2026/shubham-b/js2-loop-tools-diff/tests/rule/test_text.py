"""``text.clean_html``: the CONTRACT §5 cleanup order, step by step."""

from __future__ import annotations

import pytest

from job_search_agent.text import clean_html


def test_clean_decodes_entity_escaped_tags_before_stripping() -> None:
    assert clean_html("&lt;p&gt;Java&lt;/p&gt;") == "Java"
    assert clean_html("&lt;h2&gt;&lt;strong&gt;Who&lt;/strong&gt;&lt;/h2&gt;") == "Who"


def test_clean_decodes_entities_remaining_after_strip() -> None:
    assert clean_html("&lt;p&gt;R&amp;amp;D&lt;/p&gt;") == "R&D"
    assert clean_html("About Stripe&amp;nbsp;") == "About Stripe"


def test_clean_replaces_tags_with_space() -> None:
    assert clean_html("<li>Java</li><li>Python</li>") == "Java Python"
    assert clean_html("Java<br/>Python") == "Java Python"


def test_clean_normalizes_whitespace_and_nbsp() -> None:
    assert clean_html("  a\n\t b  c  ") == "a b c"
    assert clean_html("a&nbsp;b") == "a b"


def test_clean_keeps_csharp_intact() -> None:
    assert clean_html("&lt;li&gt;C#, .NET&lt;/li&gt;") == "C#, .NET"
    assert clean_html("C&#35; and Node.js") == "C# and Node.js"


def test_clean_keeps_comparison_signs_that_are_not_tags() -> None:
    assert clean_html("a &lt; b and c &gt; d") == "a < b and c > d"
    assert clean_html("1 < 2") == "1 < 2"


def test_clean_drops_html_comments() -> None:
    assert clean_html("a<!-- hidden Java -->b") == "a b"


@pytest.mark.parametrize("text", ["", "   ", "<p></p>"])
def test_clean_empty_inputs(text: str) -> None:
    assert clean_html(text) == ""
