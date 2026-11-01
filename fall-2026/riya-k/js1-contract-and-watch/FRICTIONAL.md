# FRICTIONAL — Job-Search Agent 1

Riya Kapadnis. All entries are from one working session on 2026-10-31 (the due date), written the same evening.
Claude Code drafted the wording, except the section marked [Riya, own words]. I chose which events to record and what I took from them.

## Commits

| Commit | What |
|---|---|
| ac26e69 | CONTRACT.md only, before any code |
| 3f09459 | Watcher, judges, validator, tests; live baseline and seeded two-day run |
| c665200 | My 20 hand labels and contract amendment 1, before any Claude call on those postings |
| 105f2ba | Sampling, prompt experiment, action-surface runs |
| 416b6b3 | Reports, live run 2 |
| 2f8f6d0 | Audit fixes: Out fields, amendment 2, seeded re-run |
| 6b8de55 | My own test run recorded in the sign-off |
| 60e69a8 | Classmate-comparison fixes (mutation check, action-surface re-run, provenance) |
| df9032f | Hand check, my own words, keep-v1 decision, signed sign-off |
| (last) | Commit hashes updated after rebasing onto classmates' pushes. Its hash is in Canvas, since a commit can't contain its own hash |

---

### 2026-10-31 — Writing the contract before any code

- **I tried / expected:** it was the due date and I wanted this done fast. The brief requires the contract to be written first
  and to be mine, so I asked Claude to ask me questions, and I answered them. Claude filled in the file from my answers.
- **What happened:** I picked AI/LLM, Data Engineer and Data Scientist title words but left out ML. Claude pointed out that Arya's
  stated target is "LLM-platform and ML-infrastructure roles", so leaving ML out would miss her best-fit jobs. I added it.
  Claude also flagged that "Databricks" appears in every Databricks posting, so I chose not to count it as a skill.
- **What Claude contributed:** questions and options; it formatted my answers into CONTRACT.md.
- **Evidence:** commit ac26e69 contains only CONTRACT.md.

### 2026-10-31 — The Unity Catalog trap (my rule had a free match I didn't see)

- **I expected:** with "Databricks" excluded, the 2-skill minimum would mean real overlap.
- **What happened:** while preparing my labeling sheet, Claude showed that "Unity Catalog", one of Arya's skills, appears in
  **901 of 901** postings because it's in Databricks' standard "About Databricks" paragraph. My rule as written gave every posting a
  free skill. I hadn't read real postings before writing the rule.
- **What I did:** added a dated amendment instead of editing the original text: Unity Catalog is not counted. Claude checked that
  none of the 24 already-reported verdicts changed. The whole-board count went from 6 relevant to 4.
- **What I understand now:** a rule written before looking at the data can be "correct" and still meaningless on that data.
- **Evidence:** CONTRACT.md "Amendments"; commit c665200; test `test_databricks_is_not_a_free_skill`.

### 2026-10-31 — Labeling, and redrawing the sample

- **What happened:** Claude's first random draw of 20 postings had 17 that were Senior/Staff/Director/Manager or outside the US, so
  every judge would say "no" and the experiment would show nothing. That draw was discarded **before** I labeled anything or Claude
  judged anything, and replaced by a stratified draw (seed 7375), documented in `experiments/select_postings.py`.
- **What I did:** I labeled all 20. Most of my "no" answers were about location, so I set one rule: any job outside the US is not relevant.
  I judged the 9 US postings one by one. I said yes to two: #3 Solutions Engineer (NYC) and #4 Software Engineer, New Grad.
- **Evidence:** `labels/hand_labels.csv`, `labels/README.md`, commit c665200.

### 2026-10-31 — My #4 label was wrong, and Claude was consistently right

- **I expected:** Claude to disagree with me on borderline postings, not to be right where I was wrong.
- **What happened:** on #4 (Software Engineer, New Grad, 2027 Start), Claude said "not relevant" in **4 of 4** fresh calls. Its reason:
  the role is for people graduating in Fall 2026 or Spring 2027, and Arya's résumé says she graduated in December 2025. It also asks for Java or C++.
  At first I asked: if she graduated in Dec 2025, doesn't she need a job now? Yes, which is exactly why a 2027-start new-grad role
  doesn't fit her. I had labeled from a summary that showed "new grad, Java or C++" but not the graduation window.
- **What I did:** I kept my label as `relevant`. Claude suggested keeping it, and I accepted, because changing the answer key after seeing the
  model's answer would hide the mistake. I reported it in SAMPLING.md and PROMPT_EXPERIMENT.md instead.
- **What I understand now:** **repeatable is not correct, in either direction.** Claude's 4/4 consistency didn't prove it right; checking
  the posting did. My hand label wasn't automatically right either: a label is only as good as what I read before choosing it.
