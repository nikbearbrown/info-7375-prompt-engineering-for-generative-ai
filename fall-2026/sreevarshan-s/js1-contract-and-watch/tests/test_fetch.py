import tempfile
import unittest
from pathlib import Path

from js1 import fetch


class _Response:
    def __init__(self, body):
        self.body = body

    def read(self):
        return self.body

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


class FetchTests(unittest.TestCase):
    def test_one_request_to_the_exact_url_with_the_user_agent(self):
        seen = []

        class Opener:
            def open(self, req, timeout=None):
                seen.append(req)
                return _Response(b'{"jobs": []}')

        body = fetch.fetch_board("databricks", opener=Opener())
        self.assertEqual(body, b'{"jobs": []}')
        self.assertEqual(len(seen), 1)
        self.assertEqual(seen[0].full_url, "https://boards-api.greenhouse.io/v1/boards/databricks/jobs?content=true")
        self.assertEqual(seen[0].get_header("User-agent"), "INFO7375-JS1-student-agent")

    def test_raw_response_saved_byte_for_byte(self):
        raw = '{"jobs":[{"id":1,"title":"CONSTRUCTED café — test"}]}\r\n  \n'.encode("utf-8")
        with tempfile.TemporaryDirectory() as tmp:
            path = fetch.save_raw(raw, Path(tmp) / "evidence" / "raw", "2026-10-29T12-00-00Z")
            self.assertEqual(path.name, "2026-10-29T12-00-00Z.json")
            self.assertEqual(path.read_bytes(), raw)


if __name__ == "__main__":
    unittest.main()
