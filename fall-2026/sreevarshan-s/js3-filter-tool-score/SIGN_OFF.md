# Sign-off — Job-Search Agent 3

## Checked
- Filter runs on all 1779 postings and produces filter_results.json: by running js3/run_filter.py myself and inspecting the output counts
- FILTER.md was committed before any filter code: by git log showing 836b5ab before 01343cc
- Reject audit: 40 postings judged by me based on title, location, and metadata; verdicts in output/audit_sheet.md
- MCP server responds correctly to initialize, tools/list, and tools/call: by running js3/mcp_client.py and reading output/mcp_transcript.txt
- 60 tests pass on a clean run: by running pytest myself

How: by hand for verdicts / by running commands myself / by reading output files directly

## Not checked
- Whether Greenhouse's or Lever's terms of service allow automated polling at this frequency
- Whether the 47 passed postings are still live (the raw data is from 2026-11-06)
- Whether any passed posting actually sponsors OPT visas (no posting states this; all sponsorship claims are insufficient)
- Whether the MCP server behaves correctly under concurrent connections (it is single-threaded)

## Not claiming
- This agent does not apply to any job, send any email, or log in anywhere
- The reject audit sample cannot measure the false-reject rate for all 1732 rejects
- The scorer's weights are hand-set guesses, not fitted on labeled data
- A score of 100 does not mean the posting is relevant to Priya Nair — it means the title matched a role word

## Driver's seat

| Task | Claude does | I do | Why judgment stays mine |
|---|---|---|---|
| Fetch postings | Run the loop, save raw JSON | Approve the board list and budget | I decide which companies are worth targeting |
| Filter | Apply FILTER.md rules to titles | Write FILTER.md, review every rule | The rules encode my judgment about what is relevant |
| Reject audit | Sample and format the sheet | Read every row and record a verdict | A verdict I didn't make isn't evidence |
| Score | Compute the weighted sum | Set the weights, interpret the output | The weights are my assumptions |
| Shortlist | Rank by score | Review the shortlist before acting | I decide what is worth my time |

Signed: Sreevarshan Sathiyamurthy, 2026-11-24
