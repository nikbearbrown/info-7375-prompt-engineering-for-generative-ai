from booking import free_slots, merge, overlaps, to_hhmm, to_minutes


def test_to_minutes():
    assert to_minutes("09:30") == 570
    assert to_minutes("00:00") == 0


def test_to_hhmm():
    assert to_hhmm(570) == "09:30"


def test_touching_intervals_do_not_overlap():
    assert not overlaps((540, 600), (600, 660))
    assert overlaps((540, 601), (600, 660))


def test_merge_sorts_by_start():
    assert merge([(600, 630), (540, 720)]) == [(540, 720)]


def test_merge_keeps_separate_intervals():
    assert merge([(700, 760), (540, 600)]) == [(540, 600), (700, 760)]


def test_free_slots():
    bookings = [("10:00", "11:00"), ("09:30", "12:00"), ("13:00", "14:00")]
    assert free_slots(bookings) == [("09:00", "09:30"), ("12:00", "13:00"), ("14:00", "17:00")]


def test_free_slots_back_to_back():
    assert free_slots([("09:00", "10:00"), ("10:00", "11:00")]) == [("11:00", "17:00")]
