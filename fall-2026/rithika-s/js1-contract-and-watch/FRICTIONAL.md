# FRICTIONAL — Job-Search Agent 1

## 2026-10-30

### Choosing the persona
- Compared all four fictional personas from the Reallocation Engine's
  search/examples/ (Aarav, Maya, Priya, Rohan) with Claude (claude.ai).
- Claude first recommended Aarav (backend/platform); after I shared Priya's
  and Rohan's files it changed its recommendation to Priya.
- I chose Priya Nair (AI/ML Engineer, Data Engineer). Reason: AI/ML and data roles are my own field, so I can label those postings by hand with confidence. Her skills (Python, SQL, Databricks, MLflow, LangGraph) appear word-for-word in postings, and her security-clearance exclusion gives clear "not relevant" cases.

- Rejected Rohan: his skills list is so broad almost any SWE job would match,
  and his exclusions are "none", so few postings would be "not relevant".
- Noticed Priya has no PyTorch/TensorFlow, which many ML postings ask for.
  This will force real decisions in my rule.

### Choosing the job board
- Tested three Greenhouse endpoints in the browser (~11:37–11:41):
  databricks, anthropic, scaleai. All three returned JSON.
- Rejected Databricks: every posting ends with an "About Databricks"
  paragraph that mentions Databricks and Unity Catalog, both on Priya's
  skills list. A keyword rule would mark every job relevant, including
  sales roles. Some postings were also in Japanese.
- Chose Scale AI: English postings, US locations, mix of engineering and
  non-engineering roles, and it likely has clearance-related postings that
  test Priya's "no security clearance" exclusion.
- Scale AI board total: 169 postings ("meta": {"total": 169}).
- Confusion I had: the endpoint looked like raw text with no Apply button.
  Learned it is the JSON data feed meant for programs; each posting's
   "absolute_url" points to the normal human page. I opened one and confirmed it is the same job with an Apply button.

### Setup mistake and fix
- Typed a bare `cd`, which took me to my home folder. `git pull` failed
  ("not a git repository") and `mkdir` created fall-2026/... in my home
  folder instead of the course repo (~11:58).
- Removed the empty folders with `rmdir` (it only deletes empty folders).
- Ran `mdfind -name week-01-video` and found TWO clones of the course repo.
  Checked both with `git log -1`: ~/info-7375-... had my latest commit
  (Oct 21), the Downloads copy stopped at Sep 25. Using ~/info-7375-...
- Downloaded Priya's resume.example.json from the professor's repo with
  curl and verified it with a one-line Python check: printed
  "Priya Nair priya.nair@example.com".
- Created .gitignore (blocks resume.json, *.real.json, .env, caches) before writing any code or the contract.


## 2026-10-31

### Contract and setup
- I asked Claude to draft the contract wording from my decisions
  (Priya, Scale AI, separate target file), and SOURCES.md says so.
  Committed contract, persona, target, and .gitignore together before any code (19d72c7).
- VS Code saved `target.example.JSON` and `CONTRACT.MD` with capital extensions.
  Renamed them via a temporary name, since macOS ignores a case-only rename.
- A grep for leftover `[` placeholders in this file found two; I filled them before committing.

### Building with Claude Code
- Claude Code asked to import `AGENTS.md` from the repo root, outside my folder. I declined.
- The terminal CLI showed "Login expired" and "API Usage Billing". I used the desktop
  app (Northeastern seat), later re-logged the CLI, and the header showed "Claude Enterprise".
- Claude Code reported 42 passing tests. I ran them myself ("Ran 42 tests ... OK") and
  confirmed with `git diff` that CONTRACT.md and the data files were unchanged (aeb018b).
- Accepted its 11 interpretations. Known limit: whole-word matching means "clearances"
  does not trigger the "clearance" exclusion.

### Runs
- First live fetch failed with CERTIFICATE_VERIFY_FAILED (python.org Python 3.14).
  Fixed it with Install Certificates.command, not by turning off HTTPS checks. The agent
  saved nothing on failure.
- Live baseline at 14:36 UTC: 170 postings, 0 new. My browser showed 169 yesterday,
  but that was a browser check, not a run.
