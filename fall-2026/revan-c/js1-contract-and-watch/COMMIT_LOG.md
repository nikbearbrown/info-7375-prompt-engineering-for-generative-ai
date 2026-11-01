# Commit log

Generated with `git log --reverse` from the project repository at commit `55d6b1f`, the state copied into this folder.
The project repository was kept locally; this file lets every commit hash cited in the documents be traced.

Each entry: short hash, full hash, author date, author, and the full commit message.

---

### `2091127`

full: `2091127f66c91fe459e97ceadfd35391c08fadf4`  
author date: 2026-10-31T00:27:33-04:00  
author: Revan Chonnad

```
Contract v1 (author-written draft) and fictional persona, before any code

CONTRACT.md written by Revan before implementation. Persona and résumé are
fictional (example.com / 555), supplied by the author.

Content by Revan. Claude Code added .gitignore and made the commit.
```

---

### `021999d`

full: `021999dd74a9203435a11a4d66a6680875d88d52`  
author date: 2026-10-31T00:40:53-04:00  
author: Revan Chonnad

```
Contract v2 (author-revised): klaviyo board, five-condition rule, seeded-run plan

Revised by Revan after checking live board data on 2026-10-31: greenhouse
board had 0 Boston/remote postings. Adds seniority and role-type conditions,
explicit skill normalization, authorization/e_verify fields, named tests.

Content by Revan; committed via Claude Code.
```

---

### `994646d`

full: `994646d6d1b2c3b0cb1bdaa2546542d7561e522e`  
author date: 2026-10-31T00:42:30-04:00  
author: Revan Chonnad

```
Résumé: add target_titles, target_role, years_experience, visa per contract v2

Edited by Revan so the fictional résumé carries every field CONTRACT.md reads.

Content by Revan; committed via Claude Code.
```

---

### `5cef19a`

full: `5cef19a69e78f27ce72bddd04d4f64865750762f`  
author date: 2026-10-31T00:46:21-04:00  
author: Revan Chonnad

```
Tests from CONTRACT.md v2, written before any implementation

Claude Code wrote these from the contract text; jsagent/ does not exist yet,
so every test currently fails at import. Covers the five named wrong versions
plus the rule's hand-check examples, location/skill edges, and refusals.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

---

### `1397a6f`

full: `1397a6ffb152b07175a7c474f672448aaf749b43`  
author date: 2026-10-31T00:51:18-04:00  
author: Revan Chonnad

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

---

### `87f68dd`

full: `87f68dd9edf466a7f8ef938bb0549ac7f8cd8299`  
author date: 2026-10-31T01:07:15-04:00  
author: Revan Chonnad

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

---

### `a6b6e62`

full: `a6b6e62ce77b89f67e393b81620d7c1d986672ca`  
author date: 2026-10-31T01:15:33-04:00  
author: Revan Chonnad

```
Labeling rule: AI-assisted first draft, reviewed and revised by Revan

Saved before any experiment posting is selected or labeled and before
any Claude experiment call, so its timestamp precedes the labels.

Committed via Claude Code.
```

---

### `ba3a9b8`

full: `ba3a9b80ee207f7d4a343df491efd19339803ffc`  
author date: 2026-10-31T01:19:21-04:00  
author: Revan Chonnad

```
Prompt revision 1 (author-chosen): one added sentence on preferred qualifications

diff against prompts/baseline.txt is exactly one added line (line 8):
A missing qualification marked "preferred" or "nice to have" alone must not
make the verdict "not_relevant".

Fixed before any baseline or experiment call, so it is a pre-stated change,
not one chosen after seeing development-set results.

Content by Revan; committed via Claude Code.
```

---

### `0fbaaad`

full: `0fbaaadfe310c23a90352c9a826c600dd7f37437`  
author date: 2026-10-31T01:24:45-04:00  
author: Revan Chonnad

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

---

### `ba2a709`

full: `ba2a709a5a3553960a02b83d1810d37f362e80b0`  
author date: 2026-10-31T01:28:05-04:00  
author: Revan Chonnad

```
Record selection rule and split seed; create empty label sheet

