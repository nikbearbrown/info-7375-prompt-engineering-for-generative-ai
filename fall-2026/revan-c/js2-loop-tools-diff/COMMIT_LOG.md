# Commit log

The commit hashes cited in this folder (for example `f3072e5`, `06e9257`) come from the local repository where this project was developed. That history is not copied into the class repository, so it is listed here: every commit, oldest first, with its short hash, UTC date, and full message. Author names and emails are omitted (every commit was made from Revan C.'s machine); a `Co-Authored-By: Claude` line marks a commit in which Claude Code wrote some or all of the content; the message says which parts. The commit that adds this file is not listed in it.

Generated with `git log --reverse` on 2026-11-10.

## `2091127` — 2026-10-31 04:27:33Z

```
Contract v1 (author-written draft) and fictional persona, before any code

CONTRACT.md written by Revan before implementation. Persona and résumé are
fictional (example.com / 555), supplied by the author.

Content by Revan. Claude Code added .gitignore and made the commit.
```

## `021999d` — 2026-10-31 04:40:53Z

```
Contract v2 (author-revised): klaviyo board, five-condition rule, seeded-run plan

Revised by Revan after checking live board data on 2026-10-31: greenhouse
board had 0 Boston/remote postings. Adds seniority and role-type conditions,
explicit skill normalization, authorization/e_verify fields, named tests.

Content by Revan; committed via Claude Code.
```

## `994646d` — 2026-10-31 04:42:30Z

```
Résumé: add target_titles, target_role, years_experience, visa per contract v2

Edited by Revan so the fictional résumé carries every field CONTRACT.md reads.

Content by Revan; committed via Claude Code.
```

## `5cef19a` — 2026-10-31 04:46:21Z

```
Tests from CONTRACT.md v2, written before any implementation

Claude Code wrote these from the contract text; jsagent/ does not exist yet,
so every test currently fails at import. Covers the five named wrong versions
plus the rule's hand-check examples, location/skill edges, and refusals.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `1397a6f` — 2026-10-31 04:51:18Z

```
Implement agent against CONTRACT.md v2; add Claude judge, mutation check, README

jsagent/: allow-listed fetch, résumé schema guard, five-condition rule,
validator, Claude judge (claude-opus-5-5, effort medium), run/CLI.
tests/test_claude_judge.py written after the implementation (fake client).
tools/check_wrong_versions.py confirms each contract wrong version fails its test.
evidence/: pre-implementation Klaviyo snapshot fetched by Claude Code with curl.

28 tests pass. No submitted runs and no Claude API calls yet.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `87f68dd` — 2026-10-31 05:07:15Z

```
Apply author review: per-skill evidence paths, strict scalar types, prompt wording, write-failure handling

Review by Revan (2026-10-31) found: skills resume_field was not a single path;
validator accepted "2" for years_experience although the prompt asks for a number,
and the prompt said "verbatim" while the validator normalizes case and punctuation.

- rule.py: skills resume_field/resume_value/posting_value are parallel lists
- validator.py: scalar citations must match the résumé value's JSON type
- prompts/baseline.txt: say how values are checked (before any API call)
- run.py: run-file or state write failures raise RunError, state untouched
- tests/test_review_fixes.py (written after the code): evidence truth on fixtures
  and all 156 snapshot postings, scalar types, write failure. All 5 fail on 1397a6f.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `a6b6e62` — 2026-10-31 05:15:33Z

```
Labeling rule: AI-assisted first draft, reviewed and revised by Revan

Saved before any experiment posting is selected or labeled and before
any Claude experiment call, so its timestamp precedes the labels.

Committed via Claude Code.
```

## `ba3a9b8` — 2026-10-31 05:19:21Z

```
Prompt revision 1 (author-chosen): one added sentence on preferred qualifications

diff against prompts/baseline.txt is exactly one added line (line 8):
A missing qualification marked "preferred" or "nice to have" alone must not
make the verdict "not_relevant".

Fixed before any baseline or experiment call, so it is a pre-stated change,
not one chosen after seeing development-set results.

Content by Revan; committed via Claude Code.
```

## `0fbaaad` — 2026-10-31 05:24:45Z

```
Add sampling and prompt-experiment tooling; record token usage per Claude call

experiment/: label sheet (no verdicts shown, no overwrite), stratified split with
fixed seed (no re-split), sampling runner (refuses held-out ids, >=4 fresh calls),
experiment runner (invalid/unavailable = fail, Wilson 95% interval; held-out needs
--final, a committed unedited prompt, and a prior dev run of the same prompt).
Every raw response saved with date, model, request id, usage.

tests/test_experiment.py written after the code, fake judge only. 41 tests pass.
No Claude API call has been made.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `ba2a709` — 2026-10-31 05:28:05Z

```
Record selection rule and split seed; create empty label sheet

Selection (Revan's choice): the 20 snapshot postings whose titles contain a
target_titles phrase. Split seed 7375, chosen before labeling. Sampling uses
development postings only. labels.csv has every label column empty.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `721935a` — 2026-10-31 05:28:21Z

```
Add reading aid: the 20 labeling postings' full text, no verdicts

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `37d77e4` — 2026-10-31 05:32:51Z

```
Seeded response for run 1, made by Revan; provenance recorded

Revan ran, in the terminal:
  .venv/bin/python -I -c "import json; d=json.load(open('evidence/klaviyo_2026-10-31_preimplementation_live.json')); d['jobs']=[j for j in d['jobs'] if j['id'] not in (8041054003, 7792539003)]; json.dump(d, open('evidence/klaviyo_2026-10-31_seeded.json','w'))"

Verified: 154 postings, only those two ids removed, rest identical.
meta.total still reads 156 (not used by the agent).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `2edbefa` — 2026-10-31 05:35:16Z

```
Add hand labels for 20 Klaviyo postings
```

## `b1aa320` — 2026-10-31 05:48:57Z

```
Refuse missing Claude credentials before fetching or calling

First attempt at live run 2 (2026-10-31 05:47Z) crashed with an uncaught SDK
TypeError because no API key was visible to the process. The crash came after the
raw response was saved and before any run file or state write, so state stayed at
run 1. The CLI, sampling, and experiment scripts now check credentials first
(CLI exit 5) and fetch or call nothing without them.

The failed attempt's evidence file is kept and recorded in PROVENANCE.md; it is
byte-identical to the pre-implementation snapshot.
Test added: test_cli_refuses_missing_credentials_before_fetching. 42 pass.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `5fc0b68` — 2026-10-31 05:52:18Z

```
Watch runs 1 (seeded baseline) and 2 (live), run by Revan

Run 1, 05:37:48Z: SEEDED baseline from evidence/klaviyo_2026-10-31_seeded.json,
154 postings, 0 new, state saved.
Run 2, 05:51:09Z: LIVE, 156 postings, 2 new (the two hand-removed ids):
  8041054003 rule relevant / Claude relevant
  7792539003 rule not_relevant (role_type) / Claude not_relevant
Both Claude outputs passed the validator; claude-opus-5-5 served; 6,823 input
and 753 output tokens. Live board unchanged since the 04:26Z snapshot (same
sha256), so the change between runs is the seeded removal, not a board change.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `335d280` — 2026-10-31 06:01:28Z

```
Correct one uncertainty note in hand labels (7777369003); no label changed

A consistency check by Claude Code against the labeling rule's objective parts
found that this posting states "Klaviyo supports work authorization and
relocation for this position", while the note said no sponsorship evidence.
Revan accepted the correction. Label stays not_relevant (Senior title, 6+ years).
The check changed no labels; judgment checks 1 and 4 were not reviewed.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `da980a7` — 2026-10-31 06:02:46Z

```
Stratified dev/held-out split, seed 7375 (run once)

dev: 2 relevant, 8 not_relevant; held-out: 1 relevant, 9 not_relevant.
No Claude experiment call has been made yet.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `30e722c` — 2026-10-31 06:09:15Z

```
Sampling and prompt-experiment outputs, run by Revan (2026-10-31 06:03-06:08Z)

60 Claude calls total (claude-opus-5-5, effort medium): 211,266 input and 17,111
output tokens. Every raw response kept.

Sampling (baseline, 5 dev postings x 4): 4 postings 4/4 same verdict matching the
hand label; 7777369003 2 not_relevant + 2 invalid.
Dev: baseline 9/10, revision-1 10/10. Held-out: baseline 10/10, revision-1 9/10.
All 4 invalids are format failures (3x resume_field 'devops_cicd' without the
'skills.' prefix; 1x malformed JSON); none is a verdict disagreement.
All 56 valid outputs match the hand label.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `144b089` — 2026-10-31 06:11:12Z

```
Draft sampling and prompt-experiment reports (Claude Code draft, for Revan to edit)

Drafted from the committed raw files; every number recomputed from them.
Marked as drafts at the top of each file.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `262067e` — 2026-10-31 06:12:44Z

```
Draft action-surface comparison; identical input files for all three surfaces

Surface 3 cites real runs (run 2, commit 5fc0b68) and Claude Code's own record in
this session. Surfaces 1 and 2 are marked not run; Revan runs them in fresh
sessions with the provided input files and validator command.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `bc111c4` — 2026-10-31 06:19:08Z

```
Draft SOURCES.md, FRICTIONAL.md, sign-off and driver's seat; update README status

Facts drawn from the commit history and session record, each traced to a commit.
Reflections, the labeling-pace note, and the signature are left for Revan.
Every test named in the sign-off exists; 42 tests pass.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `607f2f7` — 2026-10-31 18:11:57Z

```
Update cited commit hashes after rewording history; add hash note

Commit messages were reworded before the first push, so every hash changed.
Docs now cite the new hashes; SOURCES.md maps the two prompt commits that the
run summaries record under their earlier hashes. Raw run outputs are unchanged.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `3e76220` — 2026-10-31 18:46:39Z

```
Record action surfaces 1 and 2 (run by Revan on claude.ai, 2026-10-31)

Surface 1 (chat paste): relevant, passed the validator.
Surface 2 (file upload), two runs: both prose, both rejected by the validator.
The first, with memory on, cited two real projects of Revan's that were not in
the input; the committed copy redacts them and the raw reply stays in private/.
The second, after memory was removed, used only the input.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `0a373a2` — 2026-10-31 18:51:02Z

```
README: temperature record, exit code 5, scratch-dir and refusal commands; fix persona pairing

Checked from a fresh clone of 3e76220 with only the README setup commands:
42 tests passed, all wrong versions caught, a --no-claude live run worked,
and a refused slug exited 2.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `e5f5b67` — 2026-10-31 19:01:48Z

```
Revan's review of the documentation: reflections, checks, AI-assistance disclosure

Revan filled the FRICTIONAL reflections and the SOURCES "My check" column,
adopted the three reports with corrections, removed the draft banners, and
disclosed that an AI assistant (not Claude Code) drafted the first labeling
rule and the initial 20 label rows, which Revan reviewed and adopted.

Claude Code then aligned wording with that disclosure ("my reviewed label"),
and updated cited hashes after rewording the labeling-rule commit message.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `e15891d` — 2026-10-31 19:04:38Z

```
State when the 20 postings were read: between 01:35 and 02:02

Revan read all 20 full postings after the label rows were committed (01:35)
and before the split (02:02). No label changed; the only later edit to
labels.csv was one note (335d280).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `d1f9802` — 2026-10-31 19:07:31Z

```
Sign the sign-off

Signed by Revan; committed via Claude Code.
```

## `55d6b1f` — 2026-10-31 19:16:59Z

```
README: point cited commit hashes to COMMIT_LOG.md; ignore the submission zip

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `f3072e5` — 2026-11-10 05:57:21Z

```
Gate for Job-Search Agent 2: exits, budgets, repeat rule, error and permission policy, written before any code
```

## `e7493d7` — 2026-11-10 06:03:39Z

```
JS2 tests from GATE.md, written before any JS2 implementation

Boundary tests B01-B16 (docstrings quote GATE.md's predictions), loop tests
for the four exits, budgets, repeat rule, state and provider shapes (one per
GATE.md wrong version), and tests for an independent check. They fail now:
jsloop and tools/independent_check.py do not exist yet. Written by Claude
Code from Revan's GATE.md (f3072e5); EXTRA cases are marked as not in the gate.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `ac2827a` — 2026-11-10 06:08:28Z

```
Implement JS2 loop, permission policy, independent check, wrong-version checker

jsloop/: policy.py (exact-URL network allow-list; resolved-path, component-wise
write containment; state writes only with --approve-state-write), fetch.py (one
GET, no redirects followed), providers.py (Greenhouse and Lever parsers; empty
list is a failure), loop.py (four exits, budgets checked before acting, action
ledger, state written only after a finished approved run), __main__.py (CLI).
tools/independent_check.py recounts saved raw responses without importing
either agent. tools/check_wrong_versions_js2.py builds 17 mutants.

Tests changed after the implementation existed (all made stricter, none weaker):
- test_state_write_failure_is_error_and_trace_says_so: the first version made the
  state file a directory, so the run failed at preflight and never reached the
  write; it now fails at the write, after all three boards were fetched.
- test_state_bytes_unchanged_after_observation_only_run: also asserts status
  finished and state_updated false.
- the two provider-shape tests now match the shape error, not any BoardInvalid.

Written by Claude Code against Revan's GATE.md (f3072e5).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `6fbefdb` — 2026-11-10 06:11:40Z

```
JS2 documents (drafts for Revan), seeded empty fixture; rename JS1 docs to JS1_*

README.md now describes JS2; JS1's README, SOURCES and FRICTIONAL are kept as
JS1_README.md, JS1_SOURCES.md, JS1_FRICTIONAL.md with a rename note.
BOUNDARY_TESTS.md: GATE.md predictions beside test names and Claude Code's results.
REVIEW_PACKET.md, SIGNOFF.md, SOURCES.md, FRICTIONAL.md are drafts or skeletons;
the parts marked Revan are left blank. fixtures/js2/klaviyo_empty_seeded.json
is a hand-written seeded fixture, with PROVENANCE.md. Clearer wording in one
independent-check message.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `bf53a2c` — 2026-11-10 06:12:21Z

```
README: name step 2's run file exactly for the independent check

In a fresh-clone check, both JS1 demo runs landed in the same second; the
second run's file (_seeded-1.json) sorts before the first (_seeded.json), so
'ls | tail -1' picked the baseline run.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `d7f1508` — 2026-11-10 06:45:10Z

```
JS2 runs, 2026-11-10 06:32-06:34Z: DNS failure, live timeout, finished baseline, deliberate 404, seeded empty board, JS1 finished-wrong demo
```

## `bfbc822` — 2026-11-10 06:45:31Z

```
Review packet: failing test for Lever remote location, written before the patch
```

## `06e9257` — 2026-11-10 06:46:17Z

```
Lever: carry workplaceType remote into location.name (review-packet patch)

parse_lever copied only categories.location, so a Lever posting with
workplaceType "remote" and location "United States" failed CONTRACT.md's
location condition. Remote Lever postings now get
" (Lever workplaceType: remote)" appended to location.name.

Written by Claude Code at Revan's request, after Revan's failing test
(tests/test_js2_remote_review.py, committed in d7f1508). Only jsloop/providers.py
changed; jsagent/rule.py, CONTRACT.md and Revan's test are untouched.
Accept/revise/reject is Revan's decision (REVIEW_PACKET.md).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

## `9ec1695` — 2026-11-10 07:03:16Z

```
Review packet: reproduction, pre-patch test, diff review, decision to accept 06e9257
```

## `c761381` — 2026-11-10 07:15:32Z

```
README: what ran, with independent checks for the normal and seeded-empty runs
```

## `f1f1fd2` — 2026-11-10 07:20:54Z

```
BOUNDARY_TESTS: record my own run of the suite and the mutant check
```

## `679fd5c` — 2026-11-10 07:33:15Z

```
FRICTIONAL: my log for JS2
```

## `52606a2` — 2026-11-10 07:41:22Z

```
SOURCES: what Claude contributed and what I did with it
```

## `9ff48e4` — 2026-11-11 01:32:10Z

```
Sign-off and driver's seat
```

## `66965f2` — 2026-11-11 01:38:09Z

```
Use "Revan C." instead of the full name, for the class GitHub folder

fall-2026/README.md says no full names are stored in the class folders.
Replaced in README, GATE, SIGNOFF, CONTRACT, JS1_README, LABELING_RULE, and the
author line of review_evidence/post_patch_commands.txt (its header says so).
Only the name changed; no decision, result, or signature date changed.
Done by Claude Code at Revan's request.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

