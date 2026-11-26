# Frictional — Job-Search Agent 3

Tushar Patel · INFO 7375 · Fall 2026 · JS3 — The Filter, the Tool, and the Score  
Written November 25, 2026, reflecting on November 21–24.

## November 21 — Rules before implementation

I chose Cole Palmer as the persona, decided to use the posting text returned by `?content=true`, and chose to work on JS3 first. Claude chat drafted FILTER.md v0.1 from those decisions. It was committed before implementation, including the “Wrong versions” table. That gave us something to check the implementation against.

Commit: `821ddee` (FILTER.md v0.1, before code).

## November 23 — My labels needed corrections too

The audit exposed labeling slips, including keeping an Account Executive posting despite the engineering-role requirement. I could not treat my labels as automatically correct just because they were mine.

The audit corrections happened after unblinding, so I disclosed them and kept the original results visible. I left the held-out labels unchanged rather than quietly improving the evaluation target after seeing results. This meant accepting imperfections in the evidence instead of presenting a cleaner history.

Commits: `f97f528` (blind labels), `0df210f` (audit), `9ed99ce` (post-unblinding corrections).

## November 23 — A heading changed the meaning

Claude chat flagged Claude Code’s reading of experience requirements under a “preferred” heading, and I decided the rule correction. A number appearing in a posting does not necessarily make it a mandatory qualification.

This was caught before the held-out evaluation. It made me pay closer attention to what a statement actually requires, rather than treating a matching phrase as enough. I also changed recommendations about C3, C4, and experience ranges instead of accepting every proposed rule change.

Commits: `d74ca78` (v0.2 frozen), `f3edf99` (C4 amendment, before held-out).

## November 23 — The held-out result did not separate the versions

Every mode scored 24/30 on the held-out set. That result did not show that v0.2 improved on v0.1, even though the rule changes seemed reasonable.

We then added a blind changed-postings set, where v0.1 scored 1/8 and v0.2 scored 6/8. That gave us evidence about cases affected by the changes. It did not replace the original held-out result or establish that v0.2 would improve by the same amount on ordinary postings. Both results belong in the report.

Commits: `4c6754d` (held-out 24/30), `685f22d` / `8d8e92f` / `2e4ee3a` (changed-postings set).

## November 23 — A new API key did not solve the 401

The claim run kept returning a 401 even after I supplied a new key. An older key was still being loaded, but we never established exactly where it came from. Claude chat guided the troubleshooting, and I fixed the configuration at the end of `~/.zshrc`.

Claude Code ran the live fetch and the live claim run. My contribution was fixing the configuration needed for the claim run. The run eventually worked, but I should not describe that as a complete explanation of the original configuration problem.

Evidence: `evidence/claims/aborted/` (aborted attempt); `65c97a2` (live claim run).

## November 23–24 — Claim labeling

I went through the process manually because I wanted to work through the claims myself. The distinction I kept returning to was whether a quote actually asserted the claim. “Postgres or MySQL” does not establish that PostgreSQL is required. An empty sponsorship quote does not establish either sponsorship or its absence. A relevant word can appear without supporting the conclusion attached to it.

Commits: `aaf850a` (labels), `d78f566` / `eaed4d9` (shortlist and my picks).

## November 24 — Abstaining on everything exposed a rule conflict

The abstention rule abstained on all 17 postings. This exposed a disagreement between the evidence rule and G5 about how to handle silence.

The filter could allow a posting through when it did not state a disqualifying condition. The evidence check still could not turn that silence into support for a positive claim. I needed to distinguish “not ruled out” from “supported by the quote.” Otherwise, the two parts of the system appeared to agree while answering different questions.

Commit: `d78f566`.

## November 24 — The tool declaration needed to match the behavior

The MCP server read the persona file without declaring that dependency. I required the declaration to be corrected.

A tool can return the expected result while its description leaves out something that affects that result. I wanted the declaration to describe what the server actually reads, so someone using it could understand the inputs behind its output.

Commits: `47282e9` (server), `cd74578` (my trust decisions and the fix).

## November 25 — Signing only for what happened

Before submission, I needed to replace the remaining placeholders with accurate attribution. Claude chat drafted the initial specification, wrote the Claude Code prompts, reviewed reports, and recommended changes. Claude Code implemented the code, wrote every test, and ran the live operations. I made the project decisions and completed the manual work described in the report, with AI assistance disclosed.

I also kept the “Not checked” list. Passing tests and clean links do not erase those limits. My sign-off should state what I checked and what I am willing to trust, without claiming that I personally wrote tests or ran commands that Claude Code handled.