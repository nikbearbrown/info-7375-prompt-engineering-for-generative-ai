# Sign-off — Job-Search Agent 3

**Drafted by Claude Code, 2026-11-26.** The hand labels are Saloni's (AUDIT.md §2). The last
line stays WITHHELD until Saloni reads this and signs it herself.

```text
Sign-off — Job-Search Agent 3

Checked:      - the filter reads FILTER.md and nothing else; every role word has a reason line;
                config/sources.json matches FILTER.md §4 (tests/test_filter.py TestFilterDocument)
              - whole-word matching: "HTML Email Developer" is not an ML job; wrong version 1
                (substring) keeps it and is caught (test_wv1_substring_match_is_caught; also
                live through the MCP server, session A)
              - count ranking without cap or veto puts a senior posting first; wrong version 2
                is caught (test_wv2_count_ranking_is_caught)
              - silence is not support: an empty posting cannot support a years claim; wrong
                version 3 is caught (test_wv3_absence_as_support_is_caught)
              - a failed or empty board is reported as not seen, never as "nothing relevant"
                (tests/test_collect.py; the live run had 3/3 boards, so this is fake-only)
              - the MCP server opened no socket and started no process, and wrote only its own
                transcript, in session A (audit hooks, out/mcp/audit-own-*.jsonl)
              - what Claude Code sent my server, call by call (server transcript, session B),
                and that its own summary of those calls was wrong
              - candidate switches C2/C3 are off in v1.0 and do what they say when on
                (TestCandidateSwitches)
              - the exact interval code: 0 of 35 gives an upper bound of 1 - 0.025^(1/35)
                (tests/test_stats.py)
              - the reject audit: 7 of 35 judged random rejects wrong, by my hand labels (exact 95% interval 8.4% – 36.9%)
How:          - wrong versions and evidence rules: tests written by Claude Code in the same
                session as the code, NOT before reading it
              - false friend: by recomputation (code counted the boilerplate in 634/634
                Anthropic postings); by hand: `training` matched 35 dev rows, which I split 16 worth / 19 not: it does not separate the jobs I want
              - audit and held-out verdicts: by hand, blind to the filter's decision; 9 dev rows
                re-answered after seeing the error list (2 changed, labels/relabel_log.csv)
              - MCP behaviour: by observation (audit hooks, wire transcripts), not by reading
                the server's description of itself
Not checked:  - run-to-run variation of Claude: each variant ran once
              - recall of the whole pipeline: 35 random rejects can bound the reject error
                rate only loosely (0/35 still allows up to 10%)
              - whether `claude mcp serve` asks permission before Bash or Write; I did not call them
              - the evidence checker on plurals and synonyms ("visas" vs "visa"), and on claims
                that argue against a posting
              - any second collection: one snapshot, one afternoon
              - each company's site terms beyond the APIs being public
Not claiming: that a kept posting is worth Priya's time; that the filter misses almost nothing;
              that the agent's numbers are rates for all postings (every number from a sample
              is a sample estimate); that the tool annotations are true for any server but
              mine, and for mine only on the calls observed; that anything was trained.
Signed or withheld: WITHHELD — pending Saloni's labels and review (Claude Code draft, 2026-11-26)
```

## Driver's seat

| Part | What Claude should do | What I should do | Why that part stays mine |
|---|---|---|---|
| The filter's words and weights | propose them with reasons; find false friends by counting | decide which rules go in, at what version | the filter decides what I never see. A rule I didn't choose is a blind spot I didn't choose. |
| Collecting and scoring | run the GETs, keep the raw bytes, compute the record | check the run was complete before trusting "nothing new" | — |
| The reject audit | draw a seeded blind sample; compute errors and intervals from my labels | label every row myself, without the filter's answer | the labels are the ground truth the numbers are measured against. If Claude labels them, it marks its own homework. |
| Claims on the shortlist | write claims with quotes; label them mechanically | read the quotes and disagree where the checker is wrong | "supported" means the quote exists. Whether the claim is a reason to apply is a judgement about me. |
| Tool servers | build and exercise them; record transcripts | decide what each server may see and do | trust is a decision about risk to my files and data, not a fact the server can declare |
| Whether a posting is worth my time | summarise the posting and its evidence; say "I cannot tell" when the text doesn't say | decide | it depends on what I want from my career, what I'm willing to stretch for, and things that are in no posting. Claude agreed with the filter more once it could call it (SCORE.md, J3), so its "worth it" can inherit the filter's blind spots. |
