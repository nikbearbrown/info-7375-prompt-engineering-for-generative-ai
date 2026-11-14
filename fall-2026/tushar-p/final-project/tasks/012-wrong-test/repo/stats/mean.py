"""Averages."""


def average(xs):
    """Return the arithmetic mean of xs as a float: average([1, 2]) == 1.5.

    xs is a non-empty list of numbers; an empty list raises ValueError.
    """
    if not xs:
        raise ValueError("average of an empty list")
    return sum(xs) / len(xs)
