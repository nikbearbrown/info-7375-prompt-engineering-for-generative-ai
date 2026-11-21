"""The loop: observe -> decide -> act -> record -> stop.

observe  read the question and the database's source checksum
decide   screen the question; ask the model for one proposal
act      check the SQL against the policy; run it read-only under a budget
record   every step goes into RunState, saved as a run file and a ledger line
stop     on a human decision, a policy refusal, a clarification, repeated
         denials, or a spent budget; never because the model said it was done
"""

import time
from pathlib import Path

from . import gate as gate_mod
from . import policy, prompt, screen
from .adapters import ModelUnavailable
from .config import SOURCE_SHA256, Budget
from .proposal import ProposalError, parse
from .state import RunState


def _single_int(result):
    if result.total_rows == 1 and len(result.columns) == 1:
        try:
            return int(float(result.rows[0][0]))
        except (TypeError, ValueError):
            return None
    return None


def run(question, adapter, db_path, contract_path, qid="adhoc", output_shape="",
        budget=Budget(), gate_mode="interactive", decision_file=None,
        state_dir="state", outputs_dir="outputs", expected_sha=SOURCE_SHA256,
        input_fn=input, output_fn=print):
    contract_path = Path(contract_path)
    state = RunState(question, qid, adapter.label, contract_path.name)
    started = time.monotonic()

    # observe
    meta = policy.read_metadata(db_path)
    state.add("observe", question=question, source_sha256=meta.get("source_sha256"))
    if meta.get("source_sha256") != expected_sha:
        state.stop("source_mismatch", found=meta.get("source_sha256"))
        state.save(state_dir)
        return state

    # decide (screen before any model call)
    verdict = screen.screen(question)
    if verdict.refuse:
        state.stop("refused_by_policy", category=verdict.category, reason=verdict.reason)
        state.save(state_dir)
        return state

    contract_text = contract_path.read_text(encoding="utf-8")
    con = policy.open_readonly(db_path)
    feedback = ""
    accepted = None
    try:
        for attempt in range(budget.max_proposals):
            if time.monotonic() - started > budget.question_seconds:
                state.stop("budget_exhausted", budget="question_seconds")
                break
            text = prompt.build(contract_text, question, output_shape, feedback)
            state.used["proposals"] += 1
            try:
                reply = adapter.propose(qid, text, attempt)
            except ModelUnavailable as exc:
                state.used["errors"] += 1
                state.add("model_unavailable", attempt=attempt, error=str(exc))
                state.stop("budget_exhausted", budget="model_unavailable", error=str(exc))
                break
            state.add("decide", attempt=attempt, adapter=adapter.label, reply=reply)
            try:
                proposal = parse(reply)
            except ProposalError as exc:
                state.used["errors"] += 1
                feedback = f"The reply could not be parsed: {exc}."
                state.add("reject_reply", attempt=attempt, reason=str(exc))
                continue
            if proposal.needs_clarification:
                state.stop("deferred_clarification", interpretation=proposal.interpretation)
                break

            # act
            denied = None
            for name, sql in (("sql", proposal.sql), ("rows_sql", proposal.rows_sql)):
                check = policy.check_text(sql)
                if not check.allowed:
                    denied = f"{name}: {check.reason}"
                    break
            if denied is None:
                try:
                    answer = policy.execute(con, proposal.sql, budget.statement_seconds, budget.answer_rows)
                    evidence = policy.execute(con, proposal.rows_sql, budget.statement_seconds, budget.display_rows)
                except policy.PolicyDenied as exc:
                    denied = str(exc)
                except policy.BudgetExceeded as exc:
                    state.used["errors"] += 1
                    state.add("budget_interrupt", attempt=attempt, error=str(exc))
                    state.stop("budget_exhausted", budget="statement_seconds")
                    break
                except Exception as exc:  # SQL error: tell the model, try again
                    state.used["errors"] += 1
                    feedback = f"The SQL failed in SQLite: {exc}."
                    state.add("sql_error", attempt=attempt, error=str(exc))
                    continue
            if denied is not None:
                state.used["denials"] += 1
                state.add("policy_denied", attempt=attempt, reason=denied,
                          sql=proposal.sql, rows_sql=proposal.rows_sql)
                if state.used["denials"] >= budget.max_denials:
                    state.stop("stopped_policy_denials", reason=denied)
                    break
                feedback = f"The SQL was refused by the read-only policy: {denied}."
                continue

            check_note = ""
            if proposal.answer_type == "count":
                value = _single_int(answer)
                try:
                    behind = policy.count_rows(con, proposal.rows_sql, budget.statement_seconds)
                except Exception as exc:
                    behind, check_note = None, f"could not count matching rows ({exc})"
                if value is not None and behind is not None:
                    check_note = (f"answer {value} matches {behind} matching rows" if value == behind
                                  else f"MISMATCH: answer {value} but {behind} matching rows")
            state.add("act", attempt=attempt, sql=proposal.sql, rows_sql=proposal.rows_sql,
                      answer_columns=answer.columns, answer_rows=answer.total_rows,
                      evidence_rows=evidence.total_rows, seconds=answer.seconds + evidence.seconds,
                      check=check_note)
            accepted = (proposal, answer, evidence, check_note)
            break
        else:
            state.stop("budget_exhausted", budget="max_proposals")
    finally:
        con.close()

    if accepted is None:
        if state.stop_reason is None:
            state.stop("budget_exhausted", budget="max_proposals")
        state.save(state_dir)
        return state

    proposal, answer, evidence, check_note = accepted
    state.result = {"interpretation": proposal.interpretation, "sql": proposal.sql,
                    "rows_sql": proposal.rows_sql, "answer_type": proposal.answer_type,
                    "limits": proposal.limits, "columns": answer.columns,
                    "rows": [list(r) for r in answer.rows], "total_rows": answer.total_rows,
                    "evidence_rows": evidence.total_rows, "check": check_note}

    # gate
    view = gate_mod.build_view(question, proposal, answer, evidence, check_note)
    state.view_hash = gate_mod.view_hash(view)
    decision = gate_mod.decide(view, gate_mode, decision_file, input_fn, output_fn)
    state.decision = decision.decision
    state.add("gate", mode=gate_mode, decision=decision.decision, approver=decision.approver,
              note=decision.note, bound_hash=decision.bound_hash, reason=decision.reason)
    if decision.decision == "not_requested":
        state.stop("answered_not_released")
    elif decision.decision == "approve" and decision.bound_hash == state.view_hash:
        path = gate_mod.export_report(outputs_dir, state.run_id, view, decision)
        state.export_path = str(path)
        state.stop("approved_and_exported", path=str(path))
    elif decision.decision == "refuse":
        state.stop("refused_by_human", note=decision.note)
    else:
        state.stop("deferred_by_human", reason=decision.reason or decision.note)
    state.save(state_dir)
    return state
