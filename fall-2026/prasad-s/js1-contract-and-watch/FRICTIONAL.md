# FRICTIONAL.md

### 2026-10-25 — A board I never downloaded
- Tried: starting v0.2 from a contract draft made with Muse.
- Happened: the draft named Vercel as the board and cited a check, files and fingerprints that were never made. I asked where Vercel came from — it was nowhere in my work.
- Checked / changed / learned: I threw the draft out, downloaded the Stripe board myself and ran the checks myself. A citation is not evidence unless I produced it.
- Muse's part: the Vercel draft — rejected, and replaced wholesale.
- Trace: 5cd4c28; the evidence note in CONTRACT §1.

### 2026-10-25 — Locations that matched nothing
- Tried: running C2 with the persona's original locations.
- Happened: my check showed none of the 35 Stripe PM postings would pass C2. The rule would have found nothing, and looked broken doing it.
- Checked / changed / learned: I chose New York, NYC and Remote after seeing Stripe's own spellings, before any labeling. A persona has to be written against the board's spellings, not my assumptions.
- Claude's part: proposed the location check and the three values, including the warning not to use "NY" (it would match "Sunnyvale") — accepted after I saw Stripe's spellings myself.
- Trace: 5cd4c28; CONTRACT §1.

### 2026-10-26 — Four answers against the old persona
- Tried: working out the expected answers for the rule cases.
- Happened: R05, R07, R12 and R13 were worked against the old persona, after the locations had already changed. While fixing it, stale copies were uploaded three times.
- Checked / changed / learned: Claude.ai pointed the mismatch out; I checked each of the four myself, and the answers changed where the list changed. Hand-written tables catch spec drift before any code exists — provided the file on disk is the version I think it is.
- Claude's part: the flag — accepted; typing the corrected file — accepted as typing, with the answers checked by me.
- Trace: 5969e44; the note in rule_cases.json.

### 2026-10-26 — The rule that got deleted in editing
- Tried: tightening the contract in the v0.2 edits.
- Happened: the required-fields rule was removed during those edits, silently — nothing announced that it was gone.
- Checked / changed / learned: my refusal cases P05–P07 exposed it, because personas that should be refused would have run. Restored in v0.3, and I set the skills minimum to 2 so that boundary is decided, not implied.
- Claude's part: Claude.ai's earlier instruction that I could delete the "e.g." examples contributed to removing the rule; the grep that confirmed it was gone was Claude.ai's; it helped word the restoration — accepted. The skills minimum was my decision.
- Trace: 13f40e9.

### 2026-10-27 — Run 1 failed on SSL, and the contract held
- Tried: the first attempt at Run 1.
- Happened: it failed on SSL certificates, and no state.json was written.
- Checked / changed / learned: the v0.3 rule for a failed run did what it was written for — on a real failure, not a constructed one. After running Python 3.13's Install Certificates step, the next attempt was still a baseline.
- Claude's part: Claude Code's implementation followed the contract here — accepted.
- Trace: evidence/run1_attempt1_failed_ssl_2026-10-27.txt; 9078be3.

### 2026-10-28 — The draft that got committed
- Tried: committing the labeling protocol.
- Happened: the unsaved draft version was committed instead of the final wording.
- Checked / changed / learned: fixed before any labeling began, so the order the experiment depends on was never at risk.
- Claude's part: the protocol skeleton — accepted; Claude Code's report flagged the file as modified, and I confirmed the difference with git diff.
- Trace: a9a6db6 → fd5302d.

### 2026-10-28 — Leftover &nbsp; in the cleaned text
- Tried: viewing the first development posting with the viewer.
- Happened: the cleaned content still showed "&nbsp;". Stripe escapes some characters twice, and my rule unescapes once, as CONTRACT §4 says.
- Checked / changed / learned: the code and my hand labels use the same cleaned text, so they stay consistent. Whether a leftover &nbsp; ever glues two words together and hides a skill was not tested — unresolved, and listed under "Not checked" in my sign-off.
- Claude's part: pointed it out when the viewer output came back — accepted as a known limit.
- Trace: tools/show_posting.py; CONTRACT §4.

