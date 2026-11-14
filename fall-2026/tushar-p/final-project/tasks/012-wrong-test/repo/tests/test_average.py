import pytest

from stats import average


def test_pair():
    assert average([1, 2]) == 1.5


def test_three():
    assert average([1, 2, 3]) == 2


def test_four():
    assert average([1, 2, 3, 4]) == 2


def test_empty():
    with pytest.raises(ValueError):
        average([])
