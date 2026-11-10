"""Permission boundary suite B1–B20 (BOUNDARY_TABLE.md; predictions committed before this file).
Every denied case also checks that no side effect happened. SYNTHETIC inputs; no real network."""
import http.client
import http.server
import json
import os
import threading

import pytest

import agent.loop as loop_mod
from agent import judge as judge_mod
from agent.loop import EXIT, Budget, LIMITS, export_run, fetch_board
from agent.net import https_get
from agent.policy import PathPolicy, PolicyError, check_request
from tests.js2_helpers import GH, NOT_RELEVANT, RELEVANT, Clock, Transport, board, gh_body, make_root, run


@pytest.fixture
def root(tmp_path):
    r = make_root(tmp_path, [board("greenhouse", "alpha")])
    (r / "GATE.md").write_text("gate text")
    return r


def test_b01_allowed_greenhouse_url():
    assert check_request("GET", "https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true")


def test_b02_allowed_ashby_url():
    assert check_request("GET", "https://api.ashbyhq.com/posting-api/job-board/notion")


class OffList:
    name = "greenhouse"

    @staticmethod
    def url(board):
        return "https://api.lever.co/v0/postings/x"


class _NullTrace:
    seq = 0

    def __call__(self, *a, **k):
        self.seq += 1


def _ctx(root, transport):
    clock = Clock()
    (root / "out" / "raw").mkdir(parents=True, exist_ok=True)
    return {"budget": Budget(dict(LIMITS), clock, clock()), "trace": _NullTrace(), "transport": transport,
            "clock": clock, "sleep": clock.sleep, "policy": PathPolicy(root), "run_dir": root / "out",
            "dispatched": set(), "n_raw": 1}


def test_b03_off_list_host_refused_before_dispatch(root):
    t = Transport({})
    ctx = _ctx(root, t)
    with pytest.raises(PolicyError, match="not on the allow-list"):
        fetch_board({"key": "x", "provider": "greenhouse", "board": "x", "adapter": OffList}, ctx)
    assert t.calls == [] and ctx["budget"].http_used == 0


def test_b04_deceptive_suffix_refused():
    with pytest.raises(PolicyError):
        check_request("GET", "https://boards-api.greenhouse.io.evil.com/v1/boards/x/jobs?content=true")


@pytest.mark.parametrize("url", [
    "http://boards-api.greenhouse.io/v1/boards/x/jobs?content=true",
    "https://user:pw@boards-api.greenhouse.io/v1/boards/x/jobs?content=true",
    "https://boards-api.greenhouse.io:8443/v1/boards/x/jobs?content=true",
    "https://boards-api.greenhouse.io/v1/boards/x/jobs/123?content=true",
    "https://boards-api.greenhouse.io/v1/boards/x/jobs?content=true&questions=true",
    "https://api.ashbyhq.com/posting-api/job-board/notion?includeCompensation=true",
    "https://api.ashbyhq.com/../admin",
])
def test_b05_scheme_userinfo_port_path_refused(url):
    with pytest.raises(PolicyError):
        check_request("GET", url)


def test_b06_write_method_refused():
    with pytest.raises(PolicyError, match="only GET"):
        check_request("POST", "https://boards-api.greenhouse.io/v1/boards/figma/jobs?content=true")


class _Server:
    def __init__(self, handler_fn):
        hits = self.hits = []

        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                hits.append(self.path)
                handler_fn(self)

            def log_message(self, *a):
                pass

        self.httpd = http.server.HTTPServer(("127.0.0.1", 0), H)
        self.port = self.httpd.server_address[1]
        threading.Thread(target=self.httpd.serve_forever, daemon=True).start()

    def close(self):
        self.httpd.shutdown()
        self.httpd.server_close()


def test_b07_redirect_refused_destination_never_contacted(root):
    dest = _Server(lambda h: (h.send_response(200), h.end_headers(), h.wfile.write(gh_body(RELEVANT))))

    def redirect(h):
        h.send_response(302)
        h.send_header("Location", f"http://127.0.0.1:{dest.port}/v1/boards/alpha/jobs?content=true")
        h.send_header("Content-Length", "0")
        h.end_headers()

    origin = _Server(redirect)
    try:
        def transport(url, timeout, deadline):  # the real client; only the TCP endpoint is local
            return https_get(url, timeout, deadline,
                             conn_factory=lambda host, port, timeout: http.client.HTTPConnection(
                                 "127.0.0.1", origin.port, timeout=timeout))
        code, rep, run_dir = run(root, transport)
    finally:
        origin.close()
        dest.close()
    assert code == EXIT["error"] and rep["status"] == "error"
    assert len(origin.hits) == 1 and dest.hits == []  # the destination received no request
    assert not (root / "out/state/seen.json").exists()


def test_b08_posting_supplied_url_refused():
    with pytest.raises(PolicyError):
        check_request("GET", "https://jobs.ashbyhq.com/notion/1fc309c8-da20-4ff2-84c7-8b863ece2b0a")


def test_b09_write_inside_out_allowed(root):
    p = PathPolicy(root).write_new("out/runs/x/report.json", b"{}")
    assert p.read_bytes() == b"{}" and p.parent.parent.name == "runs"


