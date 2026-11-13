from textkit import slugify


def test_simple():
    assert slugify("Hello World") == "hello-world"


def test_punctuation():
    assert slugify("Hello, World!") == "hello-world"


def test_runs_of_spaces_and_edges():
    assert slugify("  Many   spaces  ") == "many-spaces"


def test_symbols():
    assert slugify("C++ & Go: a comparison") == "c-go-a-comparison"


def test_digits_kept():
    assert slugify("v2.0 release") == "v2-0-release"


def test_non_ascii_letter_is_a_separator():
    assert slugify("Cafe\u0301 au lait") == "cafe-au-lait"


def test_nothing_left():
    assert slugify("--- !!! ---") == ""
