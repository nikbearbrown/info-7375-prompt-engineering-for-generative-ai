"""Permission boundary cases P01–P20 from evidence/PERMISSION-BOUNDARIES.md.

Each docstring quotes that case's predicted result word for word. Approvals here are
in-code test objects built by the test, not human approvals.
"""

import json
import os

import pytest

from agent.approval import Approval, protected_path
from agent.errors import ReadDenied, RequestDenied, WriteDenied
from agent.fsio import FileGate
from agent.providers import Board, listing_url
from agent.transport import UrllibTransport, build_opener, send
from support import FakeHTTPSHandler, OpenSpy, TransportSpy, make_out_root

STRIPE = Board("greenhouse", "stripe")
NOTION = Board("ashby", "notion")
P01_URL = "https://boards-api.greenhouse.io/v1/boards/stripe/jobs"
P02_URL = "https://api.ashbyhq.com/posting-api/job-board/notion"
TIMEOUT = 10
RUN_ID = "run-test-1"


def assert_denied_before_transport(board, method, url):
    spy = TransportSpy()
    with pytest.raises(RequestDenied):
        send(board, method, url, transport=spy, timeout=TIMEOUT)
    assert spy.calls == []


# ---------- Network reads ----------

def test_p01_greenhouse_stripe_get_allowed():
    """P01 predicted result: "Allow one request." """
    assert listing_url(STRIPE) == P01_URL
    spy = TransportSpy()
    response = send(STRIPE, "GET", P01_URL, transport=spy, timeout=TIMEOUT)
    assert spy.calls == [("GET", P01_URL, TIMEOUT)]
    assert response.status == 200


def test_p02_ashby_notion_get_allowed():
    """P02 predicted result: "Allow one request." """
    assert listing_url(NOTION) == P02_URL
    spy = TransportSpy()
    response = send(NOTION, "GET", P02_URL, transport=spy, timeout=TIMEOUT)
    assert spy.calls == [("GET", P02_URL, TIMEOUT)]
    assert response.status == 200


def test_p03_example_com_denied():
    """P03 predicted result: "Deny before transport." """
    assert_denied_before_transport(STRIPE, "GET", "https://example.com/v1/boards/stripe/jobs")


def test_p04_suffixed_host_denied():
    """P04 predicted result: "Deny before transport." """
    assert_denied_before_transport(STRIPE, "GET", "https://boards-api.greenhouse.io.example.com/v1/boards/stripe/jobs")


def test_p05_userinfo_host_confusion_denied():
    """P05 predicted result: "Deny before transport." """
    assert_denied_before_transport(STRIPE, "GET", "https://boards-api.greenhouse.io@example.com/")


def test_p06_plain_http_denied():
    """P06 predicted result: "Deny before transport." """
    assert_denied_before_transport(STRIPE, "GET", "http://boards-api.greenhouse.io/v1/boards/stripe/jobs")


def test_p07_port_8443_denied():
    """P07 predicted result: "Deny before transport." """
    assert_denied_before_transport(STRIPE, "GET", "https://boards-api.greenhouse.io:8443/v1/boards/stripe/jobs")


def test_p08_post_denied():
    """P08 predicted result: "Deny before transport." """
    assert_denied_before_transport(STRIPE, "POST", P01_URL)


def test_p09_unconfigured_route_and_query_denied():
    """P09 predicted result: "Deny both before transport." """
    # An unconfigured route on the allowed host: a real Greenhouse route for a board not configured.
    assert_denied_before_transport(STRIPE, "GET", "https://boards-api.greenhouse.io/v1/boards/airbnb/jobs")
    # P01's exact route with JS1's ?content=true.
    assert_denied_before_transport(STRIPE, "GET", P01_URL + "?content=true")


def test_p10_redirect_recorded_not_followed():
    """P10 predicted result: "Record the redirect response. The transport spy shows exactly one request to the original URL." """
    handler = FakeHTTPSHandler(302, "Found", {"Location": "https://example.com/"}, b"moved")
    spy = TransportSpy(inner=UrllibTransport(build_opener(https_handler=handler)))
    response = send(STRIPE, "GET", P01_URL, transport=spy, timeout=TIMEOUT)
    assert response.status == 302 and response.is_redirect
    assert response.location == "https://example.com/"
    assert response.body == b"moved"
    assert spy.calls == [("GET", P01_URL, TIMEOUT)]
    assert handler.requests == [("GET", P01_URL)]


# ---------- Local writes ----------

def test_p11_summary_write_exact_bytes(tmp_path):
    """P11 predicted result: "Allow. The file has the exact supplied bytes." """
    root = make_out_root(tmp_path)
    gate = FileGate(root, RUN_ID)
    data = b'{"exit": "finished", "boards": []}\n'
    target = root / "runs" / RUN_ID / "summary.json"
    gate.write(target, data)
    assert target.read_bytes() == data


def test_p12_dotdot_escape_denied(tmp_path):
    """P12 predicted result: "Deny. The outside path is untouched." """
    root = make_out_root(tmp_path)
    gate = FileGate(root, RUN_ID)
    with pytest.raises(WriteDenied):
        gate.write(root / ".." / "escape.json", b"escaped")
    assert not (tmp_path / "escape.json").exists()


