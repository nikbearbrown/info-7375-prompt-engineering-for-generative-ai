"""Persona, board and state validation (CONTRACT.md, In and Refuses)."""
import copy
import json
import tempfile
import unittest
from pathlib import Path

from jobwatch import board
from jobwatch.persona import PersonaError, validate_resume
from jobwatch.state import StateError, load_state, save_state
from tests.helpers import RESUME, board_bytes, make_posting


class Persona(unittest.TestCase):
    def broken(self, **changes):
        data = copy.deepcopy(RESUME)
        for key, value in changes.items():
            if value is KeyError:
                del data[key]
            else:
                data[key] = value
        return data

    def test_committed_persona_is_valid(self):
        self.assertEqual(validate_resume(copy.deepcopy(RESUME))["name"], "Supriya Sharma")

    def test_real_looking_contact_details_are_rejected(self):
        with self.assertRaisesRegex(PersonaError, "example.com"):
            validate_resume(self.broken(email="supriya@gmail.com"))
        with self.assertRaisesRegex(PersonaError, "555"):
            validate_resume(self.broken(phone="617-253-1000"))

    def test_missing_unknown_and_empty_fields_are_rejected(self):
        for bad in (self.broken(skills=KeyError), self.broken(ssn="000-00-0000"),
                    self.broken(skills=[]), self.broken(name="  "), self.broken(skills=["Python", ""]),
                    self.broken(target_titles="Software Engineer")):
            with self.assertRaises(PersonaError):
                validate_resume(bad)


class Board(unittest.TestCase):
    def test_only_the_exact_endpoint_is_allowed(self):
        board.check_url(board.ALLOWED_URL)
        for url in ("http://boards-api.greenhouse.io/v1/boards/klaviyo/jobs?content=true",
                    "https://evil.example.com/v1/boards/klaviyo/jobs?content=true",
                    "https://boards-api.greenhouse.io:8443/v1/boards/klaviyo/jobs?content=true",
                    "https://boards-api.greenhouse.io/v1/boards/datadog/jobs?content=true",
                    "https://boards-api.greenhouse.io/v1/boards/klaviyo/jobs/123/applications"):
            with self.assertRaises(board.BoardError, msg=url):
                board.check_url(url)
        with self.assertRaises(board.BoardError):
            board.fetch("https://evil.example.com/")          # refused before any network use

    def test_redirects_are_refused(self):
        class Req:
            full_url = board.ALLOWED_URL
        with self.assertRaisesRegex(board.BoardError, "redirect"):
            board.RefuseRedirects().redirect_request(Req(), None, 302, "Found", {}, "https://evil.example.com/")

    def test_malformed_responses_are_rejected_not_repaired(self):
        ok = make_posting(1, "Software Engineer")
        for raw in (b"not json", b'{"no_jobs": []}', board_bytes([ok, dict(ok)]),
                    board_bytes([{**ok, "id": None}]), board_bytes([{**ok, "id": "1"}]),
                    board_bytes([{k: v for k, v in ok.items() if k != "content"}])):
            with self.assertRaises(board.BoardError, msg=raw[:60]):
                board.parse_board(raw)
        self.assertEqual(len(board.parse_board(board_bytes([ok]))), 1)


class State(unittest.TestCase):
    def setUp(self):
        self.dir = Path(tempfile.mkdtemp())
        self.path = self.dir / "seen_ids.json"

    def test_missing_file_means_baseline(self):
        self.assertIsNone(load_state(self.path, "klaviyo"))

    def test_round_trip_is_sorted_and_unique(self):
        save_state(self.path, "klaviyo", {"30", "10", "20"}, "2026-10-30T00:00:00Z")
        self.assertEqual(load_state(self.path, "klaviyo")["seen_ids"], ["10", "20", "30"])
        self.assertEqual([p.name for p in self.dir.iterdir()], ["seen_ids.json"])   # no temp files left

    def test_bad_state_stops_instead_of_resetting(self):
        good = {"board": "klaviyo", "schema_version": 1, "seen_ids": ["1"], "last_successful_run": "x"}
        for bad in ("{oops", json.dumps({**good, "board": "datadog"}), json.dumps({**good, "seen_ids": ["2", "1"]}),
                    json.dumps({**good, "schema_version": 2}), json.dumps({"seen_ids": ["1"]})):
            self.path.write_text(bad)
            with self.assertRaises(StateError, msg=bad):
                load_state(self.path, "klaviyo")


if __name__ == "__main__":
    unittest.main()
