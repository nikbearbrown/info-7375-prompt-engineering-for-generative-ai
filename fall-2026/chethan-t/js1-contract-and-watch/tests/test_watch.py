from agent import watch


def test_14_baseline_run_reports_nothing_new_and_saves_all_ids(postings):
    # Wrong version 4: baseline run reports everything as new.
    batch = [postings[k] for k in ("swe_boston_plain", "swe_london", "swe_brussels")]
    new, seen = watch.find_new(batch, None)
    assert new == []
    assert set(seen) == {4000001, 4000007, 4000012}


def test_15_only_unseen_posting_is_new(postings):
    batch = [postings[k] for k in (
        "swe_boston_plain", "swe_london", "swe_brussels", "swe_boston_and_london",
    )]
    new, seen = watch.find_new(batch, {4000001, 4000007, 4000012})
    assert [p["id"] for p in new] == [4000008]
    assert set(seen) == {4000001, 4000007, 4000012, 4000008}
