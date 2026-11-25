"""Case 9. Cases and expected verdicts drafted with Claude (chat), hand-checked and adopted by Deepak on 2026-10-29; code typed by Claude Code from his answers on 2026-10-29, before any implementation."""
from datetime import timedelta

from conftest import BOARD_URL, FIXED_NOW, FakeOpener, board_body, job, latest_report, run_args, run_cli

# Constructed postings, not from any real board. With the persona résumé they reach different
# steps of The rule, so their verdicts differ and a wrong pairing has something to show.
JOBS = [
    job(9101, "Machine Learning Engineer, Payments", "Boston, MA"),  # relevant
    job(9102, "Director of Sales", "Boston, MA"),  # not_relevant, step 1
    job(9103, "Account Executive", "Chicago, IL"),  # not_relevant, step 2
    job(9104, "AI Engineer", "Toronto, Canada"),  # not_relevant, step 3
    job(9105, "Data Scientist, Risk", "Remote in the US"),  # relevant
]
SHUFFLED = [JOBS[i] for i in (3, 0, 4, 2, 1)]


def _tokens(text):
    out, cur = [], ""
    for ch in str(text).lower():
        if ch.isalnum() or ch in "+#":
            cur += ch
        elif cur:
            out.append(cur)
            cur = ""
    if cur:
        out.append(cur)
    return out


def _whole_word(term, text):
    t, x = _tokens(term), _tokens(text)
    return bool(t) and any(x[i : i + len(t)] == t for i in range(len(x) - len(t) + 1))


def _resolve(doc, pointer):
    """RFC 6901 JSON Pointer lookup."""
    for part in pointer.split("/")[1:]:
        part = part.replace("~1", "/").replace("~0", "~")
        doc = doc[int(part)] if isinstance(doc, list) else doc[part]
    return doc


def _run(workdir, jobs, now):
    opener = FakeOpener({BOARD_URL: (200, board_body(jobs), {"Content-Type": "application/json"})})
    assert run_cli(run_args(), opener=opener, now=now) == 0
    return {r["posting_id"]: r for r in latest_report(workdir)["records"]}


def test_ac09_shuffle_keeps_each_verdict_with_its_posting(workdir):
    _run(workdir, [], FIXED_NOW)  # baseline
    state = workdir / "state" / "acme.json"
    after_baseline = state.read_bytes()

    first = _run(workdir, JOBS, FIXED_NOW + timedelta(minutes=1))
    state.write_bytes(after_baseline)  # same seen_ids, so the same postings are new again
    second = _run(workdir, SHUFFLED, FIXED_NOW + timedelta(minutes=2))

    by_id = {str(j["id"]): j for j in JOBS}
    assert sorted(first) == sorted(second) == sorted(by_id)
    assert {first[i]["record"]["verdict"] for i in by_id} == {"relevant", "not_relevant"}

    for pid, posting in by_id.items():
        assert second[pid]["record"]["verdict"] == first[pid]["record"]["verdict"]
        for rec in (first[pid], second[pid]):
            assert rec["title"] == posting["title"]
            posting_cites = [c for c in rec["record"]["citations"] if c["source"] == "posting"]
            assert posting_cites
            for c in posting_cites:
                assert _whole_word(c["value"], _resolve(posting, c["path"])), (pid, c)
