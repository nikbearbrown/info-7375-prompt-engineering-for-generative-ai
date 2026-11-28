"""Board payloads from the two applicant-tracking systems, as postings with a key.

GATE.md 'Repeat rule': Greenhouse postings are keyed by `id`, Ashby postings by
`jobUrl` (a string that is never opened). Identical duplicates collapse; conflicting
records with the same key are rejected."""

import json
import unittest

from jobwatch import ats, rule
from jobwatch.errors import InputError
from tests.fakes import ashby, ashby_job, ashby_url_key, gh_job, greenhouse
from tests.helpers import persona

UUID_A = "00000000-0000-4000-8000-00000000000a"
UUID_B = "00000000-0000-4000-8000-00000000000b"


class GreenhouseTest(unittest.TestCase):
    def test_keys_are_the_ids_as_decimal_strings_in_response_order(self):
        body = greenhouse(gh_job(303, "Data Engineer"), gh_job(7, "Recruiter"))
        postings = ats.parse("greenhouse", body)
        self.assertEqual([p.key for p in postings], ["303", "7"])
        self.assertEqual(postings[0].title, "Data Engineer")
        self.assertEqual(postings[0].location_name, "Dublin, IE")

    def test_a_posting_that_breaks_the_js1_contract_is_rejected(self):
        broken = gh_job(5)
        broken["title"] = "   "
        with self.assertRaises(InputError):
            ats.parse("greenhouse", greenhouse(broken))


class AshbyTest(unittest.TestCase):
    def test_the_key_is_the_job_url_and_the_fields_map_to_the_rule_inputs(self):
        job = ashby_job(UUID_A, "Data Engineer", "North America", "<p>Python and SQL.</p>")
        [posting] = ats.parse("ashby", ashby(job))
        self.assertEqual(posting.key, ashby_url_key(UUID_A))
        self.assertEqual(posting.id, ashby_url_key(UUID_A))
        self.assertEqual(posting.title, "Data Engineer")
        self.assertEqual(posting.location_name, "North America")
        self.assertEqual(posting.content, "<p>Python and SQL.</p>")

    def test_a_job_without_a_usable_job_url_is_rejected(self):
        for bad in (None, "", "   ", 42):
            job = ashby_job(UUID_A)
            job["jobUrl"] = bad
            with self.subTest(jobUrl=bad), self.assertRaises(InputError):
                ats.parse("ashby", ashby(job))

    def test_missing_or_mistyped_fields_are_rejected(self):
        for field, bad in (("title", ""), ("title", None), ("location", None),
                           ("location", {"name": "x"}), ("descriptionHtml", ""), ("descriptionHtml", None)):
            job = ashby_job(UUID_A)
            job[field] = bad
            with self.subTest(field=field, value=bad), self.assertRaises(InputError):
                ats.parse("ashby", ashby(job))

    def test_a_body_that_is_not_a_jobs_object_is_rejected(self):
        for body in (b"Not Found", b"[]", b'{"apiVersion": "1"}', b'{"jobs": {}}'):
            with self.subTest(body=body), self.assertRaises(InputError):
                ats.parse("ashby", body)

    def test_identical_duplicates_collapse_to_one_posting(self):
        job = ashby_job(UUID_A)
        self.assertEqual(len(ats.parse("ashby", ashby(job, dict(job)))), 1)

    def test_conflicting_records_with_one_job_url_are_rejected(self):
        first, second = ashby_job(UUID_A, "Data Engineer"), ashby_job(UUID_A, "Recruiter")
        with self.assertRaises(InputError):
            ats.parse("ashby", ashby(first, second))

    def test_the_js1_rule_reads_an_ashby_posting(self):
        job = ashby_job(UUID_B, "Machine Learning Engineer", "San Francisco, United States",
                        "<p>We use Python, SQL and PyTorch.</p>")
        [posting] = ats.parse("ashby", ashby(job))
        record = rule.rule_verdict(persona(), posting)
        self.assertEqual(record["verdict"], "relevant")
        self.assertEqual(record["posting_id"], ashby_url_key(UUID_B))


class UnknownSystemTest(unittest.TestCase):
    def test_an_unknown_system_is_a_programming_error(self):
        with self.assertRaises(ValueError):
            ats.parse("lever", json.dumps({"jobs": []}).encode())


if __name__ == "__main__":
    unittest.main()
