# FRICTIONAL — honest log

I started this assignment thinking the hard part would be the code. It wasn't. Claude Code wrote most of it quickly. The hard parts were deciding what a "relevant" job actually means for my persona, and checking whether the answers I got back were true. I selected the data engineering and data analyst roles, tightened the location and experience rules, hand-labeled 20 postings. Several of the most useful lessons came from things going wrong: a truncated posting, an overwritten file, and my own labels contradicting my rule. This log records those moments honestly, with the times, files, and tests behind them.

## 1. Building the contract and choosing a board

I started by having Claude draft the first contract from resume.json and four rules, R1–R4. My first board, Discord, turned out to be almost all senior roles in San Francisco, which was useless for that persona. Claude checked 9 other boards and we switched to Klaviyo. The contract’s worked example also described a real posting that nobody had actually read. I didn’t want an unverified claim in my contract, so I had it rewritten as a clearly labeled, made-up example.

All 54 tests passed on the first try. I didn’t trust that on its own, so we ran scripts/sabotage_check.py, which turns off the audit. The wrong-version tests then failed, which showed they really can catch mistakes. In my first runs, the two judges disagreed on 3 of 6 postings. Claude pointed to experience requirements (“5+ years”, “1-3 years Android”), and I found each one in the raw posting text. That’s how I learned my v1 rule never read years at all, and that it was counting skills from boilerplate, like “React” inside “React Native”.

## 2. v2: switching to data engineer roles

Next I changed my target to data engineer roles asking for 2–5 years, since that’s the job search I actually care about. Klaviyo had no data engineer postings at all. A scan of 49 Greenhouse boards turned up 34 roles asking for 5 years or less, so I picked Samsara and made a new fictional persona, later renamed Evan Gordon. I revised the contract openly instead of quietly editing it. The new R5 reads stated years, which closed the gap from v1. I also allowed “Senior” titles, since many of them only ask for 4–5 years, and required remote roles to be in the US. The new tests failed against the old code (15 errors) before I updated it, and then passed. That’s the order I wanted: contract, then tests, then code.

Three times, Claude wrote a guessed time into the contract that didn’t match when the file was actually saved. I corrected each one, and after that we took times straight from the file. For the experiment, I used every distinct data-titled posting on 7 saved boards (experiments/source_raw/). When the pool grew to 21, the random shuffle left out Coinbase’s “Senior Market Data Engineer”, which was probably a good match. I didn’t swap it back in, because choosing postings after seeing them would be cherry-picking.

## 3. Bugs I found and fixed

The biggest bug was that Claude was getting cut-off input. On Samsara 8039914, Claude said “relevant” and noted that “the content shown states no required years.” That wording made me look closer, and it turned out the judge was only sending the first 6,000 characters. “10+ years” was at character 6,284, so Claude never saw it. The fix raised the limit to 20,000 characters, flags any truncation, and adds a test (test_long_content_sent_whole_or_flagged). After re-judging, all 6 postings agreed with the rule. My labeling tool had the same issue (it only showed 3,500 characters), so I fixed that too.

The second bug came from my own replay. When I ran scripts/replay_runs.sh, the output said “replay of Run 2” but showed Run 3’s file. Two downloads in the same second had saved under the same name, so one overwrote the other. Raw files can no longer be overwritten (test_raw_files_never_overwritten), and the replay now reads each run’s file from the state file.

There were smaller fixes too. The console printed “PREFERRED years” on postings that weren’t even relevant, so now it only shows preferences for relevant ones. When I watched many boards, the state file listed 128 boards instead of 131, because boards with zero jobs never got saved. I wrote a test first (test_v3_empty_board_counts_as_seen) and then fixed it. Last, my .gitignore blocked every file named resume.json, including the two redacted fictional copies I used as action-surface evidence. They’d have been in my zip but missing from GitHub, so I added an exception for just those two files.

## 4. Adding data analyst roles and BI tools

I then added data analyst to my target titles. I wrote the test first (test_r1_data_analyst_added_in_v2_1), watched it fail, and it passed once the persona was updated. Samsara has no data analyst postings, and my 7 experiment boards had only one, Brex’s “Data Analyst II”. I also added Tableau and Power BI to Evan’s skills. I’d typed “PowerBI”, but the skills check matches exact whole words and postings write “Power BI”, so I saved it as “Power BI”. A test confirms “PowerBI” as one word doesn’t match. I also added an experience bullet so Evan’s résumé actually backs up the skill. After that, Claude noticed that Samsara 7922530 “warns against BI/SQL-modeling profiles”, which is the kind of nuance my rule can’t pick up.

## 5. Location rules

Next I set the location rules: remote jobs have to be in the US, Evan is willing to relocate, and Boston is preferred. Claude took “relocate” to mean within the US, and I confirmed that’s what I meant. Boston is just a preference label and never changes whether a job is relevant. The location check now uses an explicit list of US places (states, state codes, and major metros). Before any run, I tested it on all 208 real location strings in my saved data. 107 passed, and every one of them really was in the US. I added “Houston” and “West Coast” after seeing that data, which changed the list, not any of my labels. The check still has limits: a bare “Remote” fails, US cities not on the list fail, and Greater Boston towns like Somerville don’t get marked as preferred.

## 6. Persona changes

I renamed the persona Evan Gordon and said roles asking for 3–4 years should be preferred. Instead of guessing, Claude asked whether I meant a filter or a preference. My answer: 0–4 years preferred, 5 acceptable, more than 5 not valid. I then updated Evan’s education and work history to look realistic for a data engineer with about 4 years of experience. Where I didn’t give exact dates, Claude listed its choices as assumptions. I never pasted a real résumé. I only gave the degree, field, and years, and all the employers are fictional.

