"""One way to turn a board's several place fields into the single location text the rule reads (JS2 D7).

Shared by the adapters because each system scatters places differently (Greenhouse: location.name
plus offices[]; Ashby: location plus secondaryLocations[]), but check 2 needs one string, and
"; " joining, de-duplication and dropping blanks must be the same everywhere or the same posting
would read differently depending on its board.
"""


def join_places(names: list[str]) -> str:
    seen: list[str] = []
    for n in names:
        n = (n or "").strip()
        if n and n not in seen:
            seen.append(n)
    return "; ".join(seen)
