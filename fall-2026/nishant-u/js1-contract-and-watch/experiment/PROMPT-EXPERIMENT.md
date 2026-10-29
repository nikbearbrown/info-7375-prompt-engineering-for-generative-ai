# Prompt experiment: baseline vs revision-1 (draft for Nishant to edit)

Status 2026-10-29: development results, then the freeze (commit `37fd62f`), then the held-out
evaluation, run once. The held-out results are at the end.

## The labeling rule

From `LABELING-RULE.md`, written 2026-10-29, before any posting was chosen for labeling:

> My hand label for a posting is the contract rule R1–R4 applied by me, by hand: I read the title and
> location myself, and I check each of Priya's shipped skills in the posting text with Ctrl+F. I label
> it before seeing any rule or Claude verdict.

All 20 labels are in `labeling/labels.csv`, committed before any Claude judge call. The rule judge
agrees with them on the label for 20/20. On the failed check it agrees for 14/20 (`rule_vs_hand.md`).

## The split and its seal

- 20 postings from the baseline response `runs/2026-10-29-1/raw.json` (sha256 `3c10b536…c2b7`), drawn
  by `make_split.py` with seed **20261029**: 10 development, 10 held-out (`SPLIT.md`).
- `heldout_ids.json` sha256 `1cc26d9d144abe6ecfd2862f17fa39ceec331d6cb3d349ec3bb486aec163b5cc`. The
  experiment scripts refuse a held-out file with any other hash, and refuse to send a held-out id to
  Claude.
- Exposure, recorded in `SPLIT.md`: the held-out titles and locations were shared with Claude in
  claude.ai while Nishant asked how the rule reads. No prompt was written or changed from that
  conversation. No held-out posting has been sent to the `claude -p` judge.

## The prompts

| Prompt | File | sha256 (as committed, LF line endings) | Schema in `agent/validator.py` |
|---|---|---|---|
| Baseline | `prompts/baseline.md` | `5bd931e7b14669884357b6bb20b960afccea86cefe93cd8d3a3ad70b883997a1` | `baseline` (unchanged) |
| Revision 1 | `prompts/revision-1.md` | `16ecb4366aaf1d07f52f33ac5f9bb0bc9e442616954bdab6795e96968c453206` | `revision-1` |

The whole difference is one added line in the Output section:

```diff
 - "verdict": "relevant" or "not_relevant"
+- "failed_check": apply R1, R2, R3, R4 in order and give the first check that fails: "R1", "R2", "R3" or "R4"; null when the verdict is "relevant"
 - "citations": a non-empty list of objects, each with exactly the keys "resume_field", "posting_field" and "quote":
```

The `revision-1` schema is the baseline schema plus a required `failed_check`. It must be one of R1–R4
with `not_relevant`, and `null` with `relevant`. This was declared in the `CONTRACT.md` amendment
before the revision ran.

## The one change and why

The baseline passed 10/10 on dev, but its schema had no field for *which* check failed. A not_relevant
verdict could be right for the wrong reason without any measure noticing, and Claude's verdicts couldn't
be compared with the rule judge's record of the first failing check. Revision 1 asks for that check,
in R1→R4 order, so the reason becomes checkable. Nothing else in the prompt changed.

## Dev results (10 postings, 1 fresh `claude -p` call each, `claude-opus-5-5`, CLI 2.1.312)

| Measure (declared before the revision run) | Baseline (20:38–20:39 UTC) | Revision 1 (21:05–21:06 UTC) |
|---|---|---|
| Valid | 10/10 | 10/10 |
| All citations supported (reported apart, not part of pass) | 10/10 | 10/10 |
| **Pass** = valid AND verdict equals my hand label | **10/10** | **10/10** |
| **failed_check agreement with the rule judge** | not measurable (no such field) | **10/10** |

Per-call tables, with every date and session_id, are in `BASELINE-DEV.md` (baseline) and below
(revision 1). Raw replies are in `runs/baseline-dev/` and `runs/revision1-dev/`.

