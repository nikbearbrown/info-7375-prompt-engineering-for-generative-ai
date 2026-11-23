"""Offline fixture mode (GATE F18).

`--fixture <path>` grants a read of that file's exact resolved path through the FileGate.
FixtureTransport stands in for the network: it answers the one configured board's listing
URL with the fixture bytes as HTTP 200 and opens no socket. Requests still pass through
policy.check_request() and the attempt counter, exactly as live requests do.
"""

from .errors import TransportError
from .transport import Response

# The deliberately wrong input for --seed-wrong-empty ("Finished with the wrong answer").
SEEDED_EMPTY_BODY = b'{"jobs": []}'


class FixtureTransport:
    def __init__(self, url: str, body: bytes):
        self.url = url
        self.body = body

    def __call__(self, method: str, url: str, timeout: float) -> Response:
        if url != self.url:
            raise TransportError(f"fixture transport has no response for {url}")
        return Response(url, 200, (), self.body)
