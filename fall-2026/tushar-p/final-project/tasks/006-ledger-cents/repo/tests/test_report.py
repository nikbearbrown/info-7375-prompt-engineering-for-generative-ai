from ledger import by_category, format_cents, total

LEDGER = """\
2026-11-01,coffee,3.45
2026-11-02,coffee,0.29
2026-11-03,books,12.10
2026-11-04,refund,-1.15
"""


def test_total():
    assert total(LEDGER) == 345 + 29 + 1210 - 115


def test_by_category():
    assert by_category(LEDGER) == {"coffee": 374, "books": 1210, "refund": -115}


def test_formatted_total():
    assert format_cents(total(LEDGER)) == "14.69"


def test_format_negative():
    assert format_cents(-5) == "-0.05"


def test_blank_lines_ignored():
    assert total("\n2026-11-01,misc,0.10\n\n") == 10