| posting_id | my label | Claude verdict | Claude failed_check | rule failed_check | my failed check* | session_id |
|---|---|---|---|---|---|---|
| 8612874002 | not_relevant | not_relevant | R2 | R2 | R1 | `80032a25-e3a9-4392-b6f1-e7b95bb07bcf` |
| 8618151002 | not_relevant | not_relevant | R3 | R3 | R2 | `d2cf8adf-1915-425f-8201-518203292309` |
| 8660923002 | relevant | relevant | null | null | - | `bc041b4b-0429-4947-a9f5-344f187c1ff6` |
| 8818059002 | not_relevant | not_relevant | R1 | R1 | R1 | `a2112882-2ffa-45ca-92d2-8713421ab284` |
| 8820806002 | not_relevant | not_relevant | R1 | R1 | R1 | `1535d3a0-17e3-4a24-b9d4-f65061d433ba` |
| 8821336002 | not_relevant | not_relevant | R1 | R1 | R2 | `d438c20d-34b4-48e7-9cca-7e5dc593b3df` |
| 8832899002 | not_relevant | not_relevant | R4 | R4 | R4 | `ebc01209-9248-4ce2-bcaf-87e9922eb03d` |
| 8870975002 | not_relevant | not_relevant | R2 | R2 | R1 | `1c74730b-6be5-41af-9bbd-fbb5221b4e2b` |
| 8872721002 | not_relevant | not_relevant | R1 | R1 | R1 | `6e909ff7-c7f1-46f1-9708-d3dbc87bd6ad` |
| 8899853002 | not_relevant | not_relevant | R1 | R1 | R1 | `e856dc6c-cb0d-49b2-9ec4-4095ad0b7c5d` |

\* My failed check is shown for reference only; it wasn't declared as a measure. Claude matched it on
6/10. The 4 differences are the same 4 dev postings where my failed check differs from the rule
judge's (`rule_vs_hand.md`).

## What this does and doesn't show

- **Same pass rate.** On the declared pass rule, the baseline and revision 1 can't be told apart on dev
  (10/10 each). The revision added a check the baseline couldn't be given, and it met that check
  (10/10 with the rule judge).
- **Citations are no better.** Revision 1 still cites titles under unrelated résumé fields, such as
  `skills.languages` and `experience.0.title`. For the R4 failure (8832899002) it still cites
  present text rather than the absence of skills. The change wasn't aimed at citations, and they
  didn't improve.
- **Small and easy.** The dev set is 10 postings, one call each, with only 1 relevant by my labels.
  Agreement here is not a measured rate, and repeatability isn't correctness (`SAMPLING-REPORT.md`).
- **Dev only.** This section covers development results, written before the freeze. The held-out
  results are below.

2026-10-29: revision-1 frozen before the held-out evaluation. prompts/baseline.md sha256 5bd931e7b14669884357b6bb20b960afccea86cefe93cd8d3a3ad70b883997a1, prompts/revision-1.md sha256 16ecb4366aaf1d07f52f33ac5f9bb0bc9e442616954bdab6795e96968c453206. No further prompt changes.

## Held-out evaluation (run once, 2026-10-29)

- **Run by:** `python3 experiment/claude_dev.py heldout`, after the freeze commit
  `37fd62f36a1edf3042570bf6c21894976c959f61`. Before any call it checked that the commit is in
  HEAD's history, that both prompts match the frozen hashes, and that `heldout_ids.json` matches its
  sealed sha256 `1cc26d9d…63b5cc`. It claims both output folders before the first call and refuses to
  run again. A second invocation printed: `refused: experiment/runs/baseline-heldout/ exists; the
  held-out evaluation runs once only`.
- **Calls:** 20 fresh `claude -p` calls on my Claude Code login (CLI 2.1.312, `claude-opus-5-5`), 1 per
  posting per prompt. Baseline with the baseline schema (21:12–21:13 UTC), revision 1 with the revision-1
  schema (21:13–21:14 UTC). Raw replies are in `runs/baseline-heldout/` and `runs/revision1-heldout/`.
