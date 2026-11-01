# Action-surface comparison (Chapter 3)

**The task:** decide whether one Stripe posting is relevant to the fictional persona Jordan Lee, and say why, under `prompts/judge_v1.md`. The same task was done three ways.

| | 1. Paste one posting into a chat | 2. Give Claude a file to read | 3. Let an agent fetch and write its own state |
|---|---|---|---|
| How it ran | `claude -p` with the posting's requirements text and the persona pasted into the prompt; `--tools ""` | `claude -p` started in a temp dir holding `posting.json` and `persona.json`, told to read them; `--tools Read` only | `claude -p` in a temp dir with `--tools WebFetch,Write`, told to fetch the Stripe board itself and write `state.json` |
| Can read | Only the text pasted in | Any file the Read tool can reach from its working directory | Any URL WebFetch reaches, plus files |
| Can write | Nothing | Nothing | Files (its own state, and anything else in reach) |
| Can send | Nothing | Nothing | HTTP requests to any host it chooses |
| Authority needed | None beyond the chat | Read access to a folder | Network access and write access; would need an allow-list and a sandbox to be safe |
| What could go wrong | Wrong text pasted; posting truncated by hand; no record unless saved | Reads the wrong file or more files than intended (e.g. a real résumé nearby) | Fetches hosts off the allow-list (including `absolute_url`); writes state in a different shape; silently drops or invents postings; no byte-exact raw evidence; each run costs a model call for work code does deterministically |

## Evidence

<!-- generated:start -->
Ran 2026-11-01T02:59:15+00:00 UTC on posting 8113100 (Data Scientist, Fraud), model claude-sonnet-5-5. Full raw outputs are in `evidence/action-surface/`.

- **1-paste** (is_error=False · permission denials: 0; files in cwd afterwards: []): {"verdict": "not_relevant", "justification": "Role requires BS with 4-8 years of data science experience plus fraud/risk background; candidate has a bachelors and 2 years. Toronto is not a preferred city and the posting doesn't indicate remote, despite title matching data scientist.", "cited_resume_fields": ["years_experience", "highest_degree", "preferred_cities"], "cited_posting_fields": ["conte
- **2-file** (is_error=False · permission denials: 0; files in cwd afterwards: ['persona.json', 'posting.json']): {"verdict": "not_relevant", "justification": "The posting's minimum for a BS is 4-8 years of experience, and the candidate has 2 years with a bachelors. It also requires fraud or risk experience, which the candidate's skills don't show. Toronto isn't in preferred_cities, and the posting doesn't mention remote work.", "cited_resume_fields": ["years_experience", "highest_degree", "skills", "preferre
- **3-agent** (is_error=False · permission denials: 1; files in cwd afterwards: []): I couldn't write `state.json`, and I got the job details from a truncated fetch, so this is only partly done.  **File not written.** Both Write attempts failed: - The first used the short working-directory path `C:\Users\SUHASK~1\...`. The harness flagged it as a suspicious Windows path and needed manual approval. - The second used a long path I guessed (`C:\Users\SUHASK-1\...`). That was wrong. T
<!-- generated:end -->

**What the three runs showed (2026-10-31, 22:59 ET, posting 8113100 "Data Scientist, Fraud"):**
- Surfaces 1 and 2 both returned valid JSON with `not_relevant`. They cited the same reasons: BS + 4–8 years required, Toronto not preferred.
- Surface 3, the agent with tools, did not finish the task:
   - It fetched the board through WebFetch's 100,000-character chunks, which pass through a summarizing model. It assembled **about 650 ids against the 745 on the board** and said itself that this "isn't a raw download".
   - Its two attempts to write `state.json` both failed: one was denied permission (logged in `permission_denials`), and the other used a path it guessed. No state file was written.
   - It judged the posting from the title and metadata only ("I only saw the title and metadata, not the job description") and called it "marginally relevant".

This is the failure the contract's design avoids: a state file built from a summarized fetch would silently miss about 95 postings, and every later run would mis-report them as new.

## The choice: least autonomy that suffices

The agent splits the task:
- **Code holds every authority that touches the outside world.** The fetch is allow-listed, the raw board is saved byte for byte, and the state is written atomically, all by ordinary Python that the tests check.
- **Claude gets surface 1 and nothing more.** It receives the prepared text on stdin, with tools disabled (`--tools ""`), from an empty temp directory.

Why this is enough:
- Judging relevance needs only the posting text and the persona fields, and code can supply both exactly.
- Surface 2 adds file access, which Claude doesn't need for this task. It's also the one way a nearby real résumé could leak into a prompt.
- Surface 3 hands Claude network and write authority. The contract forbids that (`Refuses`: no fetch off the allow-list), and it would make the state file a model's output rather than a record anyone can recompute.

The cost of this choice: the agent can't follow a link or read a page the code doesn't fetch, so it never sees the posting's own web page (`absolute_url` is recorded, never fetched).
