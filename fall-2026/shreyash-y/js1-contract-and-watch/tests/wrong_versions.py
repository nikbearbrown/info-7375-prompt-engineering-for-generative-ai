"""The two wrong versions named in CONTRACT.md section 6, written as small, plausible
implementations. They exist only so the tests can show that the checks catch them.
Nothing in jsagent/ imports this file."""


def wrong_v1_new_postings_dedup_by_title(previous_titles, jobs):
    """Wrong Version 1: keys postings by title, so the same title in two cities collapses
    into one, and a new city for an old title is never reported."""
    seen = set(previous_titles)
    out = {}
    for job in jobs:
        if job["title"] not in seen:
            out[job["title"]] = job
    return list(out.values())


def wrong_v2_generic_judge(posting, resume):
    """Wrong Version 2: the verdict comes with a justification that cites nothing."""
    return {
        "posting_id": posting["id"],
        "board_token": posting["board_token"],
        "title": posting["title"],
        "verdict": "Relevant",
        "failed_conditions": [],
        "justification": "This job is a good match.",
    }


def wrong_v3_labels_shifted(records):
    """Extra wrong version from section 6 ('verdicts stay attached to the correct posting
    IDs'): verdicts computed in one order and zipped back onto ids in another."""
    verdicts = [r["verdict"] for r in records]
    shifted = verdicts[1:] + verdicts[:1]
    return [dict(r, verdict=v) for r, v in zip(records, shifted)]
