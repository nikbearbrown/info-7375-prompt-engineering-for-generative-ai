import pytest

from listutil import chunks


def test_remainder_chunk():
    assert chunks([1, 2, 3, 4, 5], 2) == [[1, 2], [3, 4], [5]]


def test_exact_multiple():
    assert chunks([1, 2, 3, 4], 2) == [[1, 2], [3, 4]]


def test_size_larger_than_list():
    assert chunks([1, 2, 3], 5) == [[1, 2, 3]]


def test_size_one():
    assert chunks(["a", "b"], 1) == [["a"], ["b"]]


def test_empty_list():
    assert chunks([], 3) == []


def test_bad_size():
    with pytest.raises(ValueError):
        chunks([1, 2], 0)