- **Class balance:** I labeled **2 of the 10** held-out postings relevant (and 8 not_relevant).

| Measure | Baseline | Revision 1 |
|---|---|---|
| Valid | 10/10 | 10/10 |
| All citations supported (reported apart, not part of pass) | 10/10 | 10/10 |
| **Pass** = valid AND verdict equals my hand label | **10/10** | **10/10** |
| 95% Clopper-Pearson interval for the pass rate | 69.2% to 100.0% | 69.2% to 100.0% |
| **failed_check agreement with the rule judge** | not measurable (no such field) | **10/10** |

**Failures:** none. Every call was valid, every verdict equalled my label, and every revision-1 failed_check equalled the rule judge's.

### Baseline, every call
| posting_id | date (UTC) | session_id | model | my label | Claude verdict | valid? | citations supported | pass |
|---|---|---|---|---|---|---|---|---|
| 8580854002 | 2026-10-29T21:12:16+00:00 | `6bf01159-9781-4d89-a8c7-00aab384e544` | claude-opus-5-5 | not_relevant | not_relevant | valid | 2/2 | yes |
| 8609131002 | 2026-10-29T21:12:22+00:00 | `9394b508-e82b-4b62-9bff-d017bda0c055` | claude-opus-5-5 | not_relevant | not_relevant | valid | 2/2 | yes |
| 8754821002 | 2026-10-29T21:12:29+00:00 | `b6492edc-1558-41b0-a41e-b755516aaded` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8801507002 | 2026-10-29T21:12:34+00:00 | `a09509d0-8eff-4654-852e-982df3bc90ab` | claude-opus-5-5 | not_relevant | not_relevant | valid | 3/3 | yes |
| 8804205002 | 2026-10-29T21:12:41+00:00 | `eb2ab137-378b-414c-a47c-b28a8f5c3c0e` | claude-opus-5-5 | relevant | relevant | valid | 4/4 | yes |
| 8806617002 | 2026-10-29T21:12:47+00:00 | `b6cebdd5-43de-4780-a6a9-3ada0a9fd42d` | claude-opus-5-5 | relevant | relevant | valid | 5/5 | yes |
| 8843624002 | 2026-10-29T21:12:55+00:00 | `d6e2047b-db6a-49c4-bb20-aaf8a4d163bd` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8845103002 | 2026-10-29T21:13:01+00:00 | `3af6f73e-4322-4fc6-ad47-3c1e99746568` | claude-opus-5-5 | not_relevant | not_relevant | valid | 5/5 | yes |
| 8864986002 | 2026-10-29T21:13:09+00:00 | `31990d1e-dbec-4580-8f3b-156de4f0dfce` | claude-opus-5-5 | not_relevant | not_relevant | valid | 2/2 | yes |
| 8906280002 | 2026-10-29T21:13:15+00:00 | `9a13811c-2ccd-4427-b561-1f62e913606c` | claude-opus-5-5 | not_relevant | not_relevant | valid | 2/2 | yes |

**Held-out pass rate: 10/10** (pass = valid AND verdict equals my label); 95% Clopper-Pearson interval 69.2% to 100.0%.
Valid: 10/10. All citations supported: 10/10.

No unsupported citations.

