import json

from agent import fetch, main


def test_25_replay_uses_saved_file_without_fetching(monkeypatch, tmp_path, postings):
    def no_fetch(url):
        raise AssertionError("fetch attempted during --replay")

    monkeypatch.setattr(fetch, "fetch_board", no_fetch)
    raw_before = sorted(main.RAW_DIR.glob("*")) if main.RAW_DIR.exists() else []

    saved = tmp_path / "saved.json"
    saved.write_text(json.dumps({"jobs": [postings[k] for k in ("swe_boston_plain", "swe_london", "swe_brussels")]}))
    state = tmp_path / "seen_ids.json"
    state.write_text(json.dumps({"klaviyo": [4000001]}))
    out = tmp_path / "out"

    main.main(["--replay", str(saved), "--state", str(state), "--out", str(out),
               "--no-claude", "--label", "SEEDED"])

    run = json.loads(next((out / "results").glob("*.json")).read_text())[-1]
    assert run["label"] == "SEEDED" and run["replay"] is True
    assert sorted(r["posting_id"] for r in run["results"]) == [4000007, 4000012]
    assert json.loads(state.read_text())["klaviyo"] == [4000001, 4000007, 4000012]
    after = sorted(main.RAW_DIR.glob("*")) if main.RAW_DIR.exists() else []
    assert after == raw_before  # replay saves no new raw file
