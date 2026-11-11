"""Added 2026-11-10 ~9:50 pm, AFTER the code, because Claude Code's final review found a gap: the deliberately wrong
Lever parser (wrong_versions/lever_reads_nothing) passed every unit test - only the independent check caught it.
These tests pin both parsers. logs/24 shows them failing against that wrong version."""
import json, os, importlib, unittest
loop = importlib.import_module(os.environ.get("WATCHER_LOOP", "watcher.loop"))

class Parsers(unittest.TestCase):
    def test_lever_list_is_read(self):
        body = json.dumps([{"id": "a", "text": "Data Analyst"}, {"id": "b", "text": "BI Analyst"}]).encode()
        self.assertEqual(loop.parse_jobs("lever", body), [("a", "Data Analyst"), ("b", "BI Analyst")])
    def test_greenhouse_jobs_are_read(self):
        body = json.dumps({"jobs": [{"id": 7, "title": "Analyst"}]}).encode()
        self.assertEqual(loop.parse_jobs("greenhouse", body), [("7", "Analyst")])
    def test_empty_lists_are_valid(self):
        self.assertEqual(loop.parse_jobs("lever", b"[]"), []); self.assertEqual(loop.parse_jobs("greenhouse", b'{"jobs": []}'), [])
    def test_wrong_shape_is_an_error_not_zero(self):
        with self.assertRaises(ValueError): loop.parse_jobs("lever", b'{"jobs": []}')
        with self.assertRaises(ValueError): loop.parse_jobs("greenhouse", b"[]")

if __name__ == "__main__": unittest.main()
