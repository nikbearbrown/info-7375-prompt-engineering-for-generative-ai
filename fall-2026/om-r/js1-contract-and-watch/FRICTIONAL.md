# FRICTIONAL.md: honest log

## 2026-10-30: the whole-word rule does not match "LLMs" (found limitation, rule kept as written)

**What happened.** After the baseline run, I applied the rule to all 238
real postings in `evidence/gitlab_jobs_20261030T201528Z.json` as a dry check.
None of them was reported as new. Output: `logs/dry_check_rule_over_baseline.txt`.

| Skill (CONTRACT.md rule) | Postings matching (whole-word, case-insensitive) |
|---|---:|
| Python | 24 |
| LLM | 11 |
| LangChain | 2 |
| RAG | 1 |
| PyTorch | 0 |
| vector databases | 0 |

6 of 238 postings came out relevant (at least 2 matches).

**The limitation.** 3 postings contain "LLMs" (plural): 8883003002,
8861748002, and 8871406002. Under the rule as written (whole-word match),
"LLMs" is correctly **not** a match for "LLM".
- 8883003002 (Director, Analytics Engineering) also says "LLM" elsewhere,
  so it matched LLM anyway and is relevant.
- 8861748002 (People Systems Engineer) and 8871406002 (Senior CX Platform
  Engineer) each matched only Python, so they are **not relevant**. If
  "LLMs" counted, each would have 2 of 6 and **would flip to relevant**.

So the plural gap changes 2 real verdicts in this snapshot. It is not just
cosmetic. PyTorch and "vector databases" appeared in 0 postings. The rule's
exact phrase "vector databases" would also miss the singular "vector
database" (0 postings in this snapshot either way).

**Decision.** I did not change the rule or CONTRACT.md. The contract was
written before any code, and the rule's value is that a TA can recompute
it by hand. Quietly widening it after seeing the data would mean writing
the contract to fit the results. The limitation is recorded here and is
material for the Sampling Report (Chapter 1): the Claude judgment step
may call these two postings relevant where the rule does not. That
disagreement should be labeled record vs. judgment, not "fixed".

**Unresolved.** Whether stemming or plural handling belongs in a future
revision of the contract, written as a new dated rule rather than a
silent patch.

## 2026-10-30: the contract's failure case was checked for and not present

CONTRACT.md's dated failure case is a "relevant" verdict on a role that
requires on-site presence or excludes remote candidates. I ran a rough
hand-written regex (`on-?site|in[- ]office|not (open to|eligible for) remote`)
over the 6 relevant postings. It found none (`logs/dry_check_rule_over_baseline.txt`).
That is evidence of one attempt on one snapshot, not proof of absence. The
regex can miss phrasings such as "must be located in" or "hybrid".

## 2026-10-30: the given endpoint returned no posting content

The URL first specified (`/v1/boards/gitlab/jobs`) returned 238 jobs with
no `content` field. The rule checks title **or** content, so that URL would
have quietly reduced it to a title-only rule. Changed to `?content=true`
(same host, same endpoint). Approved.

## 2026-10-30: hand labels were composed in a chat with Claude and transcribed afterward (process gap)

The 5 Sampling Report hand labels (`logs/sampling_hand_labels.md`) and my
labeling rule were composed in a chat conversation with Claude, which I
used as a drafting and thinking tool. They were transcribed into the
repository only afterward. The blank worksheet
(`logs/sampling_hand_labels_BLANK.md`, generated 2026-10-30T20:36:45Z) was
never filled in before the sampling calls ran.

Timeline from file timestamps:
- worksheet generated 20:36:45Z
- `scripts/sample_judge.py` calls ran 20:57:55Z to 20:58:58Z
- labels file written 21:05:10Z

My statement is that the labels were written in that chat before the
sampling calls ran. The only timing evidence is that chat's own
timestamps. No file in this repository records the labels before
21:05:10Z, after the calls. That is a real process gap, and I am naming it
rather than hiding it.

Two further limits:
- **Claude helped draft the labels.** They are not fully independent of
  the model they are compared against. CONTRACT.md requires Claude's
  judgment to be labeled separately from the record; by the same
  principle, Claude's part in drafting these labels is stated here.
- **Rule verdicts for these 5 postings were computed earlier.** The
  20:18Z dry check (`logs/dry_check_rule_over_baseline.txt`) ran the rule
  over all 238 baseline postings, these 5 included. It printed only the 6
  relevant ones; none of these 5 was among them, and their verdicts were
  not displayed.

**What I would do differently:** fill in the worksheet file itself, dated,
before running anything. The file's own timestamp would then be the
evidence.

## 2026-10-30: Prompt Experiment dev labels: title-only pass replaced; ChatGPT used as a reading aid

