"""booking: free time between bookings, used as task 007."""

from booking.calendar import free_slots, merge
from booking.clock import to_hhmm, to_minutes
from booking.interval import overlaps

__all__ = ["free_slots", "merge", "overlaps", "to_hhmm", "to_minutes"]
