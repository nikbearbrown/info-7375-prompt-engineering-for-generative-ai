"""Half-open intervals (start, end) of minutes: start is included, end is not."""


def overlaps(a, b):
    """Return whether intervals a and b share at least one minute.

    Intervals that only touch, like (540, 600) and (600, 660), do not overlap.
    """
    return a[0] <= b[1] and b[0] <= a[1]
