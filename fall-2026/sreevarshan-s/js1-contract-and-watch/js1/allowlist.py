"""Host allow-list. CONTRACT.md Final, Refuses: D2§5, D4§3."""

from urllib.parse import urlsplit

ALLOWED_HOSTS = frozenset({"boards-api.greenhouse.io"})


class HostNotAllowed(Exception):
    pass


def check_url(url):
    """Return url unchanged if it targets an allowed host over https; raise otherwise."""
    parts = urlsplit(url)
    host = (parts.hostname or "").lower()
    if (
        parts.scheme != "https"
        or host not in ALLOWED_HOSTS
        or parts.port not in (None, 443)
        or parts.username is not None
        or parts.password is not None
    ):
        raise HostNotAllowed(
            f"refusing {url!r}: host {host!r} is not on the allow-list {sorted(ALLOWED_HOSTS)}"
        )
    return url
