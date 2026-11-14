from rounding import round_half


def test_not_halves():
    assert round_half(2.4) == 2
    assert round_half(2.6) == 3


def test_halves_round_up():
    assert round_half(2.5) == 3


def test_same_as_builtin_round():
    assert round_half(2.5) == 2
