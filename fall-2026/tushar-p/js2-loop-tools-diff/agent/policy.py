"""Network read policy (GATE.md "Network reads", F2). Every outbound request goes through
check_request() before the transport is called.

Allowed: unauthenticated HTTPS GET to the configured board's exact host, on the default
HTTPS port, at its exact listing route, with no query string. Everything else is refused,
which also blocks applications, logins, and any ATS write request.
"""

from urllib.parse import urlsplit

from . import providers
from .errors import ConfigError, RequestDenied

ALLOWED_METHOD = "GET"


def check_request(method, url, board) -> str:
    """Return url unchanged if the request is allowed for this board; otherwise raise RequestDenied."""

    def deny(reason: str):
        label = board.key if isinstance(board, providers.Board) else repr(board)
        raise RequestDenied(f"refused {method!r} {url!r} for board {label}: {reason}")

    if not isinstance(board, providers.Board):
        deny("no configured board")
    try:
        provider = providers.check_board(board.provider, board.token)
    except ConfigError as err:
        deny(str(err))  # F7: a denial while checking a request is a board failure
    if method != ALLOWED_METHOD:
        deny(f"only {ALLOWED_METHOD} is allowed")
    if not isinstance(url, str):
        deny("URL is not a string")
    try:
        parts = urlsplit(url)
        port = parts.port
    except ValueError as err:
        deny(f"unparseable URL: {err}")
    if parts.scheme != "https":
        deny("only https is allowed")
    # "https://allowed.host@evil.com" has hostname evil.com; refuse any userinfo, even empty.
    if "@" in parts.netloc:
        deny("user info in the URL")
    if parts.hostname != provider.host:
        deny(f"host {parts.hostname!r} is not {provider.host!r}")
    if port not in (None, 443):
        deny(f"port {port} is not the default HTTPS port")
    expected_route = providers.listing_route(board)
    if parts.path != expected_route:
        deny(f"path {parts.path!r} is not the configured route {expected_route!r}")
    if "?" in url or parts.query:
        deny("query strings are not allowed")
    if "#" in url or parts.fragment:
        deny("fragments are not allowed")
    # Last line of defense: only the canonical spellings pass. This also refuses whitespace,
    # control characters, and case variants that urlsplit would quietly normalize.
    host_forms = (provider.host, f"{provider.host}:443")
    if url not in {f"https://{host}{expected_route}" for host in host_forms}:
        deny("URL is not the canonical listing URL")
    return url
