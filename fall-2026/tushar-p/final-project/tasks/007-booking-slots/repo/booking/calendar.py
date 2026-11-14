"""Free time between bookings."""

from booking.clock import to_hhmm, to_minutes
from booking.interval import overlaps


def merge(bookings):
    """Return bookings, a list of (start, end) minute intervals, sorted by
    start, with every group of overlapping intervals merged into one."""
    merged = []
    for start, end in sorted(bookings, key=lambda b: b[1]):
        if merged and overlaps(merged[-1], (start, end)):
            merged[-1] = (merged[-1][0], max(merged[-1][1], end))
        else:
            merged.append((start, end))
    return merged


def free_slots(bookings, day_start="09:00", day_end="17:00"):
    """Return the free time between day_start and day_end as ("HH:MM", "HH:MM")
    pairs, in order. bookings are ("HH:MM", "HH:MM") pairs, end not included."""
    times = [(to_minutes(start), to_minutes(end)) for start, end in bookings]
    free = []
    cursor = to_minutes(day_start)
    for start, end in merge(times):
        if start > cursor:
            free.append((to_hhmm(cursor), to_hhmm(start)))
        cursor = max(cursor, end)
    if cursor < to_minutes(day_end):
        free.append((to_hhmm(cursor), day_end))
    return free