Selection (Revan's choice): the 20 snapshot postings whose titles contain a
target_titles phrase. Split seed 7375, chosen before labeling. Sampling uses
development postings only. labels.csv has every label column empty.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

---

### `721935a`

full: `721935a23a23e7c17c9f70ffe1ac03d1b2cbc57f`  
author date: 2026-10-31T01:28:21-04:00  
author: Revan Chonnad

```
Add reading aid: the 20 labeling postings' full text, no verdicts

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

---

### `37d77e4`

full: `37d77e44ed9ede4962381af274e251f533f54b77`  
author date: 2026-10-31T01:32:51-04:00  
author: Revan Chonnad

```
Seeded response for run 1, made by Revan; provenance recorded

Revan ran, in the terminal:
  .venv/bin/python -I -c "import json; d=json.load(open('evidence/klaviyo_2026-10-31_preimplementation_live.json')); d['jobs']=[j for j in d['jobs'] if j['id'] not in (8041054003, 7792539003)]; json.dump(d, open('evidence/klaviyo_2026-10-31_seeded.json','w'))"

Verified: 154 postings, only those two ids removed, rest identical.
meta.total still reads 156 (not used by the agent).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

---

### `2edbefa`

full: `2edbefaf5d1a81f509a03ed4113ebce062f795f0`  
author date: 2026-10-31T01:35:16-04:00  
author: Revan Chonnad

```
Add hand labels for 20 Klaviyo postings
```

---

### `b1aa320`

full: `b1aa3206121c4ff59d67914d5bf28866f4f441a3`  
author date: 2026-10-31T01:48:57-04:00  
author: Revan Chonnad

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

---

### `5fc0b68`

full: `5fc0b682b4af169a7e7f02816e0db3ac95042d24`  
author date: 2026-10-31T01:52:18-04:00  
author: Revan Chonnad

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

---

### `335d280`

full: `335d2801dfa3d9fcaea22278872e0ae422a7275e`  
author date: 2026-10-31T02:01:28-04:00  
author: Revan Chonnad

```
Correct one uncertainty note in hand labels (7777369003); no label changed

A consistency check by Claude Code against the labeling rule's objective parts
found that this posting states "Klaviyo supports work authorization and
relocation for this position", while the note said no sponsorship evidence.
Revan accepted the correction. Label stays not_relevant (Senior title, 6+ years).
The check changed no labels; judgment checks 1 and 4 were not reviewed.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

---

### `da980a7`

full: `da980a78c6b490e004aaaabd02a793b92f4a39ac`  
author date: 2026-10-31T02:02:46-04:00  
author: Revan Chonnad

```
Stratified dev/held-out split, seed 7375 (run once)

dev: 2 relevant, 8 not_relevant; held-out: 1 relevant, 9 not_relevant.
No Claude experiment call has been made yet.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

---

### `30e722c`

full: `30e722cb2a070d0d444ab8472bca463ddefe0b34`  
author date: 2026-10-31T02:09:15-04:00  
author: Revan Chonnad

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

---

### `144b089`

full: `144b0895891562fc5b44b13a82a4f3da1943ccea`  
author date: 2026-10-31T02:11:12-04:00  
author: Revan Chonnad

```
Draft sampling and prompt-experiment reports (Claude Code draft, for Revan to edit)

Drafted from the committed raw files; every number recomputed from them.
Marked as drafts at the top of each file.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

---

### `262067e`

full: `262067ebbf0764c95aac6ff4919bf57c613630ce`  
author date: 2026-10-31T02:12:44-04:00  
author: Revan Chonnad

```
Draft action-surface comparison; identical input files for all three surfaces

Surface 3 cites real runs (run 2, commit 5fc0b68) and Claude Code's own record in
this session. Surfaces 1 and 2 are marked not run; Revan runs them in fresh
sessions with the provided input files and validator command.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

---

### `bc111c4`

full: `bc111c471a1aa3eff79dc1c3e95929d5f80bd8ab`  
author date: 2026-10-31T02:19:08-04:00  
author: Revan Chonnad

```
Draft SOURCES.md, FRICTIONAL.md, sign-off and driver's seat; update README status

Facts drawn from the commit history and session record, each traced to a commit.
Reflections, the labeling-pace note, and the signature are left for Revan.
Every test named in the sign-off exists; 42 tests pass.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

---

### `607f2f7`

full: `607f2f7df247c70f6e676d6c750f582494abefab`  
author date: 2026-10-31T14:11:57-04:00  
author: Revan Chonnad

```
Update cited commit hashes after rewording history; add hash note

Commit messages were reworded before the first push, so every hash changed.
Docs now cite the new hashes; SOURCES.md maps the two prompt commits that the
run summaries record under their earlier hashes. Raw run outputs are unchanged.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

---

### `3e76220`

full: `3e76220d564226ac9957053ed39defa935e4961a`  
author date: 2026-10-31T14:46:39-04:00  
author: Revan Chonnad

```
Record action surfaces 1 and 2 (run by Revan on claude.ai, 2026-10-31)

Surface 1 (chat paste): relevant, passed the validator.
Surface 2 (file upload), two runs: both prose, both rejected by the validator.
The first, with memory on, cited two real projects of Revan's that were not in
the input; the committed copy redacts them and the raw reply stays in private/.
The second, after memory was removed, used only the input.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

---

### `0a373a2`

full: `0a373a27bae9e7ee214faea06f6d6d37b7230c59`  
author date: 2026-10-31T14:51:02-04:00  
author: Revan Chonnad

```
README: temperature record, exit code 5, scratch-dir and refusal commands; fix persona pairing

Checked from a fresh clone of 3e76220 with only the README setup commands:
42 tests passed, all wrong versions caught, a --no-claude live run worked,
and a refused slug exited 2.

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

---

### `e5f5b67`

full: `e5f5b67776259187938e7914388753be9aa11020`  
author date: 2026-10-31T15:01:48-04:00  
author: Revan Chonnad

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

---

### `e15891d`

full: `e15891db4f4b3cb6c6e64f70287bbf41421bf5a2`  
author date: 2026-10-31T15:04:38-04:00  
author: Revan Chonnad

```
State when the 20 postings were read: between 01:35 and 02:02

Revan read all 20 full postings after the label rows were committed (01:35)
and before the split (02:02). No label changed; the only later edit to
labels.csv was one note (335d280).

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```

---

### `d1f9802`

full: `d1f98024825946fb7efb26435cb8b65a1ccc23f9`  
author date: 2026-10-31T15:07:31-04:00  
author: Revan Chonnad

```
Sign the sign-off

Signed by Revan; committed via Claude Code.
```

---

### `55d6b1f`

full: `55d6b1f220d980ddd6ba41236b94efc8a7d973b8`  
author date: 2026-10-31T15:16:59-04:00  
author: Revan Chonnad

```
README: point cited commit hashes to COMMIT_LOG.md; ignore the submission zip

Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>
```
