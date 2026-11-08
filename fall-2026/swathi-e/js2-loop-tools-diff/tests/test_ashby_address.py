"""Tests for the Plaid office-name defect, written before the fix.

A1-A5 are the tests Claude Code proposed on 2026-11-05 and Swathi approved,
with her decision: append only addressCountry, in parsers.py only. They check
GATE.md's "Revision (2026-11-05, before the Plaid fix)". A1, A3, A4 and A5 use
SIMULATED Ashby bodies built here; A2 reads the REAL committed Nov 5 live Plaid
response, read-only. Written by Claude Code. Every test runs inside no_network().
"""
from contextlib import contextmanager
import json
from pathlib import Path
import socket
import sys
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE))

import parsers  # noqa: E402
import persona  # noqa: E402
import rule  # noqa: E402

_, TARGETS = persona.load_persona()
REAL_NOV5_PLAID = HERE / "runs" / "2026-11-05T23-11-48-228373-0500" / "005-plaid-request.json"


@contextmanager
def no_network():
    def refuse(*args, **kwargs):
        raise AssertionError("a network connection was attempted")
    with patch.object(socket, "create_connection", refuse), patch.object(socket.socket, "connect", refuse):
        yield


def address(country, region=None):
    postal = {"addressCountry": country}
    if region:
        postal["addressRegion"] = region
    return {"postalAddress": postal}


def ashby_job(job_id, title, location, location_country=None, secondary=()):
    """SIMULATED Ashby posting. secondary: (name, country or None) pairs."""
    job = {"id": job_id, "title": title, "location": location, "isListed": True,
           "jobUrl": f"https://example.invalid/ashby/{job_id}",
           "secondaryLocations": [{"location": name, **({"address": address(c)} if c else {})}
                                  for name, c in secondary]}
    if location_country:
        job["address"] = address(location_country, "California")
    return job


def parse_one(job):
    with no_network():
        postings, _ = parsers.parse_ashby(json.dumps({"apiVersion": "1", "jobs": [job]}).encode())
    return postings[0]


class AshbyAddressCountry(unittest.TestCase):
    def test_A1_office_name_gets_its_us_country(self):
        """A1, GATE.md Revision (2026-11-05, before the Plaid fix). SIMULATED, modeled on real posting
        1bcfe93d: "San Francisco HQ" with addressCountry "United States" parses to
        "San Francisco HQ (United States)", and the JS1 rule's record says relevant."""
        posting = parse_one(ashby_job("sim-1", "Fraud Intelligence Analyst", "San Francisco HQ", "United States"))
        self.assertEqual(posting["location"], "San Francisco HQ (United States)")
        self.assertEqual(rule.judge(posting["title"], posting["location"], TARGETS)["verdict"], rule.RELEVANT)

    def test_A2_real_nov5_plaid_postings_are_relevant(self):
        """A2, GATE.md Revision (2026-11-05, before the Plaid fix), Evidence line. The REAL Nov 5
        live Plaid response, read-only: postings 1bcfe93d (Fraud Intelligence Analyst) and 4d2f0d16
        (Financial Analyst, Corporate FP&A) get the country and the rule's record says relevant."""
        with no_network():
            postings, _ = parsers.parse_ashby(REAL_NOV5_PLAID.read_bytes())
        by_id = {p["id"]: p for p in postings}
        for job_id in ("1bcfe93d-97bd-4618-b81e-dc308ef69d30", "4d2f0d16-863d-46c5-bc86-2780a34eff44"):
            with self.subTest(id=job_id):
                posting = by_id[job_id]
                self.assertEqual(posting["location"], "San Francisco HQ (United States)")
                self.assertEqual(rule.judge(posting["title"], posting["location"], TARGETS)["verdict"],
                                 rule.RELEVANT)

    def test_A3_secondary_location_gets_its_country(self):
        """A3, GATE.md Revision (2026-11-05, before the Plaid fix): each secondaryLocation is followed
        by its own addressCountry. SIMULATED: a primary with no address and a secondary "Seattle
        Office" in the United States."""
        posting = parse_one(ashby_job("sim-3", "Data Engineer", "Toronto Hub",
                                      secondary=(("Seattle Office", "United States"),)))
        self.assertEqual(posting["location"], "Toronto Hub; Seattle Office (United States)")

    def test_A4_control_no_address_leaves_location_unchanged(self):
        """A4, control for GATE.md Revision (2026-11-05, before the Plaid fix): "when the response gives
        one". SIMULATED: no address anywhere, so the location is exactly as before."""
        posting = parse_one(ashby_job("sim-4", "Data Engineer", "San Francisco HQ",
                                      secondary=(("Seattle Office", None),)))
        self.assertEqual(posting["location"], "San Francisco HQ; Seattle Office")

    def test_A5_control_non_us_country_still_fails_location_check(self):
        """A5, control for GATE.md Revision (2026-11-05, before the Plaid fix). SIMULATED: an office
        whose address is in Canada becomes "Toronto Office (Canada)" and the rule's location check
        (check 3) still fails."""
        posting = parse_one(ashby_job("sim-5", "Data Engineer", "Toronto Office", "Canada"))
        self.assertEqual(posting["location"], "Toronto Office (Canada)")
        self.assertFalse(rule.judge(posting["title"], posting["location"], TARGETS)["checks"]["location"])


if __name__ == "__main__":
    unittest.main()
