# Prompt experiment: baseline vs revision-1 (draft for Nishant to edit)

Status 2026-10-29: development results only. **The held-out evaluation hasn't been run yet.** The
revision is to be frozen by Nishant before it runs.

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
- **Not evaluated on held-out.** These are development results. The held-out comparison hasn't been
  run yet. It should run only after Nishant freezes `prompts/revision-1.md`.

2026-10-29: revision-1 frozen before the held-out evaluation. prompts/baseline.md sha256 5bd931e7b14669884357b6bb20b960afccea86cefe93cd8d3a3ad70b883997a1, prompts/revision-1.md sha256 16ecb4366aaf1d07f52f33ac5f9bb0bc9e442616954bdab6795e96968c453206. No further prompt changes.
