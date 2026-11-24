import httpx

from agent.loop import run_loop
from agent.policy import make_client


def project(tmp_path):
    for d in ("out", "evidence", "data", "config"):
        (tmp_path / d).mkdir()
    return tmp_path


LEVER = {"key": "lever:palantir", "system": "lever",
         "url": "https://api.lever.co/v0/postings/palantir?mode=json"}


def lever_postings(*ids):
    """Lever returns a plain list. Shape copied from my Nov 9 capture."""
    return [{"id": i, "text": f"Job {i}", "categories": {"location": "Remote"},
             "descriptionPlain": "x"} for i in ids]


def fake_net(body):
    def handler(request):
        return httpx.Response(200, json=body)
    return make_client(transport=httpx.MockTransport(handler))


NO_SLEEP = lambda s: None
A = "6ed76ce8-4156-4b60-b120-403538bd66cd"   # real Palantir id format, from run 1
B = "0ccbe620-a3ef-41d1-a5c4-68e56b3c91d0"


def test_string_ids_are_tracked_not_dropped(tmp_path):
    root = project(tmp_path)
    s1 = run_loop([LEVER], root, fake_net(lever_postings(A)), sleep=NO_SLEEP)
    b1 = s1["boards"]["lever:palantir"]

    assert b1["usable_ids"] == 1
    assert b1["unusable_ids"] == 0

    s2 = run_loop([LEVER], root, fake_net(lever_postings(A, B)), sleep=NO_SLEEP)
    b2 = s2["boards"]["lever:palantir"]

    assert len(b2["new"]) == 1
    assert b2["new"][0].endswith(B)


def test_empty_or_missing_ids_are_still_unusable(tmp_path):
    """The fix must not simply accept everything."""
    root = project(tmp_path)
    blank = lever_postings("tmp1")[0]
    blank["id"] = ""                  # same posting shape, empty id
    no_id = lever_postings("tmp2")[0]
    del no_id["id"]                   # same posting shape, no id at all
    body = lever_postings(A) + [blank, no_id]
    s = run_loop([LEVER], root, fake_net(body), sleep=NO_SLEEP)
    b = s["boards"]["lever:palantir"]

    assert b["usable_ids"] == 1
    assert b["unusable_ids"] == 2