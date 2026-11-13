import pytest

from timeparse import parse_duration


# Every case below is one of the docstring's own examples.
@pytest.mark.parametrize("text, seconds", [
    ("45s", 45),
    ("2h", 7200),
    ("90m", 5400),
    ("1h30m", 5400),
    ("1h0m5s", 3605),
    ("0s", 0),
])
def test_examples(text, seconds):
    assert parse_duration(text) == seconds


@pytest.mark.parametrize("text", [
    "",      # empty
    "10",    # no unit
    "h",     # no number
    "5x",    # unknown unit
    "1H",    # upper case
    "1.5h",  # not a whole number
    "1m1h",  # wrong order
    "1h1h",  # unit repeated
    "1 h",   # space
    "-5s",   # sign
])
def test_invalid(text):
    with pytest.raises(ValueError):
        parse_duration(text)
