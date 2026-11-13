"""Split a list into fixed-size chunks."""


def chunks(items, size):
    """Return items split into lists of length size, in order.

    The last chunk holds whatever is left over and may be shorter than size.
    An empty list gives no chunks. size must be a positive integer;
    otherwise ValueError is raised.
    """
    if size < 1:
        raise ValueError("size must be positive")
    out = []
    for start in range(0, len(items) - size, size):
        out.append(items[start:start + size])
    return out
