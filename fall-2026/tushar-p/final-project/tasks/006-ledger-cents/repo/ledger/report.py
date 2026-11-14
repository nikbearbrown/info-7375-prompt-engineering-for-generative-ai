"""Totals over ledger entries."""

from ledger.parse import parse


def total(text):
    """Return the sum of all amounts in text, in cents."""
    return sum(cents for _date, _category, cents in parse(text))


def by_category(text):
    """Return {category: total cents} for every category in text."""
    out = {}
    for _date, category, cents in parse(text):
        out[category] = out.get(category, 0) + cents
    return out


def format_cents(cents):
    """Return cents as dollars with two decimals: 1234 -> "12.34", -5 -> "-0.05"."""
    sign = "-" if cents < 0 else ""
    cents = abs(cents)
    return f"{sign}{cents // 100}.{cents % 100:02d}"
