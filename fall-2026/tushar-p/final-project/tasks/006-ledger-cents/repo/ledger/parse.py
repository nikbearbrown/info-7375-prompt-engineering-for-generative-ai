"""Read ledger lines like "2026-11-01,coffee,3.45" into entries."""


def parse_amount(text):
    """Return the amount in text, a decimal number of dollars with at most
    two decimals such as "3.45" or "-0.29", as an int number of cents."""
    return int(float(text) * 100)


def parse_line(line):
    """Return (date, category, cents) for one "date,category,amount" line."""
    date, category, amount = line.strip().split(",")
    return date, category, parse_amount(amount)


def parse(text):
    """Return the entries in text, one per non-blank line."""
    return [parse_line(line) for line in text.splitlines() if line.strip()]
