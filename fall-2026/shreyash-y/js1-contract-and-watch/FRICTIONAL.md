# FRICTIONAL — Job-Search Agent 1

There are two parts, kept apart on purpose. **Part 1 is Shreyash's.** Part 2 is the log Claude Code kept while it built and ran things, where "I" means Claude Code.

## Part 1 — Shreyash

### What I did, from the session record

*Claude Code listed these from the session on 2026-10-31. They are things Shreyash said or did in it, and nothing here says what Shreyash thought or felt.*

- **2026-10-28.** Chose Oscar Health as the board, Opus as the judge model, and "Interview me" as the way to write the contract. Then wrote the contract: persona, In, Out, Refuses, the six-condition rule, two wrong versions and the failure sentence. It was pasted into the session and committed alone as `7c8f9e5`, before any code.
- **2026-10-28.** Confirmed the GitHub folder, `fall-2026/shreyash-y/`.
- **2026-10-30.** Asked for run 2 ("lets do run 2"). Run 2 was live, two calendar days after the baseline: 12 new postings (`079aedb`).
- **2026-10-31.** Wrote the labeling rule and labeled the 20 postings: all Not Relevant, verdicts only (`b3faea5`).
- **2026-10-31, after the experiment:** stated "i read the 20 ads myself". Added an evidence note for each of the 20 labels, reviewed the five disputed postings, and decided both interpretation choices (`labels/DISPUTED-POSTINGS-REVIEW.md`).

### In my own words

*Shreyash's words, pasted into the session on 2026-10-31. Claude Code did not change them.*

- **2026-10-31:**
  - What I tried and expected:
    I worked on a labeling rule for 20 Oscar Health job postings. My goal was to find jobs that matched my fictional applicant's skills, experience, and location. I expected the rule to clearly separate relevant and irrelevant jobs.
  - What surprised me, or what I checked:
    I noticed that even some software engineering jobs didn't match because they required more experience or had location restrictions. One thing that surprised me was that some jobs were tagged as remote but still required employees to come into an office.
  - What I accepted, changed, or rejected from Claude:
    I worked through the 20 job postings and their labels. Later, I looked at five postings where Claude and my rule gave different results. After checking the job descriptions, I found that Claude was right in those five cases. I decided to keep the rule-based approach, but I identified some problems with how it checks experience and remote locations that I still need to fix.
  - What I still don't understand, and my next step:
    I'm still figuring out how to handle jobs that don't clearly mention experience or location requirements. I also realized that having all 20 jobs marked Not Relevant doesn't really prove the rule works for matching jobs. My next step is to test the rule on more postings and see whether it can correctly identify relevant jobs too.

- **2026-10-31 — Posting Review:**
  I went back and checked the five postings where Claude and the rule disagreed. I found that the rule missed two experience requirements and incorrectly handled three location restrictions.
  For experience, I decided that the rule should use the highest minimum requirement mentioned in the mandatory qualifications because the applicant needs to meet all required experience conditions. For remote jobs, I decided that the job should only count as eligible if someone living in Massachusetts can actually work there.
  I didn't change the original experiment results because I wanted to keep a record of what went wrong. I have identified the issues, but I still need to update the code and add tests to make sure these cases are handled correctly. My next step is to make those changes and test whether they work consistently.

- **2026-10-31 — Experiment 2 labeling review:**
  Out of the 20 Klaviyo job postings, 4 were marked Relevant and 16 were Not Relevant. In the development set, 2 out of 10 jobs matched, and the held-out set also had 2 out of 10 matches.
  I noticed that most jobs didn't qualify because they required more than 3 years of experience, were in the wrong location, or didn't match enough skills. Some jobs had software engineering titles but still failed the rule.
  Compared to my earlier Oscar dataset, where all 20 jobs were marked Not Relevant, this dataset has both relevant and irrelevant jobs. I think this gives me a better way to test whether the agent can identify matching jobs instead of just rejecting everything.
  These are the results from the labeling review. My next step is to compare them with the agent's predictions and check where they disagree.

## Part 2 — Claude Code's process log ("I" = Claude Code)

**2026-10-28, before the contract.**
- I fetched Oscar's board once with curl to see its fields: 220 postings, and the same title in several cities under different ids. That shaped one of the wrong versions I suggested to Shreyash, but Shreyash wrote the contract. The fetch was not saved or used for any run (see SOURCES.md).

**2026-10-28 23:04–23:07, contract and tests first.**
- I committed Shreyash's contract alone (`7c8f9e5`).
- I wrote INTERPRETATIONS.md. Two phrases needed a choice the contract doesn't make: which of several "N+ years" counts, and whether "Remote (Florida)" is "remote within the United States". I picked the largest N, and yes for state-limited remote, and asked Shreyash to accept or change both. No answer came, so both are still my choices.
- I wrote the tests, including the wrong versions as real code in `tests/wrong_versions.py`, and ran them with no implementation. All 5 modules failed to import (`evidence/tests-before-implementation-2026-10-28.txt`), then I committed (`1ab74ec`).

**2026-10-28 23:10, implementation.**
- 63/65 tests passed on the first run. The 2 failures were my own test bug: the folder scan for real contact details flagged the fake bad email and phone that the persona tests use as examples, and then the fetch test's `…@evil.example.com` URL.
- I split those strings and allowed subdomains of example.com. I changed no rule or wrong-version test to make the code pass (`6d74630`).
- Later the same scan caught `accommodations@hioscar.com` inside a real Oscar posting. I allowed that one domain by name, because it is the employer's published address, not a person's (`20041e3`).

