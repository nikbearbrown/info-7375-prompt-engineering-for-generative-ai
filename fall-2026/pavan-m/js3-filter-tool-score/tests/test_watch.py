import json
from pathlib import Path

import httpx
import pytest

from agent.watch import run_watch
from agent.net import make_client, HostNotAllowed
from agent.resume import load_resume


PERSONA = Path(__file__).parent.parent / "data" / "persona_alex.json"


def write_fake_response(path, ids):
    """Write a tiny fake Greenhouse response with the given posting ids."""
    data = {
        "jobs": [{"id": i, "title": f"Job {i}"} for i in ids],
        "meta": {"total": len(ids)},
    }
    path.write_text(json.dumps(data))


def write_resume(path, **changes):
    """Copy Alex's résumé, change some fields, save it to path."""
    data = json.loads(PERSONA.read_text())
    data.update(changes)
    path.write_text(json.dumps(data))
    return path


def test_first_run_baseline_reports_zero_new_postings(tmp_path):
    seeded = tmp_path / "response.json"
    write_fake_response(seeded, [1, 2, 3])
    state_path = tmp_path / "state.json"
    evidence_dir = tmp_path / "evidence"

    result = run_watch(state_path, evidence_dir, seeded_file=seeded)

    assert result["baseline"] is True
    assert result["new_ids"] == []
    state = json.loads(state_path.read_text())
    assert set(state["seen_ids"]) == {1, 2, 3}


def test_seeded_run_uses_saved_response_without_greenhouse_request(tmp_path):
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps({"seen_ids": [1, 2]}))
    seeded = tmp_path / "response.json"
    write_fake_response(seeded, [1, 2, 3])
    evidence_dir = tmp_path / "evidence"

    requests_made = []

    def handler(request):
        requests_made.append(request)
        return httpx.Response(500)

    client = httpx.Client(transport=httpx.MockTransport(handler))

    result = run_watch(state_path, evidence_dir, client=client, seeded_file=seeded)

    assert result["mode"] == "seeded"
    assert result["new_ids"] == [3]
    assert len(requests_made) == 0
    seeded_evidence = list(evidence_dir.glob("*seeded*"))
    assert len(seeded_evidence) > 0
    assert seeded_evidence[0].read_text() == seeded.read_text()


def test_rejects_unapproved_hosts_and_redirects():
    def handler(request):
        if request.url.path == "/redirect":
            return httpx.Response(302, headers={"Location": "https://evil.example.org/steal"})
        return httpx.Response(200, json={"jobs": [], "meta": {"total": 0}})

    client = make_client(transport=httpx.MockTransport(handler))

    response = client.get("https://boards-api.greenhouse.io/v1/boards/gleanwork/jobs")
    assert response.status_code == 200

    with pytest.raises(HostNotAllowed):
        client.get("https://evil.example.org/steal")

    with pytest.raises(HostNotAllowed):
        client.get("https://boards-api.greenhouse.io/redirect", follow_redirects=True)


def test_rejects_nonfictional_resume_identity(tmp_path):
    good = write_resume(tmp_path / "good.json")
    real_email = write_resume(tmp_path / "email.json", email="alex.morgan@gmail.com")
    real_phone = write_resume(tmp_path / "phone.json", phone="(617) 867-5309")

    resume = load_resume(good)
    assert resume["name"] == "Alex Morgan"

    with pytest.raises(ValueError):
        load_resume(real_email)

    with pytest.raises(ValueError):
        load_resume(real_phone)


def test_failed_fetch_or_rule_preserves_previous_state(tmp_path):
    state_path = tmp_path / "state.json"
    state_path.write_text(json.dumps({"seen_ids": [1, 2]}))
    before = state_path.read_text()
    evidence_dir = tmp_path / "evidence"

    def handler(request):
        return httpx.Response(500)

    client = make_client(transport=httpx.MockTransport(handler))

    with pytest.raises(Exception):
        run_watch(state_path, evidence_dir, client=client)

    assert state_path.read_text() == before