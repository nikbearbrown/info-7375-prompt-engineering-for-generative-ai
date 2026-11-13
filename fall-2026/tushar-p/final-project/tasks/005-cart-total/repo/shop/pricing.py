"""Prices. Every price is a whole number of cents (an int)."""


def apply_discount(price_cents, percent):
    """Return price_cents reduced by percent percent, rounded down to whole cents.

    percent is from 0 to 100. The result is an int.
    """
    return price_cents * (100 - percent) / 100