The first dev-set labeling pass was title-only. Before anything ran on
these postings, I replaced it with a full-content review pass that used
ChatGPT as a reading and drafting aid. This is disclosed per the course AI
policy. The judgment and the final verdicts are mine; I reviewed and
confirmed the labels before saving them.

The labels were saved to `logs/experiment_dev_labels.md` at
2026-10-30T21:23:43Z (SHA-256 `96b3cf98...c7b457`). The times of the two
labeling passes were not recorded. At save time, no rule, judge, or prompt
output existed for any of the 20 experiment postings. Labeling with AI
help again means these labels are not fully independent of model
judgment (see the hand-label note above).

## 2026-10-30: Prompt Experiment dev labels, timing (my account; adds to the note above)

"Dev-set hand labels for the Prompt Experiment: the first labeling pass
(title-only) and the full-content review pass (using ChatGPT as a reading/
drafting aid, disclosed per the course AI policy) both happened in quick
succession around 2026-10-30T21:20:00Z (5:20pm ET). The title-only pass
was explicitly discarded before anything ran -- several verdicts changed
once the full posting content was actually read (notably postings
8891301002 and 8806017002, which flipped from 'not relevant' to
'relevant' once the content, not just the title, was weighed against the
labeling rule). The final verdicts in logs/experiment_dev_labels.md are
Om's own judgment, confirmed by him before saving."

That time is my own statement. The only time on disk is the labels file's
save time, 2026-10-30T21:23:43Z, which fits it. The discarded title-only
pass was not saved anywhere.

## 2026-10-30: Prompt Experiment held-out labels: no AI assistance; labeled after seeing dev results

The held-out labels were saved to `logs/experiment_heldout_labels.md` at
2026-10-30T21:45:56Z (SHA-256 `fad8cf67...4b1697`). At that time no output
existed for any held-out posting under either prompt. 3 of 10 are labeled
relevant. The labeling rule is unchanged from dev.

**A difference from the dev set:** I used no AI assistance for the
held-out labels. For the dev labels I used ChatGPT as a reading and
drafting aid in the full-content pass (see the note above). So the two
label sets were made differently. Any dev vs. held-out difference in pass
rate could partly reflect that, not only the prompts.

**Labeled with knowledge of the dev results:** I wrote the held-out labels
after the dev phase was scored (dev calls 21:33-21:34Z). By then I knew
that both prompts' one dev miss (8891301002) turned on the word
"integrating". The rule text did not change, but several held-out reasons
now state my reading of it explicitly. Postings 12 and 18 say "my reading
of 'integrating'", and posting 17 states how I read its LLM requirement
("I read that fluency as advisory expertise"). My interpretation was made
explicit after seeing how Claude read the word. That is not the same as
seeing held-out outputs, which did not exist yet, but the labels are not
blind to the dev-phase discussion either.

## 2026-10-30: CORRECTION: no AI assistance was used for the dev-set labels

"Correction (2026-10-30, per Om Raut): the dev-set hand-label file
previously stated 'Labeled by: Om Raut (with ChatGPT assistance)'. This
was incorrect -- no ChatGPT or other AI assistance was actually used for
the dev-set labels. The file has been corrected to remove that claim.
The only genuine change between the dev set's title-only pass and its
full-content pass was reading the actual posting content more carefully,
not any AI tool."

**Record of the correction:**
- **Where the claim came from:** the ChatGPT statement entered this
  repository from my own instructions, in three places: the labels file
  header, and two FRICTIONAL.md notes ("title-only pass replaced; ChatGPT
  used as a reading aid" and the dev-label timing note). Those notes are
  left as written above and are superseded by this correction.
- **The held-out note:** its sentence "For the dev labels I used ChatGPT
  ... So the two label sets were made differently" is also superseded.
  Neither label set used AI assistance. One real process difference
  remains: dev had two passes (title-only, then full content) and
  held-out had one. The point that held-out was labeled after seeing the
  dev results still stands.
- **Evidence preserved:** the original file is kept unmodified as
  `logs/experiment_dev_labels.ORIGINAL_20261030T212343Z.md`, with its
  original timestamp (2026-10-30T21:23:43Z) and SHA-256 `96b3cf98...c7b457`.
  That timestamp is the evidence that the dev labels existed before the
  dev runs (21:33Z). The corrected `logs/experiment_dev_labels.md` (edited
  21:51:31Z, SHA-256 `56309630...f68854`) differs from it only in line 1.
  All 10 verdicts and reasons are identical, so no dev score changes.
- **Not affected:** the Sampling Report's hand labels, which were
  composed in a chat with Claude (see the 2026-10-30 hand-label note
  above). This correction concerns the Prompt Experiment dev labels only.
