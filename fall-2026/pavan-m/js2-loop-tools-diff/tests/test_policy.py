
import json
import os

import httpx
import pytest

from agent.policy import (
    PolicyError,
    make_client,
    check_write,
    check_read,
    reset_state,
    state_path,
)


def project(tmp_path):
    """A fake project folder: out/, evidence/, data/, plus a GATE.md."""
    for d in ("out", "evidence", "data", "config"):
        (tmp_path / d).mkdir()
    (tmp_path / "GATE.md").write_text("original")
    return tmp_path


def recording_client():
    """A client whose fake internet records every request that is actually sent."""
    sent = []

    def handler(request):
        sent.append(str(request.url))
        if request.url.path == "/redirect":
            return httpx.Response(
                302,
                headers={"Location": "https://evil.example.org/steal"},
            )
        return httpx.Response(200, json={"jobs": []})

    return make_client(transport=httpx.MockTransport(handler)), sent


# ---------- Network: B1-B5 ----------

def test_B1_host_off_allow_list_refused():
    client, sent = recording_client()
    with pytest.raises(PolicyError):
        client.get("https://example.org/")
    assert sent == []


def test_B2_lookalike_host_refused():
    client, sent = recording_client()
    with pytest.raises(PolicyError):
        client.get("https://boards-api.greenhouse.io.evil.com/")
    assert sent == []


def test_B3_redirect_off_allow_list_refused():
    client, sent = recording_client()
    with pytest.raises(PolicyError):
        client.get(
            "https://boards-api.greenhouse.io/redirect",
            follow_redirects=True,
        )
    assert not any("evil.example.org" in url for url in sent)


def test_B4_post_refused():
    client, sent = recording_client()
    with pytest.raises(PolicyError):
        client.post("https://boards-api.greenhouse.io/")
    assert sent == []


def test_B5_allowed_host_get_allowed():
    client, sent = recording_client()
    r = client.get(
        "https://api.lever.co/v0/postings/palantir?mode=json"
    )
    assert r.status_code == 200
    assert len(sent) == 1


# ---------- Writes: B6-B10, B12 ----------

def test_B6_write_inside_out_allowed(tmp_path):
    root = project(tmp_path)
    p = check_write(
        root / "out" / "runs" / "test" / "summary.json",
        root,
    )
    assert p.resolve().is_relative_to((root / "out").resolve())


def test_B7_dotdot_traversal_refused(tmp_path):
    root = project(tmp_path)
    with pytest.raises(PolicyError):
        check_write(root / "out" / ".." / "GATE.md", root)
    assert (root / "GATE.md").read_text() == "original"


def test_B8_absolute_path_outside_refused(tmp_path):
    root = project(tmp_path)
    with pytest.raises(PolicyError):
        check_write(tmp_path.parent / "js2_escape.txt", root)


def test_B9_prefix_trick_refused(tmp_path):
    root = project(tmp_path)
    (root / "out-evil").mkdir()
    with pytest.raises(PolicyError):
        check_write(root / "out-evil" / "x.json", root)


def test_B10_symlink_escape_refused(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    project(root)

    outside = tmp_path / "outside"
    outside.mkdir()
    os.symlink(outside, root / "out" / "link")

    with pytest.raises(PolicyError):
        check_write(root / "out" / "link" / "x.json", root)

    assert list(outside.iterdir()) == []


def test_B12_write_to_read_only_evidence_refused(tmp_path):
    root = project(tmp_path)
    with pytest.raises(PolicyError):
        check_write(root / "evidence" / "new.json", root)


# ---------- Reads: B11, B13 ----------

def test_B11_read_evidence_allowed(tmp_path):
    root = project(tmp_path)
    f = root / "evidence" / "capture.json"
    f.write_text("{}")

    result = check_read(f, root)
    assert result.name == "capture.json"


def test_B13_read_outside_project_refused(tmp_path):
    root = tmp_path / "proj"
    root.mkdir()
    project(root)

    other = tmp_path / "other" / "README.md"
    other.parent.mkdir()
    other.write_text("not yours")

    with pytest.raises(PolicyError):
        check_read(other, root)


# ---------- Approval: B14-B16 ----------

def _seed_state(root, key):
    p = state_path(key, root)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps({"seen_ids": ["a", "b"]}))
    return p


def test_B14_reset_without_approval_refused(tmp_path):
    root = project(tmp_path)
    p = _seed_state(root, "lever:palantir")
    before = p.read_text()

    with pytest.raises(PolicyError):
        reset_state("lever:palantir", root, approvals=set())

    assert p.read_text() == before


def test_B15_reset_with_wrong_approval_refused(tmp_path):
    root = project(tmp_path)
    p = _seed_state(root, "lever:palantir")
    before = p.read_text()

    with pytest.raises(PolicyError):
        reset_state(
            "lever:palantir",
            root,
            approvals={"reset:ashby:openai"},
        )

    assert p.read_text() == before


def test_B16_reset_with_matching_approval_allowed(tmp_path):
    root = project(tmp_path)
    p = _seed_state(root, "lever:palantir")

    reset_state(
        "lever:palantir",
        root,
        approvals={"reset:lever:palantir"},
    )

    assert json.loads(p.read_text())["seen_ids"] == []
