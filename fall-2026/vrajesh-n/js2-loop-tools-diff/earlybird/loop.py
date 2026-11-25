"""The agent loop: for each board, decide -> act (fetch) -> observe (parse) -> record (watch, rule) -> next.

It stops on one of four designed exits (GATE.md): finished, incomplete, budget-exhausted, error.
Reaching an exit says the loop stopped, not that its numbers are right; that is check.py's job.
"""
from . import Refused, boards, rule, validate, watch
from .gate import BudgetExhausted

EXIT_CODES = {"finished": 0, "incomplete": 1, "error": 2, "budget-exhausted": 3}


def run(board_list, tools, budget, trace, state, resume, day, label, parse=boards.parse):
    results, reason = [], None
    try:
        for i, b in enumerate(board_list):
            key = b["key"]
            trace.record(key, "decide", detail=f"board {i + 1}/{len(board_list)}: fetch {b['platform']} board")
            budget.start_board(key)
            obs = tools.fetch(key, boards.url(b), boards.raw_name(b))
            if obs["status"] != "ok":
                # never invent a value for a failed board: counts are None, not 0
                results.append({"key": key, "status": obs["status"], "postings": None, "new": None,
                                "error": obs["error"], "raw_path": obs.get("raw_path")})
                continue
            try:
                postings = parse(b["platform"], obs["body"])
            except boards.ShapeError as e:
                trace.record(key, "parse", result="error", error=str(e), raw_path=obs["raw_path"])
                results.append({"key": key, "status": "error", "postings": None, "new": None,
                                "error": f"bad response shape: {e}", "raw_path": obs["raw_path"]})
                continue
            trace.record(key, "parse", result="ok", count=len(postings), raw_path=obs["raw_path"])
            baseline = key not in state["boards"]
            new = watch.update(state, key, postings, day, label)
            rows = []
            for p in new:
                rec = rule.judge(p, resume)
                rows.append({"record": rec, "record_errors": validate.errors(rec, p, resume),
                             "location": p.get("location"), "url": p.get("url")})
            relevant = sum(r["record"]["verdict"] == "relevant" for r in rows)
            invalid = sum(bool(r["record_errors"]) for r in rows)
            trace.record(key, "record", new=len(new), baseline=baseline, relevant=relevant,
                         invalid_records=invalid)
            results.append({"key": key, "status": "ok", "postings": len(postings), "new": len(new),
                            "baseline": baseline, "relevant": relevant, "invalid_records": invalid,
                            "raw_path": obs["raw_path"], "rows": rows})
        status = "incomplete" if any(r["status"] != "ok" for r in results) else "finished"
    except BudgetExhausted as e:
        status, reason = "budget-exhausted", str(e)
    except Refused as e:
        status, reason = "error", f"refused: {e}"
    except Exception as e:  # unexpected: stop everything and hand it to a human
        status, reason = "error", f"{type(e).__name__}: {e}"
    done = {r["key"] for r in results}
    not_attempted = [b["key"] for b in board_list if b["key"] not in done]
    trace.record(None, "exit", label=label, status=status, reason=reason, not_attempted=not_attempted)
    return {"label": label, "day": day, "exit": status, "reason": reason, "boards": results,
            "not_attempted": not_attempted, "budget": budget.snapshot()}
