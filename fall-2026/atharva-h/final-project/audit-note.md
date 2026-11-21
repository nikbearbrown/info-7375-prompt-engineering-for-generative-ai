# Audit note

Packet document 9 of 10. Previous: [artifact.md](artifact.md) · Next: [transfer-reflection.md](transfer-reflection.md)

## 1. Predictions before the critique

Written 2026-11-21, before the reviewer saw anything. Kept unedited.

What I expect an independent code-and-evidence reviewer to find:
1. **The text check is regex-based and can be fooled.** For example, identifiers in double quotes or unusual whitespace. I expect this to be a real but contained finding, because the authorizer and the read-only connection are separate layers behind it.
2. **The recorded adapter weakens the "agentic" claim.** The model step was not live inside the loop; replies were obtained from a Claude subagent and replayed. I expect this to be called genuine.
3. **The count-versus-rows check is not independent.** Both queries come from the same model reply, so a consistent mistake passes it. I expect this to be genuine.
4. **The answer key and the agent were both built with Claude.** Independence rests on separate code paths (Python counting versus model SQL), not on separate people. I expect this to be genuine, and it's the main limit of the evaluation.
5. **Small samples.** 10 development and 5 held-out questions can't support a general accuracy claim.

## 2. The reviewer's findings

**Reviewer:** a separate Claude Code subagent that didn't build the project. It made 47 tool calls, reviewed commit `53fbca0`, and was told to break the policy, the gate, the key independence, the freeze and the comparators. Its full report, word for word: [evidence/independent-review-2026-11-21.md](evidence/independent-review-2026-11-21.md).

**Judgments below are Claude's triage. The owner confirms or overrides each one in [SIGNOFF.md](SIGNOFF.md).** "Fixed" means changed in code or docs after the review. Fixed code is covered by `tests/test_review_fixes.py` (15 tests).

