# FRICTIONAL.md — Job-Search Agent 3

These entries were drafted by Claude.ai from my checkpoint log and the commit history, at my request. I checked each one and edited it in my own words.

### 2026-11-15 — Commands written for one folder, run from another
- Tried: create the JS3 folder from my terminal.
- Happened: I ran a command written for the repository root from inside prasad-s/, and made a nested copy of the path. Later, root-relative git paths failed from inside the JS3 folder.
- Checked / changed / learned: find showed only empty folders, so rmdir removed them safely. A command's folder is part of the command; from then on, every command named the folder it runs from.
- Claude's part: Claude.ai's first instructions assumed the root without saying so clearly; it gave the undo steps.
- Trace: JS3-CP1.

### 2026-11-15 — The template went into the first commit
- Tried: commit FILTER.md v1.
- Happened: I committed it with only the five decision blanks filled; the rest was still Claude.ai's bracketed prompts.
- Checked / changed / learned: it was not pushed, so I undid it with git reset --soft and recommitted with every bracket replaced (a grep for "[" printed nothing). A skeleton's prompts are not my words, and the commit should hold only mine.
- Claude's part: Claude.ai's message made the five decisions look like the whole job. FILTER.md's changelog credits its layout.
- Trace: JS3-CP1.

### 2026-11-15 — The counts ran before the tooling was committed
- Tried: commit seal_draw.py, then run counts.
- Happened: I staged it, ran counts, and committed afterwards.
- Checked / changed / learned: git diff showed no change since staging, so counts ran on exactly the committed script, and the CP2b message says so. The order is the evidence: commit, then run.
- Trace: JS3-CP2b.

### 2026-11-15 — The seed's commit hash won't survive the rebase
- Happened: git reported that my branch had diverged from the shared main. Rebasing before the push gives JS3-CP1 a new hash, and the seal's seed is CP1's first 8 characters.
- Checked / changed / learned: SEAL.md §5 records the full hash as first committed, and my documents cite checkpoints, not hashes. A commit hash is only stable after the push.
- Claude's part: Claude.ai spotted it from the "diverged" message.
- Trace: JS3-CP2c; SEAL.md §5.

### 2026-11-16 — I pasted the sealed labels into the review chat
- Tried: ask Claude.ai how to tell when §5 does not cover a case.
- Happened: I pasted all 30 held-out labels, with quotes from the postings, before their hash was committed. Claude.ai helps choose the filter changes, so the set could no longer measure them blind.
- Checked / changed / learned: I retired the set to development data and drew a replacement from the next ranks under the same seed (SEAL.md §8). Nothing from the new set went into a chat. A seal is only as good as the habits around it, and the rule has to be at the top of the instructions, not in the middle.
- Claude's part: Claude.ai had put the don't-paste rule inside a long message; it proposed the replacement design.
- Trace: JS3-CP3b to CP3f.

### 2026-11-16 — Three held-out ids came out of a check message
- Happened: label_view's check printed the board key and id of each missing row. I pasted that output while fixing my file, so three ids from the new set reached the chat.
- Checked / changed / learned: the tool's messages now never print an id or repeat an argument, and tests prove it. SEAL.md §8 records the three ids: ids only, no titles, no labels. A tool's error messages are output too.
- Claude's part: Claude.ai had told me the check's messages were safe to paste.
- Trace: JS3-CP3g.

### 2026-11-16 to 18 — Edits that weren't saved before the commit
- Happened: SEAL.md v1.3's fixes, and the first audit/recheck_notes.txt, were committed without my edits in them; a grep and the line count showed it.
- Checked / changed / learned: SEAL v1.4 and JS3-CP6h added them, each saying when. git diff before git add, every time.
- Trace: JS3-CP3c, CP6h.

### 2026-11-17 — FILTER v1 kept nothing
- Happened: JS2's rule, unchanged, judged 1,248 postings and kept none. 23 of the 27 postings with a PM title and a workable location named none of the five skills, while 38 non-PM closest calls had 2 or 3 of them.
- Checked / changed / learned: the persona's skill words, Python and SQL, are engineering words. PM postings rarely list them, so the gate the persona implied rejected the very jobs it was for.
- Trace: JS3-CP5d; AUDIT.md §7.

### 2026-11-18 — I read Staff PM as an ordinary PM title
- Happened: my blind audit verdicts marked 12 Staff Product Manager postings worth while marking Senior ones not_worth, so 22 "wrong rejects" were mostly my misreading. On PM ladders, Staff sits above Senior.
- Checked / changed / learned: I kept §5 as written. Pass 2 re-read under it (19 changes), and pass 3 fixed an off-by-one edit and two roles that skills had rescued. Every change is in audit/recheck_notes.txt. The labeler and the filter made the same mistake: it is the false friend the audit found, "Product Manager" inside "Staff Product Manager".
- Claude's part: Claude.ai pointed out the inconsistency and the ladder; the decisions were mine.
- Trace: JS3-CP6d to CP6j; AUDIT.md §7 and §8.

### 2026-11-19 and 20 — The years at the bottom of the posting
- Happened: row 62 (7+ years), and held-out postings 15 (8+ years) and 24 (10+ years, and a Staff title), all had their requirement under "Minimum requirements" near the end of a long posting. I had written "no years stated" for each. The years rule found row 62; the reveal's re-check found 15 and 24.
- Checked / changed / learned: pass 4, and the held-out re-check (SEAL.md §10). The viewer wraps text, so a search for "5+ years" can miss a phrase split across lines; joining the lines fixed that. For a PM role, the experience line decides the level, and it is often the last line.
- Trace: JS3-CP7e, CP11b.

### 2026-11-20 — Is "5+ years preferred" a requirement?
- Happened: §5 did not say. I decided that preferred years do not fail level (FILTER.md v2.1), before the held-out scoring. That made audit row 31 worth (pass 5) and exposed F10, which counts preferred years: v2 missed row 31 and, on the held-out set, its one worth posting.
- Checked / changed / learned: a standard can be incomplete. Deciding it in the open, before scoring, keeps the measurement honest even when the answer costs the filter.
- Claude's part: Claude.ai leaned the other way and laid out what each choice would change; the call was mine.
- Trace: JS3-CP11b to CP11e; MEASURE.md §2.

### 2026-11-16 — Claude Code reached for the vault
- Happened: while building label_view, Claude Code included ls ~/js3-vault in a check command, which the prompt forbade. Its permission check blocked the command before it ran.
- Checked / changed / learned: nothing in the vault was read. The boundary held because something other than the instruction enforced it, and that is the kind of boundary to rely on.
- Claude's part: Claude Code reported the slip itself.
- Trace: JS3-CP3a.

### 2026-11-20 — The client wasn't where I expected, and the protocol had moved
- Happened: there is no claude command on this Mac, because I use the desktop app. So I registered the server through an uncommitted .mcp.json, and CONTRACT v0.12 corrects v0.11. Claude Code then probed with server/discover (2026-07-28), got "method not found", and fell back to the handshake my server speaks. The filesystem server's latest version needed Node 24 and crashed.
- Checked / changed / learned: interoperability is something you observe, not something a version number promises.
- Trace: JS3-CP10b to CP10d, CP12a.