### 2026-10-28 — Run 2: 29 new, and a recount that failed first
- Tried: verifying Run 2's new count independently.
- Happened: 29 new, all not_relevant, some of them with old ids. The recount script first failed on the UTC file name.
- Checked / changed / learned: the script was fixed and I recounted — 29, identical. "New" means new to the agent; why the old-id postings were missing on day one was not checked.
- Claude's part: the recount script and its fix were Claude.ai's; I ran it on my saved files, and the 29 is from them.
- Trace: evidence/run2_recount_by_me_2026-10-28.txt.

### 2026-10-29 — "Reuse," built against my plan
- Tried: having Claude Code build the save tool according to chat_plan.md.
- Happened: Claude Code misread my plan's complete sentence ("…reply: no") as cut off, asked me, and the "Recommended" option chosen in that question was reuse — the opposite of my plan.
- Checked / changed / learned: Claude.ai spotted the mismatch, and I had the reuse build reverted. My plan is the spec; clicking a "Recommended" option can quietly override my own written plan.
- Claude's part: the reuse build — rejected and reverted; the spotting of it — accepted.
- Trace: 1bf0301 ("no reuse, per chat_plan.md").

### 2026-10-29 — Clipboard saves, and the helper I turned down
- Tried: saving the chat replies by hand, by copy and paste.
- Happened: I pasted the tool's summary into Claude once; saved a command instead of a reply twice (Run 2's 8154295, and sampling's 6348471_r1); made a wrong save for 7202630; and deleted save_reply.py by accident in the same stretch of work.
- Checked / changed / learned: every bad save was caught, by its first line or by the no-overwrite refusal, and redone before any commit; save_reply.py came back with git checkout. My fix is now routine: pbpaste | head -1 before every save.
- Claude's part: a batch-chat helper tool, proposed to automate this — rejected as too complex. The manual check is simpler, and I can audit it.
- Trace: no commit contains the bad saves — they were caught first; the corrected saves are in a4ff13d (sampling) and fc69190 (Run 2 replies).

### 2026-10-29 — My first label was wrong; my reasons stayed generic
- Tried: hand-labeling the development set, starting with 6348471, "Product Marketing Manager."
- Happened: my first call was C1 true. A method reminder made me re-check the substring: "Marketing" sits between "Product" and "Manager," so C1 is false. Separately, 6 of my 10 development reasons say only "a target title" — generic.
- Checked / changed / learned: I changed the first label to false before the set went on. I chose to leave the generic reasons as written, and disclose that here rather than quietly improve them after the fact.
- Claude's part: the method reminder — accepted; the suggestion to make the reasons specific — rejected. The reasons stand as written.
- Trace: 6126445; hand_labels_development.json.

### 2026-10-30 — The revision met its prediction, and I can't show it caused it
- Tried: one change only — option C — with a prediction written and committed before any revision chat.
- Happened: development went 9/10 to 10/10, and the targeted failure appeared in none of the 20 revision replies. Held-out scored 10/10 under both prompts, so the two cannot be separated there.
- Checked / changed / learned: the predictions were met, but whether C caused the improvement is unresolved — 0 failures in 20 replies happens about 16% of the time by chance, assuming the replies fail independently. A met prediction is consistency, not causation.
- Claude's part: found the pattern (whole-list rejections on failed conditions) and listed options A, B and C — accepted as a list to choose from; the choice, the reason and the prediction were mine.
- Trace: 323d2b6; revision_decision.md.

### 2026-10-30 — Two drafts claimed more than the record
- Tried: writing up the conclusions and the driver's seat.
- Happened: my conclusions overclaimed in four places — a causal opening, "the targeted failure is gone," "nothing else moved," and the sampling pattern stated as a rule. Separately, three driver's-seat rows gave me credit for work that was Claude's.
- Checked / changed / learned: the four claims were narrowed to what the data shows, and the rows corrected so the credit matches who did the work. Drafts — mine or Claude's — still get read against the record before they go in.
- Claude's part: flagged the four overclaims in my conclusions and supplied corrected wording — accepted; drafted the driver's-seat rows, then flagged three that credited me for its work and drafted the correction — accepted after I checked it.
- Trace: the conclusions of the sampling and prompt-experiment reports; the driver's seat table in README.md.

---