I checked two test cases by hand against the five rules (fixtures 1004 and 1003), and both matched the tests. My first try at running the suite failed because I left the . out of -t .. Once I fixed that, all 65 tests passed, and later all 75. I froze the persona before labeling, so every label and experiment uses the same Evan.

## 7. Job board changes

At one point I tried watching every Greenhouse board I could find. Claude tried 338 company names and 131 responded. It warned me upfront that this went beyond the brief’s “one public job board”, and I went ahead anyway. That run judged 10 new postings, and the two judges agreed on 9. When I re-read the brief (“one board, the smallest honest slice”), I decided to go back to one board. config/boards.json now lists only samsara, and test_board_list_config failed and then passed. The fresh runs went 0 → 6 new (5 judged) → 0, and the judges agreed on all 5. I kept the 131-board list as config/boards_all.json.

I also deleted the archive/ folder of earlier runs to keep the submission small, which took it from 47 MB to 24 MB. Before I did, Claude pointed out that it held the original v1 contract, the raw posting from the truncation bug, and the 131-board results. Those now live only in this log, the tests, and the code.

## 8. Labeling

I finished my labeling rule (LABELING_RULE.md) before labeling anything. In my first pass, I labeled 18 of 20 postings and skipped 2. When I checked those labels against my own rule, I found I’d marked 4 Staff/Lead roles as relevant even though my rule excludes them, and most of my notes just repeated the job title. I’d been going by titles. That pass is saved as labels_first_pass_19-45.csv.

In my second pass (label.py --redo), I labeled the 2 I’d skipped. For one intern role I typed “n” as the note but left it marked relevant, which was a typo. That pass is saved as labels_second_pass_19-49.csv. I then decided to follow my rule as written, so the 4 Staff/Lead roles and the intern became “not relevant”. I made that call before running Claude or the rule judge against my labels. One limitation is still there: most of my notes are title-level, so some labels reflect the title more than the full rule.

## 9. Sampling and the prompt experiment

For sampling, I asked Claude about 5 postings, 4 fresh times each. All 20 answers were consistent and none were rejected. But on Discord 8299493002, Claude disagreed with my label all 4 times by repeating the same misreading. The résumé fields it cited also changed between calls, even when the verdict didn’t. I checked every reason Claude gave when it missed. Two of its misses, 7858719 and 7917475, both ask for “8+ years”, so those were actually my labeling mistakes, since my own rule says they aren’t relevant. On 8299493002, Claude’s reason was partly wrong: it read “5+ years of production code” as “5+ years of ad-tech.”

For the prompt experiment, I picked one change out of three options: a sentence about domain experience. It’s the only difference between prompts/judge_v1_baseline.txt and prompts/judge_v2_revision.txt. Both versions gave identical results, 8/10 on dev and 9/10 on held-out, with raw results in experiments/prompt_experiment/results/*.jsonl. The change didn’t fix the posting I aimed it at, because Claude still treated the requirement as an ads-specific minimum. Looking back, the “quote the exact phrase” option would have gone after the real cause. I stuck to the protocol the whole way: I didn’t change any labels after seeing Claude’s answers, and I unlocked the held-out set only once per prompt (results/HELDOUT_LOG.txt). Across nine watch runs, Samsara 7922530 was judged relevant 6 times and not relevant 3 times.

## 10. What I accepted, changed, rejected, learned, and left open

Rejected: the unverified worked example, editing my v1 rule in place after its runs, guessed timestamps, and editing my dev labels after seeing Claude’s answers.

Changed: the board (Discord → Klaviyo → Samsara → 131 boards → Samsara), the persona (Rohan → Jordan → Evan, plus data analyst, BI tools, location, and preferred years), how experiment postings were chosen, how much text the judge gets, and how much the labeling tool shows.

Accepted after checking: Claude’s experience claims (I searched the raw text for each one), its “content shown” remark (which led me to the truncation bug), and Claude’s reference drafts for my three conclusions, which I rewrote in my own words.

What I learned: A verdict that repeats isn’t necessarily right; 8299493002 got the same wrong reading four times in a row. The validator checks Claude’s format, not whether its reasons are true, and only reading the posting myself caught the “ad-tech” misreading. My own labels need the same checking as Claude’s answers, because labeling by title left me with two labels that break my own rule. Claude only knows what my code gives it: the 6,000-character cut hid a requirement, and the saved raw response is what exposed it. Fixing the wrong cause changes nothing; my v2 sentence went after domain bias when the real problem was a misread requirement. And I should re-read the brief before expanding the project, since going to 131 boards meant I later had to switch back to one.

Traceability: The prompts are prompts/judge_v1_baseline.txt and prompts/judge_v2_revision.txt (one sentence apart), with held-out unlocks in results/HELDOUT_LOG.txt. The tests are the ones named above, plus the full suite (python3 -m unittest discover -s tests -t ., 75 tests) and scripts/sabotage_check.py. Run evidence is in evidence/raw/ and evidence/runs/, along with state/seen_ids.json, experiments/sampling/results.jsonl, and my two label snapshots, labels_first_pass_19-45.csv and labels_second_pass_19-49.csv

Still unresolved: My location check depends on a hand-maintained list of US places. My years check only reads the first years phrase, so it can’t tell “minimum” from “preferred”. Two of my labels still break my own rule. There was no real second calendar day, so the change between runs was seeded. And I didn’t read Greenhouse’s terms of use in full.