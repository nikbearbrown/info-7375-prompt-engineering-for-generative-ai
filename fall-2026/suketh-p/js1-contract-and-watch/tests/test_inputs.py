"""Input validation from CONTRACT.md 'In': the persona résumé and the board response.
Constructed inputs only."""

import json
import unittest

from jobwatch import board, resume
from jobwatch.errors import InputError
from tests.helpers import board_bytes, job, persona


class ResumeValidationTest(unittest.TestCase):
    def test_accepts_the_fictional_persona(self):
        self.assertEqual(resume.validate_resume(persona())["name"], "Alex Morgan")

    def rejects(self, mutate):
        p = persona()
        mutate(p)
        with self.assertRaises(InputError):
            resume.validate_resume(p)

    def test_rejects_a_resume_not_marked_fictional(self):
        self.rejects(lambda p: p.update(fictional=False))

    def test_rejects_an_email_outside_example_com(self):
        self.rejects(lambda p: p.update(email="alex.morgan@gmail.com"))

    def test_rejects_a_phone_without_the_555_exchange(self):
        self.rejects(lambda p: p.update(phone="202-867-0147"))

    def test_rejects_a_missing_preference(self):
        self.rejects(lambda p: p["preferences"].pop("location_terms"))

    def test_rejects_a_non_string_skill(self):
        self.rejects(lambda p: p["skills"].append(7))

    def test_rejects_an_empty_skill_list(self):
        self.rejects(lambda p: p.update(skills=[]))

    def test_rejects_fields_the_contract_does_not_name(self):
        # A real résumé would carry fields like this; the persona never does.
        self.rejects(lambda p: p.update(work_history=["Constructed Co, 2020-2024"]))

    def test_rejects_a_term_that_normalizes_to_nothing(self):
        self.rejects(lambda p: p["preferences"]["focus_terms"].append("++"))

    def test_error_message_does_not_repeat_the_rejected_value(self):
        p = persona()
        p["email"] = "alex.morgan@gmail.com"
        with self.assertRaises(InputError) as caught:
            resume.validate_resume(p)
        self.assertNotIn("gmail", str(caught.exception))


class BoardValidationTest(unittest.TestCase):
    def test_returns_postings_with_the_contract_fields(self):
        postings = board.parse_board(board_bytes(job(101, "Data Engineer", "Boston, MA", "<p>x</p>")))
        self.assertEqual([(p.id, p.title, p.location_name) for p in postings], [(101, "Data Engineer", "Boston, MA")])
        self.assertEqual(postings[0].content, "&lt;p&gt;x&lt;/p&gt;")

    def test_accepts_an_empty_jobs_array(self):
        self.assertEqual(board.parse_board(b'{"jobs": [], "meta": {"total": 0}}'), [])

    def test_rejects_malformed_json(self):
        with self.assertRaises(InputError):
            board.parse_board(b'{"jobs": [')

    def test_rejects_a_response_without_a_jobs_array(self):
        for body in (b'{"meta": {}}', b'{"jobs": {}}', b"[]"):
            with self.subTest(body=body), self.assertRaises(InputError):
                board.parse_board(body)

    def test_rejects_ids_that_are_not_positive_integers(self):
        for bad in (0, -5, "101", True, 1.5, None):
            j = job(101, "Data Engineer", "Boston, MA", "<p>x</p>")
            j["id"] = bad
            with self.subTest(id=bad), self.assertRaises(InputError):
                board.parse_board(json.dumps({"jobs": [j]}).encode())

    def test_rejects_missing_or_empty_required_fields(self):
        def broken(field, value):
            j = job(101, "Data Engineer", "Boston, MA", "<p>x</p>")
            j[field] = value
            return j
        for j in (broken("title", ""), broken("title", None), broken("location", {}),
                  broken("location", None), broken("location", {"name": 5}),
                  broken("content", ""), broken("content", None)):
            with self.subTest(job=j), self.assertRaises(InputError):
                board.parse_board(json.dumps({"jobs": [j]}).encode())

    def test_accepts_an_empty_location_name(self):
        # The contract requires a string; an empty one later fails the location condition.
        postings = board.parse_board(board_bytes(job(101, "Data Engineer", "", "<p>x</p>")))
        self.assertEqual(postings[0].location_name, "")

    def test_identical_duplicate_ids_produce_one_posting(self):
        j = job(101, "Data Engineer", "Boston, MA", "<p>x</p>")
        self.assertEqual([p.id for p in board.parse_board(board_bytes(j, j))], [101])

    def test_conflicting_records_sharing_an_id_are_an_error(self):
        a = job(101, "Data Engineer", "Boston, MA", "<p>x</p>")
        b = job(101, "Data Engineer II", "Boston, MA", "<p>x</p>")
        with self.assertRaises(InputError):
            board.parse_board(board_bytes(a, b))


if __name__ == "__main__":
    unittest.main()