- **Evidence:** `experiments/results/sampling_v1.jsonl` (#4, attempts 1–4); SAMPLING.md.

### 2026-10-31 — Same posting, different answers; and a test that caught a real bug

- **What happened:**
  - #3 (Solutions Engineer) got relevant, relevant, not relevant, and one reply rejected by the validator across 4 fresh calls.
  - The three action surfaces gave two different verdicts on it within one minute.
  - The rejected reply was over the validator's 600-character limit, which the prompt never states. That's a mismatch I created, still unfixed.
  - Separately, a test failed during the build: two runs in the same second overwrote each other's raw evidence file. Claude fixed it so
    evidence is never overwritten, and the test now passes.
- **Evidence:** SAMPLING.md, ACTION_SURFACE.md, `jsagent/watch.py` `unused_path`, test `test_baseline_then_only_new_and_never_repeat`.

### 2026-10-31 — What I accepted, changed, and rejected from Claude

- **Accepted:**
  - Board and persona defaults (Databricks, the priya-nair example).
  - Claude's recommendations on wrong versions (the brief's two examples, plus two extra tests).
  - The labeling-rule wording "honest fit today".
  - Not counting Ray and Kubeflow.
  - Keeping the #4 label locked.
- **Changed / decided myself:**
  - Renamed the persona to Arya Sahni.
  - Added ML title words.
  - US-only labeling.
  - Chose the v2 change (add my criteria).
  - Chose amendment 1.
- **Rejected:** Claude's first wording for SOURCES ("Claude transcribed the answers…"). I asked for different wording, and it now says the decisions are
  mine and Claude formatted them.

### 2026-10-31 — Pre-submission audit against the brief and classmates' folders

- **I tried / expected:** before signing, I asked Claude to check everything against the brief again and against my classmates'
  submissions, because I didn't want to lose marks.
- **What happened:** the audit found three gaps between what my contract says and what the code did:
  - "Out" promises each posting's `location` and `url`, but the verdicts didn't include them.
  - The contract says "all matching is case-insensitive", but the code matches "US" and state codes in capitals only. Claude
    checked that case-insensitive matching would wrongly put "Montréal, Canada" in Alabama ("al"), so the code was right and the contract was incomplete.
  - The driver's seat pointed only to commits, not to transcript lines.
- **What I did:** added amendment 2 to CONTRACT.md (case-sensitive state codes) instead of editing the original text. Claude added the two
  fields with a test and re-ran the seeded watch (same counts), added quoted chat lines to the driver's seat, added `requirements.txt`
  and a sources line to the README.
- **What I did myself:** ran the full test suite on my own machine (`python3 -m unittest discover -s tests -v` → 17 tests, OK).
- **Evidence:** CONTRACT.md amendment 2; `test_out_fields_present`; `test_location`; the final commit.

### 2026-10-31 — Comparing my work with four classmates' submissions

- **What happened:** Claude read aditya-r, sreevarshan-s, revan-c and pavan-m in depth next to mine. My strengths: the #4 case, a real
  two-day change with 24 real new postings, the dated amendments, and quoted chat lines in the driver's seat. My gaps: no proof the tests
  catch the wrong versions in the real code, an undisclosed validator limit, an arithmetic slip in SAMPLING.md (I wrote "18 of 20" valid
  where the file shows 19), and an action-surface comparison confounded by a shorter prompt.
- **What I did:** added `tools/check_wrong_versions.py` (all 4 mutations caught), re-ran the 3 surfaces with the full format (all 3 now
  pass the validator), corrected the count, cited the `called_at` order for the experiment, added sha256 provenance, ran a fresh clone,
  and added the validator limit and prompt injection to "Not checked".
- **What I didn't copy:** classmates' 80-test suites and multi-draft contracts. I can't honestly recreate a drafting history I don't have.

### 2026-10-31 — Hand check of one rule verdict

- **I tried:** working through my own rule by hand on posting 6866538002 (Data Science Intern, 2027 Start), before Claude told me the code's answer.
  The first link Claude gave me opened in Google search, not the posting, so Claude saved the exact text the agent read to a file.
- **What happened:** title, location and seniority matched the code. I found none of Arya's skills, but the code found Python and SQL, both
  in one line I missed ("Proven ability to work with data in SQL and Python"). My verdict was not relevant, because it is an internship and
  Arya wants full-time. The rule says relevant, because it has no Intern exclusion.
- **What I did:** recorded it in `labels/handcheck/README.md`. I didn't change the rule tonight; adding Intern/Internship is the next step.

### In my own words [Riya, own words]

When Claude was right about #4 I realised that human error is something major and we need such AI to help us find the errors which can be
used to avoid future errors. When I noticed the internship gap I felt that I should have given proper instructions in the first place to avoid
such issues. If I did this again I would make sure to be thorough in my requirements and check all the things myself so that I can catch the
mistakes the AI and I have made.

*(Written by me in the chat. Claude suggested two edits, which I accepted: spelling fixes, and "the mistakes the AI has made" →
"the mistakes the AI and I have made".)*

### Still unresolved

- **The held-out set has no "relevant" labels**, so 10/10 there means nothing. "Always no" scores the same. Next time: stratify the split by label.
- **My rule's title list is too narrow.** It said no to all 20 labeled postings and missed both of my yeses ("Solutions Engineer",
  "Software Engineer"). I haven't decided whether those titles should count for Arya.
- **The real two-day change uses a classmate's 10-29 snapshot (seeded).** My own live run 2 was 33 minutes after run 1 and found 0 new.
  Next step: run the watch again on a later day.
- **The validator's 600-character limit isn't in the prompt.**
- **The rule has no Intern/Internship exclusion** (found by my hand check).
