# Frictional: Job-Search Agent 1

Pavithra Prasad · INFO 7375 · JS1 The Contract and the Watch

Commits (`fall-2026/pavithra-p/js1-contract-and-watch/`), oldest first: `586c296` my contract draft · `9aed486` reviewed contract · `c175a59` watcher · `d6a3a4b` run 1 · `695ed9f` rule and wrong versions · `5b130b8` first freeze · `c16b311` re-freeze · `7327ccd` my labels · `7bfeae4` Claude judge · `71cdf3b` sampling replies · `d500451` persona · `aa3e1ab` sampling report · `287eefe` baseline dev · `30e32c3` prompt experiment · `15e9d2a` run 2 · `5a9bd79` action surfaces · `ac36f3d` README, sources and frictional · `e185766` label audit and experiment 2 · final commit: the hash in the Canvas submission.

My main prompts and inputs to Claude Code (quotation marks show my exact words; the rest is summarised):

- 2026-10-29: "So make sure you follow all the details mentioned in the assignment description, and make sure you remember all the previous TA remarks which we had got for deduction."
- 2026-10-29: Asked to keep the contract to only what the assignment asks (six sections).
- 2026-10-30: Checked that the watched board, Pinterest, is on Greenhouse, the host we chose.
- 2026-10-30: Asked for a re-freeze with non-senior roles, and set all software engineer roles as in scope for Rohan.
- 2026-10-31: Chose the one prompt change in experiment 1 and wrote my sampling conclusion.
- 2026-10-31: "Okay, so just go ahead with the experimenting and let me know what all I should do" (experiment 2), then set my labels: every posting asking for 3 or more years is Not Relevant.

## 2026-10-29: The contract

- Wrote my contract draft: In, Out, Refuses, the rule and the failure sentence (`586c296`).
- Claude Code sharpened it: exact title words, whole-word skill matching, the refuses list and the two wrong versions. It came out too long, so I asked for only what the assignment asks: six sections (`9aed486`). Both were committed before any code.
- Friction: Pinterest writes "CA" for both California and Canada, so the rule only accepts "United States", "USA" or "US" (`test_location_rejects_toronto_ca`).

## 2026-10-29: The board

- Tried GitLab first: my rule marked only 1 of its 236 jobs Relevant. Switched to Pinterest.
- A ChatGPT review suggested a board with more entry-level roles. I kept Pinterest; Figma and Twilio were used only for the experiment.

## 2026-10-30: Run 1 and the 20 postings

- Ran the baseline in my own terminal: 165 jobs, 0 new (`d6a3a4b`).
- The first freeze of 20 postings was mostly senior roles (`5b130b8`). I asked why, and it was re-frozen as 20 non-senior roles from Pinterest, Figma and Twilio (`c16b311`), before any label or Claude answer.

## 2026-10-30: My labels

- Labelled all 20 before any Claude run: 11 Relevant, 9 Not Relevant (`7327ccd`).
- Hard decision: I labelled by title. Only plain Software Engineer roles count; senior and ML roles are not Rohan's background. I did not check years. Claude Code pointed out that this differs from my written rule. I kept my labels and noted it in `experiment/README.md`.

## 2026-10-30: Sampling

- 5 postings × 4 fresh Claude conversations: 20/20 valid, the same verdict every time (`71cdf3b`).
- Unexpected: Claude disagreed with my labels on 3 of 5. Its reasons quoted the years, for example "4+ years" in 8009057 (line 35).
- I thought Claude would mostly agree with my answers. I was surprised when three were different, but I realized I had not checked the job descriptions properly.

## 2026-10-30: Persona name

- Changed the fictional persona's name from Aarav Patel to Rohan Mehta (`d500451`). Only the name and contact details changed.

## 2026-10-31: Prompt experiment

- Baseline on dev: 3/10 against my labels, lower than answering "Not Relevant" every time (5/10) (`287eefe`).
- I chose one change, line 6 of the prompt: stop using the years the description asks for. Claude Code predicted about 7/10 before the run. Result: dev 7/10, then held-out last, 4/10 → 8/10 (`30e32c3`).
- The scores improved, but I am not sure the answers actually got better. The new prompt matched my labels more closely, but I may have made mistakes when labeling the jobs.

## 2026-10-31: Run 2 and the action surfaces

- Ran the watch in my own terminal: 8 new Pinterest jobs (`15e9d2a`). I ran it twice by accident; the second run found 0 new, so nothing was reported twice (`test_second_run_reports_only_unseen_ids`).
- Unexpected: 2 of Claude's 8 replies left `resume_fields` empty. The validator rejected them, and they were saved, not repaired (`test_invalid_reply_is_saved_and_never_repaired`).
- Pasted job 7832348 into claude.ai myself. Chat, file and agent all said Not Relevant ("Staff", 6+ years) (`5a9bd79`).

## 2026-10-31: Label audit

- A ChatGPT cross-check of my draft found that 13 of my 20 labels differ from my written rule.
- Claude Code added `python3 -m agent audit` (`test_audit.py`). I ran it: my labels match the rule on 7 of 20. Against the rule, the baseline scores 10/10 on both sets and the revision 6/10.
- Unexpected: the new prompt matched my labels more, but my contract less.
- I kept my labels as they were (`7327ccd`) and opened three postings myself: 8009057 asks for "4+ years"; 7838591 asks for no years and names Python, Java and TypeScript; 8213988 asks for "Minimum of 2 years" and names SQL and Python. All three match the rule, not my label.

## 2026-10-31: Experiment 2

- After the audit I started a second experiment: 20 new postings from seven more boards, frozen before any label or Claude answer (`experiment-2/`, `test_set_2_drops_set_1_and_repeats_and_takes_up_to_4_per_board_biggest_first`).
- I read 9 postings myself first ("its close to 3 so i feel can be relevant"). Then Claude Code listed the years lines and skills of all 20, and I decided: "all more than 3 yoe skip it i wont apply" and "ok all the others i would recommend". 8 Relevant, 12 Not Relevant.
- Friction: Claude Code deleted the first freeze by mistake before it was committed. It saved the boards again, and the same 20 postings came back.
- I left the one prompt change to Claude Code ("do whatever you feel would be correct"). It chose reading a range of years by the lowest number. I accepted it: "yes because there could be multiple postings based on the yoe so thats why i feel its better to consider the lower bound since they have mention ed and sk;ll matches". Result: 8/10 before and after, on dev and held-out.
- Unexpected: all 4 misses are postings I called Relevant with fewer than two of Rohan's skills. And my rule's code misread "2–12+ years" and "1.5+ years" on 3 postings that Claude read correctly. The decimal one is fixed with a test (`test_experience_reads_decimal_years_whole`); ranges are left open because my contract does not say how to read them.

## What is unresolved

- Some jobs were still marked incorrectly, and a few answers had format errors. Next time, I would check the job descriptions more carefully and test with more jobs.

## Human and AI contributions

- I did: wrote the contract draft, chose the board, rejected the senior-only freeze, labelled the 20 postings, wrote the sampling conclusion, chose the persona name and the prompt change, ran both watch runs and the audit, did the claude.ai chat, checked four postings by hand, and decided the 20 labels of experiment 2.
- Claude Code: sharpened the contract, wrote the code and the 46 tests, ran the freezes, sampling and experiments, listed the years and skills for my experiment 2 labels, chose the experiment 2 change when I asked it to, and drafted the reports.
- Accepted: the sharpened rule, the "CA" check, keeping Claude without tools, the label audit.
- Changed: the long contract (cut to six sections), the first freeze, the persona name.
- Rejected: changing my labels to match my rule; moving away from Pinterest.
