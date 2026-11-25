"""New-posting detection against the seen-postings file."""


def find_new(postings, seen_ids):
    """Return (new_postings, updated_seen_ids). seen_ids=None means baseline run."""
    current = [p["id"] for p in postings]
    if seen_ids is None:
        return [], sorted(set(current))
    seen = set(seen_ids)
    new = [p for p in postings if p["id"] not in seen]
    return new, sorted(seen | set(current))
