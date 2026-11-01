# FRICTIONAL: Job-Search Agent 1

> **How this file was made:** Claude Code drafted the factual log below from our session on 2026-10-31 and checked it against the commits and files it cites. The "My reflections" paragraph and the "Yes, it did" answer are my own words. The Agent 2 list is Claude's suggestion. All times are ET, 2026-10-31, unless marked.

## 1. What I tried and what happened

- **The contract.** First I asked Claude to write CONTRACT.md "so it doesn't get written off as AI wrote this". Claude declined to disguise authorship and offered two options: answer one question per section, or let it draft and label the draft. I chose to answer questions (Q1–Q6). I took several of its suggestions; each one is marked in the contract. The contract was committed alone, before any code (`5ca21ed`, 19:14).
- **Contradictions inside my own contract.**
  - In Q1 I listed Jack's cities; in Q2 I said location "is not a matter of concern". Claude asked which I meant, and I dropped location from the rule.
  - In Q3 I chose "skip the bad item and continue" for refusals. Claude kept "a résumé that fails the check stops the run" as the one exception, because there's nothing to continue with.
- **The failure sentence (Q6).** I didn't understand what was being asked, so Claude gave five examples. I took all five, and the contract says so.
- **No API key.** None was set. I chose to install the Claude Code CLI instead of creating a key (Claude had recommended the key). For the judge model I chose Opus 5.5 over Claude's suggestion of Sonnet.
- **Failure condition #3 fired on the first data pass (~19:39).** The rule marked Figma's "Data Platform Engineer" `not_relevant`: its description names only 1 of Jack's 8 skills (Python). The only "AWS" was inside "Washington". I did not change the rule.
- **The board didn't change.** Two live fetches about a minute apart had identical ids. The second run's "new" postings therefore come from a SEEDED earlier snapshot (the response minus its 10 newest postings), labeled as seeded everywhere.
- **The labeling sample took three draws** (`experiments/make_label_sheet.py`). Plain random gave 19 of 20 obvious non-matches. A data-title stratified draw still gave mostly Manager, Director and Intern roles. The third draw (14 plausible + 6 other) was used.
- **The action-surface agent run (surface 3).** It fetched the board but recorded a different URL than the one given, and its Write of `state.json` was denied, so no state file was produced. Its attempted id list was 140 of 140 correct when checked against the saved response.
- **Labeling.** I asked Claude to write the labeling rule (it did, labeled as its draft, and I accepted it unchanged). I then asked it to suggest labels and notes, and it declined. I labeled all 25 in chat and Claude recorded my words. My first answers had problems:
  - "somewhat relevant", which isn't a valid label;
  - five labels with no reason;
  - a location reason (#15) that broke my own rule;
  - reasons that didn't match the posting ("cybersecurity" for an HR-systems role; "design role" for an engineering internship);
  - reasons that didn't match Jack's résumé ("experience with AI tools"; "knows CRM and ERP").

  After Claude flagged these, I revised 8 entries, and 3 labels flipped from `relevant` to `not_relevant` (`experiments/label_revisions.md`). The labels were committed before any experiment ran (`f3bc3e4`, 20:44).
- **Every one of the 20 experiment labels came out `not_relevant`.** I briefly asked to broaden Jack's persona to software engineering. Claude laid out the cost (a contract revision, relabeling, re-running the sampling calls) and recommended against it. I kept the persona (option "a") and stated the limit instead.
- **Results.**
  - Both prompts scored 10/10 on dev and on held-out.
  - The rule matched my labels on 18 of 20; it missed Security Scientist and Data Scientist through branch (b).
  - Sampling: zero spread (each posting got the same verdict 4 of 4 times). Claude matched my label on 3 of 5.

## 2. What I checked, changed, or learned, and what is unresolved

**Checked:**
- I ran the tests (32 pass, including W1 and W2).
- Run 2's 10 new ids equal the 10 seeded removals.
- The agent's id list in the action-surface run was 140/140 correct.

**Not checked by me:**
- Failure condition #1 was recomputed by Claude with a second method (`scripts/recompute_rule.py`: 10/10 match), not by hand.

**Changed:**
- 8 hand-label entries, after the flags.
- The labeling-sample method, twice.

**Unresolved:**
- **The rule's skill thresholds cut both ways.** The 3-skill bar missed Data Platform Engineer, a posting I labeled relevant. The 4-skill branch (b) produced both of the rule's held-out errors.
- **The experiment can't test recall.** With all 20 labels `not_relevant`, it can only catch false positives.
- **Three labels are not independent of Claude.** 5551730004, 5552580004 and 6233040004 flipped after Claude's flags. For 6233040004, I had also already seen Claude's verdict.

**My reflections (my own words):**
I tested all the jobs which seemed relevant to Data Engineer on job board, I checked the skills and matched them using keywords to get accurate results, I also checked whether the experience was matching or not to judge the qualification of Jack. Some jobs didn't match where I was surprised seeing the results, it gave me a better understanding on how job platforms work when candidates apply for the jobs.

**On the labels Claude flagged (did the flags change my mind?):** Yes, it did.
**What to do differently in Agent 2** (suggested by Claude from tonight's results; I didn't come up with my own):
- Label a set that includes real positives, for example a board with more data engineering roles or several boards. Tonight's 20 were all `not_relevant`.
- Revisit the rule's thresholds through a dated contract revision. The 3-skill bar missed Data Platform Engineer, and branch (b) caused both of the rule's held-out errors.
- Label before seeing any Claude output, and do a real second-day run instead of a seeded one.

## 3. What I accepted, modified, or rejected from Claude

| Item | Accepted, modified, or rejected | Where |
|---|---|---|
| Writing the contract in a way that hides AI authorship | I asked for it; Claude declined; I answered questions instead | Claude Code session, 2026-10-31 (transcript kept on my machine) |
| Suggested titles, skills, whole-word matching, W1 + W2, label format, verdict values | accepted | marked in CONTRACT.md |
| "Lead" as a disqualifying word (offered as a candidate) | rejected; Lead titles are allowed | CONTRACT.md |
| Get an API key | rejected; used the CLI | README toolchain |
| Sonnet as judge | rejected; chose Opus 5.5 | `agent/config.py` |
| Failure-sentence examples | accepted, all five | CONTRACT.md |
| Labeling rule draft | accepted unchanged | `experiments/LABELING_RULE.md` |
| Flags on my label reasons | modified 8 entries | `experiments/label_revisions.md` |
| Broaden the persona vs. option (a) | Claude recommended (a); I accepted | this chat |
| Revision-prompt change (option 1 of 3) | accepted | `prompts/judge_revision.md` |
| Drafts of README write-ups, ACTION_SURFACE, SOURCES, this log | I did not edit them directly; I gave my views and corrections in chat, and Claude inserted them in my words | git diff after `f3bc3e4` |

## 4. Traceability

| Commit | Time | What it fixes in time |
|---|---|---|
| `5ca21ed` | 19:14 | CONTRACT.md alone, before code |
| `c32d395` | 20:03 | code, tests, runs 1–2, sampling calls, action-surface runs, all before labels |
| `f3bc3e4` | 20:44 | hand labels and the labeling rule, before any experiment run |
| _(final)_ | | results, write-ups, this file, sign-off |

- **Prompts:** `prompts/judge_baseline.md`, `prompts/judge_revision.md`.
- **Tests:** `tests/`.
- **Raw results:** `experiments/results/`, `runs/`, `evidence/raw/`.
