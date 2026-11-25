"""Allow-list tests. No test here opens a network connection."""

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from agent import fetch


class ExplodingOpener:
    """Fails the test if any code path tries to open a URL."""

    def __init__(self):
        self.calls = 0

    def open(self, *args, **kwargs):
        self.calls += 1
        raise AssertionError("network call attempted")


class FakeResponse:
    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FakeOpener:
    def __init__(self, body):
        self.body = body
        self.urls = []

    def open(self, request, timeout=None):
        self.urls.append(request.full_url)
        return FakeResponse(self.body)


REFUSED_URLS = [
    "http://boards-api.greenhouse.io/v1/boards/scaleai/jobs?content=true",
    "https://example.com/v1/boards/scaleai/jobs",
    "https://boards.greenhouse.io/scaleai",
    "https://boards-api.greenhouse.io.evil.example/v1/boards/scaleai/jobs",
    "https://boards-api.greenhouse.io@evil.example/v1/boards/scaleai/jobs",
    "https://boards-api.greenhouse.io:8443/v1/boards/scaleai/jobs",
    "ftp://boards-api.greenhouse.io/jobs",
    "file:///etc/passwd",
]


class AllowListTests(unittest.TestCase):

    def test_refuses_other_hosts_and_http_without_network(self):
        opener = ExplodingOpener()
        with mock.patch("urllib.request.urlopen",
                        side_effect=AssertionError("network")), \
                mock.patch("urllib.request.build_opener",
                           side_effect=AssertionError("network")):
            for url in REFUSED_URLS:
                with self.subTest(url=url):
                    with self.assertRaises(fetch.FetchRefused) as ctx:
                        fetch.fetch_bytes(url, opener=opener)
                    self.assertIn("refused", str(ctx.exception))
        self.assertEqual(opener.calls, 0)

    def test_http_error_message_names_the_scheme(self):
        with self.assertRaisesRegex(fetch.FetchRefused, "not https"):
            fetch.check_url("http://boards-api.greenhouse.io/v1/boards/scaleai")

    def test_refuses_unknown_board_token(self):
        for board in ("databricks", "../scaleai", "scaleai?x=1", ""):
            with self.subTest(board=board):
                with self.assertRaises(fetch.FetchRefused):
                    fetch.board_url(board)

    def test_allowed_url_is_https_greenhouse(self):
        self.assertEqual(
            fetch.board_url("scaleai"),
            "https://boards-api.greenhouse.io/v1/boards/scaleai/jobs"
            "?content=true")

    def test_redirect_to_other_host_is_refused(self):
        handler = fetch._AllowListRedirectHandler()
        with self.assertRaises(fetch.FetchRefused):
            handler.redirect_request(None, None, 302, "Found", {},
                                     "https://evil.example/jobs")

    def test_saves_raw_unchanged_and_returns_sha256(self):
        body = b'{"jobs": [], "meta": {"total": 0}}  \n'  # odd bytes kept
        opener = FakeOpener(body)
        with tempfile.TemporaryDirectory() as tmp:
            path, sha = fetch.fetch_board("scaleai", tmp, "20261031T000000Z",
                                          opener=opener)
            self.assertEqual(Path(path).name,
                             "20261031T000000Z_scaleai.json")
            self.assertEqual(Path(path).read_bytes(), body)
            self.assertEqual(sha, fetch.sha256_hex(body))
            self.assertEqual(len(sha), 64)
            with self.assertRaises(FileExistsError):
                fetch.save_raw(body, tmp, "20261031T000000Z", "scaleai")
        self.assertEqual(opener.urls, [fetch.board_url("scaleai")])


if __name__ == "__main__":
    unittest.main()
