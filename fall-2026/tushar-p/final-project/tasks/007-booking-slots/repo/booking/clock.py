"""Times of day as minutes since midnight."""


def to_minutes(hhmm):
    """Return the minutes since midnight for "HH:MM": to_minutes("09:30") == 570."""
    hours, minutes = hhmm.split(":")
    return int(hours) * 100 + int(minutes)


def to_hhmm(minutes):
    """Return minutes since midnight as "HH:MM": to_hhmm(570) == "09:30"."""
    return f"{minutes // 60:02d}:{minutes % 60:02d}"