def test_p13_sibling_out_evil_denied(tmp_path):
    """P13 predicted result: "Deny. The sibling path is untouched." """
    root = make_out_root(tmp_path)
    sibling = tmp_path / "out-evil"
    sibling.mkdir()
    (sibling / "summary.json").write_bytes(b"original")
    gate = FileGate(root, RUN_ID)
    with pytest.raises(WriteDenied):
        gate.write(sibling / "summary.json", b"overwritten")
    assert (sibling / "summary.json").read_bytes() == b"original"
    assert sorted(p.name for p in sibling.iterdir()) == ["summary.json"]


def test_p14_symlink_outside_and_inside_targets_denied(tmp_path):
    """P14 predicted result: "Deny both. The linked targets are untouched." """
    root = make_out_root(tmp_path)
    gate = FileGate(root, RUN_ID)

    outside = tmp_path / "outside-target"
    outside.mkdir()
    (outside / "existing.json").write_bytes(b"outside original")
    link = root / "link"
    link.symlink_to(outside, target_is_directory=True)
    with pytest.raises(WriteDenied):
        gate.write(link / "summary.json", b"through outside link")
    assert sorted(p.name for p in outside.iterdir()) == ["existing.json"]
    assert (outside / "existing.json").read_bytes() == b"outside original"

    link.unlink()
    inside = root / "inside-target"
    inside.mkdir()
    (inside / "existing.json").write_bytes(b"inside original")
    link.symlink_to(inside, target_is_directory=True)
    with pytest.raises(WriteDenied):
        gate.write(link / "summary.json", b"through inside link")
    assert sorted(p.name for p in inside.iterdir()) == ["existing.json"]
    assert (inside / "existing.json").read_bytes() == b"inside original"


# ---------- Protected write ----------

def test_p15_protected_without_approval_denied(tmp_path):
    """P15 predicted result: "Deny. The protected path is untouched." """
    root = make_out_root(tmp_path)
    gate = FileGate(root, RUN_ID)
    with pytest.raises(WriteDenied):
        gate.write(protected_path(root), b'{"shortlist": []}\n')
    assert not protected_path(root).exists()


def test_p16_protected_with_exact_approval_allowed(tmp_path):
    """P16 predicted result: "Allow. The file has the approved bytes." """
    root = make_out_root(tmp_path)
    gate = FileGate(root, RUN_ID)
    data = b'{"shortlist": ["4012345"]}\n'
    approval = Approval.for_bytes(protected_path(root), data, RUN_ID)  # test object, not a human approval
    gate.write(protected_path(root), data, approval=approval)
    assert protected_path(root).read_bytes() == data


def test_p17_approval_reused_with_changed_payload_denied(tmp_path):
    """P17 predicted result: "Deny. The previously approved bytes remain." """
    root = make_out_root(tmp_path)
    gate = FileGate(root, RUN_ID)
    approved = b'{"shortlist": ["4012345"]}\n'
    approval = Approval.for_bytes(protected_path(root), approved, RUN_ID)
    gate.write(protected_path(root), approved, approval=approval)  # the P16 write
    with pytest.raises(WriteDenied):
        gate.write(protected_path(root), b'{"shortlist": ["4012345", "9999999"]}\n', approval=approval)
    assert protected_path(root).read_bytes() == approved


# ---------- Local reads ----------

def test_p18_state_read_allowed(tmp_path):
    """P18 predicted result: "Allow. Return the saved state." """
    root = make_out_root(tmp_path)
    saved = {"greenhouse/stripe": [101, 102], "ashby/notion": ["a1b2"]}
    saved_bytes = (json.dumps(saved, indent=2) + "\n").encode("utf-8")
    (root / "state.json").write_bytes(saved_bytes)  # test setup, outside the gate
    gate = FileGate(root, RUN_ID)
    returned = gate.read(root / "state.json")
    assert returned == saved_bytes
    assert json.loads(returned) == saved


def test_p19_unapproved_fixture_never_opened(tmp_path, monkeypatch):
    """P19 predicted result: "Deny before opening the file." """
    root = make_out_root(tmp_path)
    fixtures = tmp_path / "fixtures"
    fixtures.mkdir()
    selected = fixtures / "selected.json"
    unapproved = fixtures / "unapproved.json"
    selected.write_bytes(b'{"jobs": []}')
    unapproved.write_bytes(b'{"jobs": [{"id": 1}]}')
    gate = FileGate(root, RUN_ID, fixture_path=selected)
    opens = OpenSpy(monkeypatch)
    with pytest.raises(ReadDenied):
        gate.read(unapproved)
    assert opens.calls == []


def test_p20_approval_reused_in_new_run_denied(tmp_path, monkeypatch):
    """P20 predicted result: "Deny before opening the file for writing. The previously approved bytes remain." """
    root = make_out_root(tmp_path)
    data = b'{"shortlist": ["4012345"]}\n'
    first_run = FileGate(root, RUN_ID)
    approval = Approval.for_bytes(protected_path(root), data, RUN_ID)
    first_run.write(protected_path(root), data, approval=approval)  # the P16 write

    new_run = FileGate(root, "run-test-2")
    opens = OpenSpy(monkeypatch)
    with pytest.raises(WriteDenied):
        new_run.write(protected_path(root), data, approval=approval)
    assert opens.calls == []
    assert protected_path(root).read_bytes() == data  # OpenSpy passes reads through
    assert sorted(os.listdir(root / "protected")) == ["shortlist.json"]
