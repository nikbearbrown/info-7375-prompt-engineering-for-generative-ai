import pytest

from versions import compare


@pytest.mark.parametrize("a, b, want", [
    ("1.10", "1.9", 1),
    ("1.9", "1.10", -1),
    ("2.0", "2.0", 0),
    ("1.0", "1.0.0", 0),
    ("1.0.0", "1", 0),
    ("1.0.0-rc1", "1.0.0", -1),
    ("1.0.0", "1.0.0-rc1", 1),
    ("1.0.0-alpha", "1.0.0-beta", -1),
    ("1.0-rc1", "1.0.0-rc1", 0),
    ("0.9.9", "1.0.0-rc1", -1),
    ("10.0", "9.99.99", 1),
])
def test_compare(a, b, want):
    assert compare(a, b) == want