def test_b10_parent_traversal_refused(root):
    with pytest.raises(PolicyError):
        PathPolicy(root).write_new("out/../GATE.md", b"overwritten")
    assert (root / "GATE.md").read_text() == "gate text"


def test_b11_sibling_prefix_refused(root):
    with pytest.raises(PolicyError):
        PathPolicy(root).write_new("out-evil/x.json", b"x")
    assert not (root / "out-evil").exists()


def test_b12_symlink_escape_refused(root, tmp_path):
    outside = tmp_path / "outside"
    outside.mkdir()
    os.symlink(outside, root / "out" / "link")
    with pytest.raises(PolicyError):
        PathPolicy(root).write_new("out/link/x.json", b"x")
    assert list(outside.iterdir()) == []


def test_b12b_symlink_at_the_target_file_is_not_followed(root, tmp_path):
    victim = tmp_path / "victim.txt"
    victim.write_text("keep")
    os.symlink(victim, root / "out" / "t.json")
    with pytest.raises(PolicyError):
        PathPolicy(root).write_new("out/t.json", b"x")
    assert victim.read_text() == "keep"


def test_b13_read_allowed_write_refused(root):
    pol = PathPolicy(root)
    before = (root / "config/boards.json").read_bytes()
    assert pol.check_read("config/boards.json").read_bytes() == before
    with pytest.raises(PolicyError):
        pol.write_new("config/boards.json", b"{}")
    assert (root / "config/boards.json").read_bytes() == before


@pytest.mark.parametrize("path", ["approvals/r.json", "out/../approvals/r.json"])
def test_b14_runtime_cannot_write_approval(root, path):
    with pytest.raises(PolicyError):
        PathPolicy(root).write_new(path, b"{}")
    assert list((root / "approvals").iterdir()) == []


def test_b15_protected_export_needs_export_path(root):
    with pytest.raises(PolicyError, match="protected"):
        PathPolicy(root).write_new("out/approved-shortlists/r.json", b"{}")
    assert not (root / "out/approved-shortlists").exists()


def _proposal_run(root):
    A = GH.format("alpha")
    run(root, Transport({A: [(200, gh_body(NOT_RELEVANT))]}))
    code, rep, run_dir = run(root, Transport({A: [(200, gh_body(NOT_RELEVANT, RELEVANT))]}), propose_export=True)
    assert rep["approval_request"]["write_occurred"] is False
    return rep["run_id"], rep["approval_request"]


@pytest.fixture
def no_network_no_model(monkeypatch):
    def boom(*a, **k):
        raise AssertionError("export must make no board request or model call")
    monkeypatch.setattr(loop_mod, "https_get", boom)
    monkeypatch.setattr(judge_mod, "call_claude", boom)


def test_b16_export_without_approval_refused(root, no_network_no_model):
    run_id, prop = _proposal_run(root)
    assert export_run(root, run_id) == EXIT["incomplete"]
    assert not (root / prop["destination"]).exists()
    results = list((root / "out/exports").glob(f"{run_id}.*.result.json"))
    assert len(results) == 1 and json.loads(results[0].read_text())["write_occurred"] is False


@pytest.mark.parametrize("field, value", [("sha256", "0" * 64), ("destination", "out/approved-shortlists/other.json"),
                                          ("run_id", "20990101T000000000Z_other")])
def test_b17_export_with_mismatched_approval_refused(root, no_network_no_model, field, value):
    run_id, prop = _proposal_run(root)
    appr = {k: prop[k] for k in ("run_id", "operation", "destination", "sha256")}
    appr[field] = value
    (root / "approvals" / f"{run_id}.json").write_text(json.dumps(appr))
    assert export_run(root, run_id) == EXIT["error"]
    assert not (root / prop["destination"]).exists()


def test_b18_matching_approval_creates_once(root, no_network_no_model):
    run_id, prop = _proposal_run(root)
    appr = {k: prop[k] for k in ("run_id", "operation", "destination", "sha256")}
    (root / "approvals" / f"{run_id}.json").write_text(json.dumps(dict(appr, approved_by="test")))
    assert export_run(root, run_id) == EXIT["finished"]
    dest = root / prop["destination"]
    first = dest.read_bytes()
    assert first == (root / prop["proposed_bytes_file"]).read_bytes()
    doc = json.loads(first)
    assert doc["entries"][0]["posting_id"] == "101" and doc["entries"][0]["RECORD_verdict"] == "relevant"
    assert export_run(root, run_id) == EXIT["error"]  # create-only
    assert dest.read_bytes() == first


def test_b19_repeated_action_refused(root):
    A = GH.format("alpha")
    t = Transport({A: [(200, gh_body(RELEVANT)), (200, gh_body(RELEVANT))]})
    ctx = _ctx(root, t)
    b = {"key": "greenhouse:alpha", "provider": "greenhouse", "board": "alpha",
         "adapter": __import__("agent.providers", fromlist=["Greenhouse"]).Greenhouse}
    fetch_board(b, ctx)
    with pytest.raises(PolicyError, match="repeated action"):
        fetch_board(b, ctx)
    assert t.calls == [A]


def test_b20_read_outside_root_refused(root):
    with pytest.raises(PolicyError):
        PathPolicy(root).check_read("../../secret.txt")
