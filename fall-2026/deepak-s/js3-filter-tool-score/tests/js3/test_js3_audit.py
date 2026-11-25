"""Phase 3b: the reject-audit draw. Written by Claude Code (claude-opus-5-5), 2026-11-25.
All filter outputs here are SEEDED (hand-built)."""
import js3kit  # noqa: F401
from jobwatch import audit


def out(i, decision, score, board="seeded:b"):
    return {"key": f"{board}:{i}", "board": board, "posting_id": str(i), "decision": decision, "score": score}


def outputs():
    o = [out(i, "reject", None) for i in range(100)]                 # gate rejects
    o += [out(100 + i, "reject", 7) for i in range(14)]               # scored rejects, all at 7
    o += [out(200 + i, "keep", 8 + (i % 3)) for i in range(12)]       # kept: 8, 9, 10
    o += [out(300 + i, "abstain", None) for i in range(5)]
    o.append({"key": None, "board": "seeded:failed", "posting_id": None, "scope": "board", "decision": "abstain", "score": None})
    return o


def test_groups_are_disjoint_exclude_heldout_and_abstentions_and_follow_the_order():
    hk = {"seeded:b:100", "seeded:b:200", "seeded:b:5"}
    g, pools = audit.draw(outputs(), hk, seed=1)
    keys = [o["key"] for grp in g.values() for o in grp]
    assert len(keys) == len(set(keys)) and not set(keys) & hk
    assert all(o["decision"] != "abstain" for grp in g.values() for o in grp)
    assert [len(g[k]) for k in audit.SIZES] == [10, 5, 30, 6]
    assert all(o["score"] == 7 for o in g["close_call_reject"])
    assert pools == {"close_call_reject": 13, "close_call_keep": 11, "random_reject": 102, "random_keep": 6}


def test_close_call_keeps_take_the_nearest_scores_first():
    g, _ = audit.draw(outputs(), set(), seed=1)
    assert sorted(o["score"] for o in g["close_call_keep"]) == [8, 8, 8, 8, 9]


def test_draw_is_reproducible_with_the_seed_and_varies_with_it():
    a, _ = audit.draw(outputs(), set(), seed=4)
    b, _ = audit.draw(list(reversed(outputs())), set(), seed=4)
    c, _ = audit.draw(outputs(), set(), seed=5)
    keys = lambda g: [o["key"] for grp in g.values() for o in grp]  # noqa: E731
    assert keys(a) == keys(b) and keys(a) != keys(c)


def test_shortfall_when_there_are_no_scored_rejects():
    o = [out(i, "reject", None) for i in range(40)] + [out(100 + i, "keep", 13) for i in range(3)]
    g, pools = audit.draw(o, set(), seed=1)
    assert [len(g[k]) for k in audit.SIZES] == [0, 3, 30, 0]
    assert pools["close_call_reject"] == 0 and pools["random_keep"] == 0


# --- near-decision group ----------------------------------------------------------------------------
def role_out(i, decision, rule="R01"):
    o = out(i, decision, None if decision == "reject" else 10)
    o["matched"] = [{"rule": rule, "field": "title"}]
    return o


def test_near_decision_takes_every_role_matched_reject_minus_heldout_and_drawn():
    outs = [role_out(1, "reject"), role_out(2, "reject"), role_out(3, "keep"), role_out(4, "reject", rule="X05"),
            {**out(5, "reject", None), "matched": []}, role_out(6, "reject")]
    picked = audit.near_decision(outs, heldout_keys={"seeded:b:2"}, already={"seeded:b:6"})
    assert [o["key"] for o in picked] == ["seeded:b:1"]


def test_append_keeps_existing_rows_and_adds_one_comment(tmp_path):
    from jobwatch import sheets
    from jobwatch.policy import Policy
    from jobwatch.tools import Tools
    tools = Tools(Policy(str(tmp_path), read_dirs=("audit", "data"), write_dirs=("audit", "data/texts")))
    (tmp_path / "audit").mkdir()
    old_rows = [{"posting_key": "seeded:b:9", "group": "random_reject", "title": "SEEDED", "location": "", "url": "",
                 "text_path": "data/texts/x.txt", "verdict": "", "override_reason": ""}]
    (tmp_path / "audit" / "a.csv").write_bytes(sheets.sheet_bytes(["head", "verdict: ..."], audit.COLUMNS, old_rows))
    lines = [{"key": f"seeded:b:{i}", "board": "seeded:b", "posting_id": str(i), "url": None, "title": f"SEEDED {i}",
              "location": None, "text": "t"} for i in (1, 9)]
    new = audit.append_near_decision(tools, lines, [role_out(1, "reject"), role_out(9, "reject")], "SEEDED", set(), "audit/a.csv")
    comments, _, rows = sheets.parse_sheet((tmp_path / "audit" / "a.csv").read_bytes())
    assert rows[0] == old_rows[0] and [r["posting_key"] for r in rows] == ["seeded:b:9", "seeded:b:1"] and len(new) == 1
    assert comments[0] == "head" and comments[-1] == "verdict: ..." and comments[1].startswith("near_decision: 1 drawn")
