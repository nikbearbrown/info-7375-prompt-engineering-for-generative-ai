from tagging import add_tag


def test_starts_empty():
    assert add_tag("x") == ["x"]


def test_starts_empty_every_time():
    assert add_tag("y") == ["y"]


def test_case_insensitive():
    assert add_tag("X", ["x"]) == ["x"]


def test_input_not_changed():
    tags = ["a"]
    assert add_tag("b", tags) == ["a", "b"]
    assert tags == ["a"]


def test_returns_a_new_list():
    tags = ["a"]
    result = add_tag("a", tags)
    assert result == ["a"] and result is not tags
