"""Parse short duration strings."""


def parse_duration(text):
    """Return the number of seconds in a duration such as "1h30m".

    A duration is one or more parts. Each part is a whole number written
    with the digits 0-9, followed by a unit: "h" (hours), "m" (minutes), or
    "s" (seconds). Units appear in that order (h, then m, then s), each at
    most once. There are no spaces, signs, decimal points, or upper-case
    units.

    Examples:
        parse_duration("45s") == 45
        parse_duration("2h") == 7200
        parse_duration("90m") == 5400
        parse_duration("1h30m") == 5400
        parse_duration("1h0m5s") == 3605
        parse_duration("0s") == 0

    Anything else raises ValueError, for example: "" (empty), "10" (no
    unit), "h" (no number), "5x" (unknown unit), "1H" (upper case),
    "1.5h" (not a whole number), "1m1h" (wrong order), "1h1h" (unit
    repeated), "1 h" (space), and "-5s" (sign).
    """
    raise NotImplementedError
