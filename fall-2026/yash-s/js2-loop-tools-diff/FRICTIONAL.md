# FRICTIONAL — Job-Search Agent 2

## 2026-11-09: Planning the Loop and Writing the Gate

### What I Am Building

In Job-Search Agent 1, I built a watcher for the Databricks Greenhouse job board.

It saved raw responses, remembered posting IDs, and reported only new jobs.

For Job-Search Agent 2, I want to extend that system into a bounded multi-board agent.

The agent will watch several boards, follow request and time limits, use a permission policy, and report why each run stopped.

I am starting from my JS1 code rather than building everything again.

I will use the instructor's Lectern collector as a reference for other applicant-tracking systems, but I will record what code or ideas I actually reuse.

### My Board Choices

I chose four boards for the first version:

1. Databricks on Greenhouse
2. Anthropic on Greenhouse
3. OpenAI on Ashby
4. A deliberately misspelled Greenhouse board, `databricks-misspelled`

This gives me three intended working boards across two applicant-tracking systems, plus one deliberate failure.

I selected the misspelled board because I want to see whether my agent correctly handles a failed request.

### My Prediction Before Running

I predict that the three real boards will return job postings.

I expect the misspelled board to return an HTTP 404 error because the board name should not exist.

My agent should record this as a failed board, not as a board with zero new postings.

Since one planned board fails, I expect the overall run to be marked incomplete rather than finished, assuming the other boards succeed and no budget is exhausted.

For Databricks, I predict approximately 10 new postings since the last JS1 watch on October 31.

This is only a prediction. I have not run the JS2 agent yet.

### My Budget Decision

I decided to start with a limit of 4 boards, 6 HTTP requests, and 120 seconds per run.

I want the loop to have clear limits instead of continuing indefinitely.

I will allow one retry for a timeout or temporary server error, but no retry for an HTTP 404.

Retries must count toward the request budget.

If a budget is reached, the agent must stop and explain what work is unfinished.

### My Permission Decisions

I will allow HTTPS requests only to the Greenhouse and Ashby API hosts used by my selected boards.

I will allow the program to read the fictional resume and write evidence to its approved folders.

It must not write outside those folders, modify the fictional resume, or reset state without the required approval.

I want the permission restrictions implemented in code because prompt instructions alone are not enough.

### What I Think Could Go Wrong

One problem I expect is the loop treating a failed board as an empty board.

This would be misleading because the agent might report zero new jobs even though it never received a valid response.

Another problem could be an incorrect path check that allows writes to a folder with a similar name, such as `runs-evil`.

I will write tests for these cases.

### What I Learned From JS1

My JS1 project received 100/100.

The TA appreciated that I wrote predictions before testing, checked Claude's claims against real data, and recorded failures instead of hiding them.

The TA also suggested that I find some genuinely relevant postings so I can measure false negatives.

For JS2, I want to pay more attention to that limitation if I find suitable early-career postings.

The TA also suggested rerunning planted-bug checks after changes.

I plan to save those checks as part of this project instead of running them only once in a temporary folder.

### Decisions After Reviewing My Gate

Before implementing the agent, Claude reviewed my gate and pointed out two areas that needed clearer rules. I agreed with the feedback and updated my decisions before starting the implementation.

First, I decided that a well-formed empty job list can initially be treated as a successful observation. A separate checker will compare it with an earlier saved response and flag a suspicious drop to zero. This will help me demonstrate that an agent can finish normally but still give a wrong answer.

Second, I decided to start Databricks from my final JS1 state containing 924 seen IDs. Anthropic and OpenAI will start with new baseline states.

I also clarified how invalid responses affect exit status, how evidence files are protected from overwriting, and what the approval flag can and cannot prove.

I made these decisions before building or testing the JS2 implementation.

### What I Will Do Next

I will commit GATE.md, BOUNDARY-TESTS.md, and this FRICTIONAL entry before Claude Code writes the new implementation.

After that, I will ask Claude to implement the loop and permission checks according to the written gate.

I will run the tests myself and record the actual results next to my original predictions.

I will keep the original decisions in Git history if I need to revise them later.
