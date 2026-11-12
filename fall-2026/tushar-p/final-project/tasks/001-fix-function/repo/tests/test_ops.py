import pytest

from calc import add, divide, multiply, subtract


def test_add():
    assert add(2, 3) == 5


def test_subtract():
    assert subtract(10, 4) == 6


def test_multiply():
    assert multiply(3, -4) == -12


def test_divide():
    assert divide(7, 2) == 3.5
    with pytest.raises(ZeroDivisionError):
        divide(1, 0)