| # | Finding (short) | Severity | Triage | What was done |
|---|---|---|---|---|
| 1 | Contract v2 was used for development round 2 and the one-shot held-out run **before owner review**, breaking this project's own Gate 2 | High | **Genuine** | Can't be undone. Stated in [gates.md](gates.md) and [evidence.md](evidence.md). If the owner rejects or changes v2, the held-out set is spent and a new one is needed. |
| 2 | "0 unsafe SQL executed" is true by construction: executed SQL had already passed the same check, and the model never attempted unsafe SQL | Medium | **Genuine** | The tautological re-check was removed from `evaluate.py`. Docs now say the model didn't attempt unsafe SQL, and that the safety evidence is tests 1–4 and F1–F4. |
| 3 | A Python helper or `printf` on a huge string could overrun the 10 s statement budget; the 60 s question budget wasn't enforced per statement | Medium | **Genuine** | `printf`/`format` removed from the allow-list. `title_has`/`norm` inputs capped at 1,000 characters. SQLite string length capped at 10 MB where Python supports it (3.11+, **not** 3.9). Each statement's budget is now capped by the time left for the question. The live CLI timeout (180 s) isn't capped by the question budget (open). |
| 4 | A `'` inside a double-quoted name blinded the text check; "three independent layers" was overstated (read-only mode alone doesn't block `ATTACH`) | Low | **Genuine** | The text check now skips all quoted forms in one pass. Python's "one statement at a time" error now counts as a policy denial. [action-surface-map.md](action-surface-map.md) corrected to two independent layers for reads and writes, plus the first-word rule. **No authorizer bypass was found.** |
| 5 | Model text could forge a system "Check:" line in the gate view | Medium | **Genuine** | Model text is flattened to one line, stripped of markdown emphasis, and introduced as "Model-written…". System lines are labelled as SponsorSQL's. |
| 6 | The gate hash covered only the rendered, truncated view; `A\|B` and `A/B` collided; file approvals are just JSON anyone can write | Low–medium | **Genuine** | The view now includes SHA-256 values of the full answer and the kept evidence rows. Pipes are escaped, not replaced. **Not fixed:** file-mode approvals aren't tied to a run id or a person, and file mode never displays the view. Documented in [gates.md](gates.md). |
| 7 | Crash paths (a decision file `[]`, a missing CLI binary, a missing database) wrote no state | Low | **Genuine** | Unexpected errors now stop as `stopped_error` with state saved. A non-object decision file defers. An `OSError` from the CLI becomes `ModelUnavailable`. |
| 8 | Comparators accepted some wrong answers (extra rows, 40.9, duplicate labels) | Medium | **Genuine** (latent) | Comparators now require one row and one column for single values, whole numbers for counts, and unique labels. **All three runs were re-scored from the saved replies: 4/10, 9/10 and 5/5, unchanged** (`evals/results/*-rescored-after-review.json`). |
| 9 | Keys share the normalization code and definitions with the system, and v2 hands the key's definitions to the model; so 9/10 and 5/5 measure spec-to-SQL translation, not external truth. The BI exclusion (1,013 cases) is debatable. | Medium | **Genuine** | Stated as the main limit in [evidence.md](evidence.md). The BI wording stays an open owner decision. |
| 10 | The held-out set is weak evidence of transfer: the same session wrote the held-out set and v2; held-out questions are slot variants of the development ones | Medium | **Genuine** | v2's header line ("held-out questions were not looked at") is **unverifiable** and shouldn't be relied on. The file is left unedited because its hash is recorded in the results; this note is the correction. |
| 11 | v2's change table (naming D3, D5, D6, D8) went into every round-2 and held-out prompt; v1's baseline was handicapped (it referred to rules it didn't include) | Low–medium | **Genuine** | Stated in [evidence.md](evidence.md): development 9/10 estimates nothing beyond those questions. |
| 12 | The pre-mortem's "prediction" had already been observed in the October draft; C1 re-runs the October query | Medium | **Genuine** | The pre-mortem is kept unedited. The controlled failure is now described as a **replication**: predicted from the October evidence, triggered on purpose, caught by the key. It isn't a new discovery. |
| 13 | Times written inside documents (for example "13:10", "13:15", "13:20") contradict the commit times | Low–medium | **Genuine** | Those in-document times were typed by Claude as estimates and are **wrong**. Only commit order is evidence. Frozen files aren't edited, to keep their hashes; this note is the correction. |
| 14 | Recorded-reply provenance can't be verified from the files; the parent session (which had the keys in context) transcribed the replies; the live adapter ran in the project folder | Medium | **Genuine** | Stated in [evidence.md](evidence.md). The live adapter now runs the CLI from an empty temporary folder. Still not tested live. |
| 15 | Screen gaps ("address" not matched; some prediction phrasings slipped through); no model-side refuse field | Low–medium | **Genuine** | Regex fixed; the reviewer's examples are now refused (tests). **Not fixed:** the reply schema still has no refuse field (that needs a v3 contract). Some false refusals remain (for example "Attorney job titles"), as a conservative choice. |
| 16 | The count check trusts the model's `answer_type` label and compares two model queries | Low | **Genuine** | Documented. The H3 false MISMATCH still appears (open; needs a `value` answer type in a v3 contract). |
| 17 | The view printed the constant workbook hash, not the database's recorded value | Low | **Genuine** | The view now prints the checksum recorded in the database it actually queried. It's still a label, not a hash of the database file (documented). |
| 18 | README/brief claimed "see the number is right"; `load_lca_sqlite.py` was cited but missing; the clean-checkout log is a summary | Low–medium | **Genuine** | Wording changed to "see how the number was produced, and check it". `evals/load_lca_sqlite.py` added. The log is described as a filtered summary in [STRANGER-RUN.md](STRANGER-RUN.md). |

**False positives:** none judged so far. Prediction 2 (recorded replies weaken the "agentic" claim) and prediction 4 (key and agent both built with Claude) were confirmed by findings 14 and 9. Prediction 1 (the regex text check can be fooled) was confirmed by finding 4. Prediction 3 (the count check isn't independent) was confirmed by finding 16.

## 3. Failed cases

- **Development round 1 (v1), 4/10:** D3 (budget stop on a text-column join), D4, D5, D6, D9 (substring title matching, the predicted failure), D8 (untrimmed titles).
- **Development round 2 (v2), 9/10:** D8. Four titles end in a non-breaking space or tabs; the key's Python `strip()` removes them, SQLite `TRIM()` doesn't. A definition gap, not a model mistake.
- **Held-out (v2), 5/5:** no failed answers. One **false alarm**: H3's count check showed "MISMATCH" for a median labelled `count`.
- **Controlled failure:** the October substring query on D5 failed against the key, as predicted; the `title_has` version passed.

Details: [evals/FAILURE-LOG.md](evals/FAILURE-LOG.md).

## 4. Gap Account — what a reviewer of this kind could never reach

The reviewer was an AI reading files and running local commands in the same environment. It could never reach:
- **Whether the recorded replies are genuine model output.** It saw only files written by the session that also held the keys. There are no independent transcripts or run IDs.
- **Real time:** whether "gate before code" and "freeze before proposals" happened in that order, or were only committed in that order. Git dates are author-set.
- **Human facts:**
  - whether the owner reviewed anything
  - how a real person behaves at the gate (reading the view, or pasting a hash)
  - whether the key's definitions match what a student means by "Data Analyst" or "BI Analyst"
- **The world outside the file:** whether the SQLite load matches the DOL's own figures beyond the 40 Boston rows; whether a newer DOL release changes the answers; second worksites that aren't in this file.
- **Live behaviour of the `claude -p` path:** tool use, file access, run-to-run variation.

Only a person (the owner, a TA, a stranger) can close the human items. Only a re-download and an independent recount can close the data items.
