"""The host allow-list (CONTRACT.md, In and Refuses 1).

A URL passes only if it is https, names no user or password, uses port 443 (or none), and its
host is EXACTLY a host on the list. No substring, prefix or suffix match: wrong version 3 in the
contract is exactly that mistake, and tools/mutants.py plants it to prove the tests notice.
"""

from __future__ import annotations

from urllib.parse import urlsplit, urlunsplit

from .errors import Refused

ALLOWED_HOSTS = frozenset({"api.ashbyhq.com"})
BOARD_URL = "https://api.ashbyhq.com/posting-api/job-board/openai"

# Characters that let two URL parsers disagree about where the host ends.
_SUSPICIOUS = set("\\ \t\r\n") | {chr(c) for c in range(32)} | {chr(127)}


def check(url: str) -> str:
    """Return the URL rebuilt from its checked parts, or raise Refused naming the problem."""
    if not isinstance(url, str) or any(ch in _SUSPICIOUS for ch in url):
        raise Refused(f"refused: {url!r} contains characters a URL should not have")
    parts = urlsplit(url)
    if parts.scheme != "https":
        raise Refused(f"refused: {url!r} is not https")
    if parts.username is not None or parts.password is not None:
        raise Refused(f"refused: {url!r} names a user or password")
    host = parts.hostname  # lowercased by urlsplit
    if not host:
        raise Refused(f"refused: {url!r} has no host")
    if host not in ALLOWED_HOSTS:
        raise Refused(f"refused: host {host!r} is not on the allow-list ({', '.join(sorted(ALLOWED_HOSTS))})")
    try:
        port = parts.port
    except ValueError:
        raise Refused(f"refused: {url!r} has an unreadable port") from None
    if port not in (None, 443):
        raise Refused(f"refused: {url!r} uses port {port}, not 443")
    # Rebuilt from the checked host, so what is fetched is exactly what was checked.
    return urlunsplit(("https", host, parts.path or "/", parts.query, ""))
