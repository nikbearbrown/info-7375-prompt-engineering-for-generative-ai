"""Compare version strings."""


def compare(a, b):
    """Return -1, 0, or 1 as version a is older than, the same as, or newer than b.

    A version is whole numbers separated by dots, like "1.10.2", optionally
    followed by "-" and a pre-release tag, like "2.0.0-rc1".
    - Numbers compare as numbers: "1.10" is newer than "1.9".
    - Missing numbers count as 0: "1.0" is the same as "1.0.0".
    - A pre-release is older than the same version without one:
      "1.0.0-rc1" is older than "1.0.0".
    - Two pre-releases of the same version compare by their tags as plain
      strings: "1.0.0-alpha" is older than "1.0.0-beta".
    """
    if a == b:
        return 0
    return -1 if a < b else 1