- Started Claude Code in my home folder by accident and declined to trust it.
- In auto mode, Claude Code created `tools/make_seeded_earlier.py` from my paste and ran
  a command without asking. I switched auto mode off after that.
- First seeded second run stopped on a report-filename collision (two runs in the same
  second). Re-ran it: 7 new, 2 relevant by rule. The rule and Claude disagreed on
  "Senior/Staff ML Research Scientist", which showed the rule's title gate is too broad.
- Forgot to commit the runs; noticed when `git log` lacked them, then committed (d14f6fe).
- Live second run at 17:29 UTC: 0 new, identical SHA-256. The board did not change.

### Labeling
- Changed the proposed labeling rule: up to 2 years of experience with internships
  counting, a no-sponsorship condition, and data science/analytics roles (9cf0d33).
  My first attempt committed a placeholder line (6cfffa2).
- The first random sample (a40d97b) had almost no plausible postings. Re-sampled,
  stratified, before any labels (065d568).
- First labeling attempt (`tools/label.py`): I marked a TS/SCI-required DevOps job and a
  medical fellowship as relevant, and typed a condition number into a note. Claude pointed
  out these contradicted my rule. I reset the sheet and switched to `label_v2.py`, which
  asks each condition in turn.
- The first posting was in London. The persona can only work in the US, so I added a
  US-location condition before saving any label.
- Claude flagged 8 labels as inconsistent with my rule. I re-checked those postings and
  corrected them before any prompt ran (2b7d3ce, then cb39cee).

### Claude trials
- Sampling: the same verdict in all 4 runs for each of the 5 postings; 16/20 matched my labels.
- Dev: both prompts 9/10. Held-out: baseline 10/10, revision 8/10.
- Claude's reasons said the New Grad job requires a Fall 2026/Spring 2027 graduation and
  the Frontier Agents job requires 4+ years. I checked the raw text
  (`label_audit_evidence.txt`): both were true. One was a gap in my rule; the other was my
  labeling error (my note said "0-1 yrs"). I kept the pre-registered scores and added a
  separate post-hoc section (64194b7).

### Action surface
- Twice I saved my own copied command instead of Claude's reply: copying commands
  overwrote the clipboard. Caught it by checking the file and switched to pasting into TextEdit.
- In manual mode, Claude Code read the file without asking. A macOS "Data Access
  Blocked" notice appeared; I did not check what caused it.
- The README was first committed unsigned, because a `#` comment broke the `open` command.
  Signed it in the next commit (0561c57).

### Accepted, modified, rejected
- Accepted: Priya, Scale AI, the target file, the contract draft, Claude Code's
  implementation, stratified re-sampling, the condition-by-condition labeling tool,
  and the report drafts (after reading them).
- Modified: the labeling rule (my four changes); Claude's first persona suggestion
  (Aarav), which I did not take.
- Rejected: the external AGENTS.md import, trusting my home folder, auto mode, and
  disabling certificate checks.

### Unresolved
- Report-filename collisions; the validator accepts field names that don't exist; the agent's
  rule ignores location, sponsorship, seniority, and graduation windows; the macOS notice;
  Claude's verdict on posting 4720573005 changed between occasions.

### In my own words
- What surprised me most: Claude's reasons caught two mistakes in my own labels:
  a graduation-window requirement my rule never considered, and a "4+ years"
  requirement I had noted as "0-1 yrs". I had treated my hand labels as the ground
  truth, but the score was only as good as my labels. I only accepted Claude's claims
  after checking the raw posting text myself. I was also surprised that four identical
  answers in a row still did not mean the answer was right.
- What I would do differently next time: write the labeling rule more completely
  before starting (location, graduation windows, required vs. preferred experience),
  and label more slowly, opening every posting instead of relying on the excerpts.
  I would also turn off Claude Code's auto mode before the first prompt, not after it
  had already written a file and run a command without asking.
- What I still don't fully understand: why the same baseline prompt said "relevant"
  for the Frontier Agents posting in one `claude -p` run but "not relevant" in the chat
  and file runs, when my sampling runs were perfectly consistent. I also don't know
  what sampling settings `claude -p` uses, or what triggered the macOS "Data Access
  Blocked" notice.