**2026-10-28 23:10, run 1.**
- Live baseline: 220 fetched, 0 reported new. A recount found the raw file's 220 unique ids equal to the state file, and the same sha256 (`evidence/run1-terminal-2026-10-28.txt`).
- I picked the 20 postings to label by a seeded procedure committed before labeling. A random draw from the whole board would have been almost all claims and clinical jobs, so the pool was limited to engineering and data departments and titles. Even so, Oscar had no junior engineering roles.

**2026-10-30 19:02, run 2.**
- 214 fetched, 12 new, 18 gone. A separate script that reads only the two raw files agreed.
- Wrong version 1 turned up for real: the same title, new ids, in 3 and 4 cities. All were reported separately.
- The two judges disagreed once (8172223, condition 3). The ad limits remote work to residents of certain states, and Massachusetts is not one of them. My literal rule passed it; Claude failed it. This was the case I had flagged as a choice two days earlier.

**2026-10-31, labels.**
- Shreyash labeled verdicts only, so the hand-label pass mark became verdict agreement. I had proposed verdict plus failed conditions on 2026-10-28, and it was not taken up.
- I kept a second score, Claude's failed conditions against the rule's record, labeled as not a hand label.
- **Unresolved:** with all 20 labels Not Relevant, a judge that always says "Not Relevant" scores 10/10. The pass mark cannot separate prompts.

**2026-10-31, sampling and development.**
- 20 sampling calls and 10 development calls all agreed with each other, and all said Not Relevant.
- The rule's record differed on two development postings. I read both ads in the saved raw response:
  - **8083703:** "4+ years of industry or other quantitative technical fields" has no word "experience", so my pattern missed it.
  - **6555819:** the office tag is "Remote", but the ad says "hybrid … live within commutable distance".
- In both cases Claude's reading fit the ad. My rule was the one that was wrong, even though anyone can recompute it.
- **I did not fix the rule.** Fixing it mid-experiment would have changed the record that run 2 and the experiment were scored against.
- I chose the one prompt change (quote the posting words behind each failed condition) after reading the development answers. Shreyash did not choose it.

**2026-10-31, a scorer bug before held-out.**
- My quote checker reported 57/58 quotes found. The one "miss" was `' (4), and its requirement of '`: a short quoted span had thrown off how my regex paired quote marks.
- After the fix: 58/58. Both the fix and the dev results were committed (`5c34654`) before the first held-out call (`9402a60`).

**2026-10-31, held-out.**
- The same pattern as development: 10/10 on the hand labels for both prompts, and 8/10 on the record.
- The two record disagreements were again the experience pattern (8319419) and a "Remote (New York)" tag on a hybrid ad (8250366).

**2026-10-31, action surface, way C.**
- **Attempt 1 failed.** My allow pattern `Bash(curl -s https://boards-api.greenhouse.io/*)` refused every curl the agent wrote (it used `-sS` and quotes). It stopped and said it had changed nothing.
- **Attempt 2 worked,** with `Bash(curl *)`, which allows curl to any host. Things I had not expected:
  - `ls`, `cat` and `jq` ran although they were not on my list.
  - It wrote files outside its folder.
  - It hand-typed 232 ids into a command. I checked them and they were correct.
  - Its summary said the state held 228 ids; it held 232.
- Way B, and way C, left folders in `~/.claude/projects/` despite `--no-session-persistence`.
- I trimmed the CLI's local environment listing from the four event logs before posting. Each file says so.

**2026-10-31 16:28, a bug in my validator, found by review.**
- A separate Claude agent graded the submission as a TA, seeing only the rubric and the files. It found that my validator's citation check was a plain substring test. The posting field `id` was "found" inside the word "considered", so the justification "This job is a good match and should be considered for the skills" passed.
- I confirmed it by running it myself. So wrong version 2 was caught for the rule judge but not for the Claude judge. My test for it only tried a justification with no field names at all.
- Fixed with whole-word matching (singular/plural and underscore-as-space allowed), and `id` alone no longer counts. I added 3 tests, so there are 68.
- I re-checked all 73 saved answers offline: none changed validity (`evidence/revalidation-2026-10-31.txt`). No reported result moved. The fix was made after the runs and is labeled that way.

**2026-10-31 16:38, run 3.**
- Shreyash asked for a new live run. It fetched 214 postings with 0 new and 0 gone.
- The raw response is byte-identical to run 2's (same sha256 `e6620c3549fb…`), so the board did not change in about 21.5 hours, and no Claude call was made.
- A separate recount agreed, and the state now records 3 runs. A quiet day is a real result for a watcher too: the baseline logic and the id memory held across three runs.

**2026-10-31 16:52–17:10, experiment 2.**
- Shreyash agreed with the review that experiment 1 could not test positives.
- I counted rule-positives on 20 Greenhouse boards (counts only) and picked Klaviyo. I committed a seeded pick of 20 with positives in both halves and a blind sheet (`c3eaff1`). Shreyash labeled all 20 with failed conditions and reasons (`8e2c92b`).
- Both unchanged prompts then found the 4 positives with no false ones, on development and on held-out, and gave identical answers to each other on all 20.
- The condition disagreements were more interesting than the verdicts:
  - Two postings list San Francisco as the location but Boston as an office. Claude passed condition 3; Shreyash and the rule failed it. The contract doesn't settle it.
  - On 7809608003 the rule and Claude both fail condition 4, with only Python in the ad. The hand label doesn't, which is probably a slip. I left the label as committed.
- The rule's experience defect showed up once more (7783904003).

**What I would do next (for JS2).**
- Fix the two rule defects, with tests taken from the five real postings.
- Ask Shreyash for per-condition labels.
- Add a board with junior roles, so the Relevant path is tested on a real posting.
