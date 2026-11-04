"""Build the SEEDED second-run input from the real first-run evidence.

ONE change: insert one constructed, fake posting at the front of the "jobs"
array. All other bytes are kept exactly as received from GitLab's board.
See evidence/seeded-run-note.md.

    python3 scripts/make_seeded.py
"""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
REAL = ROOT / "evidence" / "gitlab_jobs_20261030T201528Z.json"
SEEDED = ROOT / "evidence" / "gitlab_jobs_SEEDED_20261030T201528Z_plus-one-fake-posting.json"
PREFIX = b'{"jobs":['

FAKE_ID = 9999999002
FAKE_POSTING = {
    "_seeded": "CONSTRUCTED for JS1 seeded run - not a real GitLab posting",
    "absolute_url": "https://example.invalid/SEEDED-not-a-real-gitlab-posting",
    "id": FAKE_ID,
    "internal_job_id": 9999999001,
    "location": {"name": "Remote, United States"},
    "title": "Senior Machine Learning Engineer, RAG Platform [SEEDED - not a real GitLab posting]",
    "company_name": "GitLab",
    "updated_at": "2026-10-30T12:00:00-04:00",
    "first_published": "2026-10-30T12:00:00-04:00",
    "language": "en",
    "content": (
        "&lt;p&gt;SEEDED TEST POSTING. You will build retrieval-augmented generation "
        "(RAG) services that ground answers in customer code, written in Python "
        "and deployed on Kubernetes.&lt;/p&gt;"
    ),
}


def main():
    raw = REAL.read_bytes()
    assert raw.startswith(PREFIX), "unexpected response layout"
    ids = {j["id"] for j in json.loads(raw)["jobs"]}
    assert FAKE_ID not in ids, "fake id collides with a real posting"

    inserted = json.dumps(FAKE_POSTING, separators=(",", ":")).encode() + b","
    SEEDED.write_bytes(PREFIX + inserted + raw[len(PREFIX):])
    print(f"wrote {SEEDED.relative_to(ROOT)}: {len(ids)} real postings + 1 seeded (id {FAKE_ID})")


if __name__ == "__main__":
    main()