### Revision 1, every call
| posting_id | date (UTC) | session_id | model | my label | Claude verdict | valid? | citations supported | pass |
|---|---|---|---|---|---|---|---|---|
| 8580854002 | 2026-10-29T21:13:21+00:00 | `e778b9d9-8d92-4f72-9349-df98b2f24fba` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8609131002 | 2026-10-29T21:13:26+00:00 | `a61df78c-0f20-4f46-919b-00a52c0910f2` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8754821002 | 2026-10-29T21:13:31+00:00 | `0be87d8c-0a05-4558-896e-7f5a23644133` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8801507002 | 2026-10-29T21:13:36+00:00 | `5360e758-a624-47f2-b8a0-551528720be4` | claude-opus-5-5 | not_relevant | not_relevant | valid | 4/4 | yes |
| 8804205002 | 2026-10-29T21:13:44+00:00 | `c93a579d-c10e-4815-80b5-c21e3591b595` | claude-opus-5-5 | relevant | relevant | valid | 4/4 | yes |
| 8806617002 | 2026-10-29T21:13:51+00:00 | `d5769752-ab34-4e4c-a708-d851e8e290de` | claude-opus-5-5 | relevant | relevant | valid | 6/6 | yes |
| 8843624002 | 2026-10-29T21:13:58+00:00 | `24abecca-5b71-4aa8-9d7e-348e8f28f199` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8845103002 | 2026-10-29T21:14:04+00:00 | `06e0dad2-5fb0-42bf-bcef-67acd66c687c` | claude-opus-5-5 | not_relevant | not_relevant | valid | 3/3 | yes |
| 8864986002 | 2026-10-29T21:14:12+00:00 | `16673089-0169-432d-8908-c3983537ea86` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |
| 8906280002 | 2026-10-29T21:14:18+00:00 | `bed7cf93-d0f7-4017-8583-90a41f3b8cbe` | claude-opus-5-5 | not_relevant | not_relevant | valid | 1/1 | yes |

**Held-out pass rate: 10/10** (pass = valid AND verdict equals my label); 95% Clopper-Pearson interval 69.2% to 100.0%.
Valid: 10/10. All citations supported: 10/10.

### failed_check vs the rule judge (declared second measure)

**failed_check agreement with the rule judge: 10/10** (counted only when valid).

| posting_id | Claude failed_check | rule failed_check | agrees | my failed check (not a declared measure) |
|---|---|---|---|---|
| 8580854002 | R1 | R1 | yes | R1 |
| 8609131002 | R1 | R1 | yes | R2 |
| 8754821002 | R1 | R1 | yes | R1 |
| 8801507002 | R4 | R4 | yes | R4 |
| 8804205002 | null | null | yes | - |
| 8806617002 | null | null | yes | - |
| 8843624002 | R2 | R2 | yes | R1 |
| 8845103002 | R4 | R4 | yes | R4 |
| 8864986002 | R1 | R1 | yes | R1 |
| 8906280002 | R1 | R1 | yes | R1 |

No unsupported citations.

My failed check differs from Claude's and the rule judge's on 8609131002 and 8843624002. These are the
2 held-out postings where my failed check differs from the rule judge's (`rule_vs_hand.md`). It wasn't
a declared measure.

## Limits

- **10 cases is tiny.** Both pass rates are 10/10. The exact 95% Clopper-Pearson interval for 10/10 is
  69.2% to 100.0%: the result is consistent with a true pass rate as low as about 69%. One failure (9/10)
  would have given 55.5% to 99.7%. The two prompts' intervals are the same.
- **Class balance.** Only 2 of the 10 held-out postings (and 1 of the 10 dev postings, 3 of all 20)
  are relevant by my labels. Each prompt's relevant path was tested 2 times on held-out. A prompt
  that answered not_relevant to everything would have passed 8/10.
- **The pass rule can't separate the prompts.** Both scored 10/10 on dev and on held-out, so the declared pass
  rule shows no difference between them. Revision 1's only measurable gain is the second measure,
  failed_check agreement with the rule judge (10/10). The baseline couldn't be scored on it because its
  schema has no such field.
- **Exposure.** As recorded in `SPLIT.md`, the held-out titles and locations, but not their posting
  text or my labels, were shared with Claude in claude.ai while I asked how the rule reads. No prompt
  was written or changed from that conversation, and no held-out posting was sent to the `claude -p`
  judge before this run. Still, the held-out set is not untouched in the strictest sense.
- **One model, one day, one board.** Every call was `claude-opus-5-5` through Claude Code CLI 2.1.312 on
  2026-10-29, against one snapshot of Faire's Greenhouse board, for one fictional persona. None of this
  says how another model, a later date, another board or another résumé would score.
- **One call per posting.** The held-out run sampled each posting once. The repeatability evidence is
  from 5 dev postings only (`SAMPLING-REPORT.md`).
