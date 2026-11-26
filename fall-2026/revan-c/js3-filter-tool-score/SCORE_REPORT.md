# What moves the score — JS3 (Chapter 9)

**Status: measured conditions, November 25, 2026 ET.** The origin table comes from the code and FILTER.md. I confirmed the 47 audit verdicts. The three deterministic filter conditions and three Claude prompt/context conditions ran on development and then once each on held-out labels.

## Where every number came from

No number in this scorer was fitted on labels. Nothing here was trained.

| Number or object | Value | File | Origin |
|---|---|---|---|
| Role weight | 3 for `backend engineer` / `platform engineer`, 2 for the other target titles, else 0 | `jsfilter/filter.py` `ROLE_WEIGHT` | hand-set, FILTER.md v1 |
| Target title phrases | 5 phrases | `resumes/aarav-patel.json` `target_titles` | inherited (JS1 persona) |
| Seniority words | 7 words | `SENIORITY_WORDS` | inherited (JS1 CONTRACT.md condition 4) |
| Role-type words | 5 words | `ROLE_TYPE_WORDS` | inherited (JS1 CONTRACT.md condition 5) |
| Topic phrases | 10 phrases | `TOPIC_PHRASES` | hand-set, FILTER.md v1 R5 |
| Topic cap | 2 | `TOPIC_CAP` | hand-set, FILTER.md v1 |
| Minimum skills | 2 | `MIN_SKILLS` | inherited (JS1 CONTRACT.md condition 3) |
| Skill cap | 3 | `SKILL_CAP` | hand-set, FILTER.md v1 |
| Threshold | 6 of 8 | `THRESHOLD` | hand-set, FILTER.md v1 |
| Closest-call band | total 5 with all rules passing, or total ≥ 6 with one rule failed | `closest_calls` | hand-set, FILTER.md v1 |
| Reject sample size | 30 | `tools/js3_filter_run.py` | assignment minimum |
| Split | 50 / 25 / 25 within kept and rejected | `split()` | hand-set, FILTER.md v1 section 6 |
| Seeds | `js3-reject-audit-2026-11-25`, `js3-label-split-2026-11-25`, `js3-sheet-order-2026-11-25` | `tools/js3_filter_run.py` | split seed: FILTER.md; the other two chosen by Claude Code and committed before any label |
| Claude prompt | `prompts/baseline.txt`, `prompts/revision-1.txt` | `prompts/` | inherited (JS1; revision 1 was author-chosen there) |
| Claude model, effort | `claude-opus-5-5`, `medium`; temperature not sent | `jsagent/claude_judge.py` | inherited (JS1) |

## One change at a time

Each condition changes exactly one object from its baseline. Run on dev first; then once on held-out with `--final` (the script refuses a second held-out run).

| Condition | Object | Compared with | What changed | Why this change |
|---|---|---|---|---|
| `filter_v1` | — | — | FILTER.md v1 as committed | baseline |
| `setting_threshold_5` | setting | `filter_v1` | threshold 6 → 5 | the only below-threshold posting is Full Stack SWE – People Systems (total 5) |
| `filter_no_platform` | filter rule value | `filter_v1` | R5 without `platform`, applied in memory; no v2 file was saved | `platform` matched in 106 of 215 descriptions, including product and career-growth uses unrelated to platform engineering |
| `claude_prompt_baseline` | prompt (Claude baseline) | — | JS1 baseline prompt, full posting | Claude baseline |
| `claude_prompt_revision1` | prompt | `claude_prompt_baseline` | JS1 revision-1 prompt | prompt object only |
| `claude_context_excerpts` | context | `claude_prompt_revision1` | content = only the filter's quoted excerpts (what `score_posting` returns) | context object only |
| tool list | tools | — | **not run** | see below |

Held-out size: 11 postings (1 kept, 10 rejected). With 11, one disagreement moves agreement by 9 points, so no difference here is evidence of a general improvement.

### Results

| Condition | Development agreement (n=11) | Held-out agreement (n=11) | Change on all 215 posting fates |
|---|---:|---:|---|
| `filter_v1` | 10/11 | 11/11 | Baseline: 4 kept, 1 below threshold, 210 hard-rule rejects. |
| `setting_threshold_5` | 10/11 | 11/11 | One change: A31 moves from below threshold to kept. Its confirmed verdict is `not_relevant`. |
| `filter_no_platform` | 10/11 | 11/11 | No fates change; 78 numerical scores change. |
| `claude_prompt_baseline` | 11/11 | 11/11 | Claude judged all 11 dev postings not relevant; on held-out it judged one relevant and ten not relevant. |
| `claude_prompt_revision1` | 11/11 | 11/11 | Same verdicts as the Claude baseline on both sets; no measured agreement gain. |
| `claude_context_excerpts` | 10/11 | 11/11 | One dev false positive (A41); held-out verdicts matched the full-posting condition. |

The development set has **zero** relevant postings by the confirmed labels. The deterministic filter's one disagreement is a false positive (A41, a 5+ year C# backend role). The Claude baseline and revision correctly rejected A41 with full posting text, while the excerpt-only condition called it relevant. Its 1,282-character excerpt omitted the posting's 5+ years of C# requirement and no-sponsorship statement. The held-out set has **one** relevant posting and ten not relevant postings; all six conditions agree with those 11 labels. Each Claude run saved 11 request IDs, served model `claude-opus-5-5`, and reported zero invalid or unavailable responses. The six Claude summaries are under `runs/js3/experiments/`, with names ending in `_{dev|held_out}_claude_*`.

The Wilson interval reported for 11/11 agreement is approximately 74.1%–100% under the script's sampling calculation. These small, deliberately sampled sets do not establish population performance. Each held-out condition was run once after its development run; no later rule is being selected from those results.

The 30 randomly sampled rejects had 0 disagreements with the confirmed verdicts. All 15 closest calls had 0 disagreements. Every kept posting was reviewed: A07 and A12 were judged relevant; A38 and A41 were judged not relevant. The full record and the false-friend contexts are in `REJECT_AUDIT.md` and `runs/js3/experiments/audit_report.json`.

**Decision after measurement:** Keep threshold 6 and retain `platform` in v1. Removing `platform` did not change a single keep/reject fate, despite changing 78 scores. Lowering the threshold would promote A31, which the confirmed review rejected. The prompt revision did not improve agreement over the Claude baseline on these labels. Keep the full posting as Claude's context for this task: the shorter excerpts caused one false positive on development and no gain on held-out. A possible experience-requirement rule was noticed from A38/A41 but was not part of this predeclared comparison; it is not presented as tested on held-out labels.

## Persistence is not proof of training

The baseline filter file and threshold are saved in code, so their behavior persists across runs. The two measured variants temporarily override a setting or topic list inside the evaluation process. The Claude conditions changed a prompt file or the posting text sent to the API; the resulting verdicts were recorded in the per-posting files. None of these mechanisms changes model parameters. Persistence of a file, prompt, or context across sessions would not prove that a model was trained.

## One predictive claim this supports, one intervention claim it does not

- **Predictive, within these labels:** Filter v1 agreed with all 11 held-out verdicts in the saved 2026-11-10 snapshot; one was relevant and ten were not. This describes a small, preselected evaluation set, not generalization to future postings.
- **Not established:** These observations do not show that acting on a kept posting leads to an interview, offer, or better use of my time. The prompt revision did not improve agreement on these sets; excerpt-only context lost one development verdict. No tool-list change was measured, and these runs cannot establish whether another prompt or context would improve future answers.
