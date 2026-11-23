# FRICTIONAL — Final Project Film
**Swathi Baba Eswarappa | INFO 7375 | November 22, 2026**

## 1. I had trouble logging into Claude Code

When I first opened Claude Code to start working on my film, I noticed that it was showing API Usage Billing and a 401 error instead of my university subscription. It was also running in auto mode, which I didn't want because I wanted to review and approve what Claude Code was doing.

I used `/login`, selected the Claude account with subscription option, and logged in through my Northeastern account. After that, it showed Claude Enterprise. I also switched to manual mode using Shift+Tab.

I decided to keep manual approval throughout the process instead of allowing Claude Code to make decisions automatically. Once I fixed the login issue, I was able to continue.

**Evidence:** `BUILD-PROMPT.md`

## 2. I realized I had chosen the wrong narration voice

Initially, I selected `am_michael` because Claude Chat's notes said my pitch film used that voice. But when Claude Code checked the original pitch film during Phase 1, it found that although the pitch film had started with `am_michael`, the final version actually used `af_heart`.

Since I wanted both films to sound consistent, I decided to change the voice to `af_heart`. Claude Code suggested keeping `am_michael` because it was already in the beat sheet, but I chose to change it.

This was Claude Chat's error, and checking the previous project helped me catch it before rendering the new film.

**Evidence:** `build/beat_sheet.orig.json` and `beat_sheet.json`

## 3. My project plan needed more corrections than I expected

Claude Chat helped me prepare the narration and project appendix, and I reviewed them with ChatGPT before approving anything.

During the review, we found several problems in the technical plan. For example, the recall calculation included employers that didn't have sponsorship records, and the independent checker wasn't strong enough to catch a case where the agent matched a posting to the wrong employer.

We also found that H-1B1 and E-3 records needed to be separated from H-1B records, the confidence bound wasn't appropriate for our selected test sample, and the employer aliases could accidentally expose information from the held-out dataset. Another issue was that the Department of Labor files are cumulative, so we needed a way to avoid counting duplicate records.

I asked Claude Chat to correct these issues in two rounds rather than accepting the first draft. I reviewed the revised plan and made the final decisions about the voice, how to handle Certified-Withdrawn cases, the 20/40 employer split, and the evaluation targets.

Some references are still verified only through search results or university websites, and the FY2026 LCA record layout still needs to be checked when I implement the final project.

**Evidence:** `PLAN-APPENDIX.md`, Sections 6, 7, and 9

## 4. I didn't want Claude Code running Git commands

Before starting the film, I wanted to make sure Claude Code wouldn't accidentally change my existing pitch film or course repository.

During Phase 1, Claude Code found that the original build script used `git fetch` to get the upstream quality gates. It had also run a read-only `git status` in the toolkit while checking the setup. My prompt only banned Git commands that change something, so this was allowed, but Claude Code reported it. After that, I banned all Git commands during production.

Instead, Claude Code used the five upstream gate scripts from toolkit commit `519fcbb` (October 12), which were already in my Mode Build folder. It checked those scripts against the toolkit's own history using file hashes, without fetching anything.

I approved this because it allowed us to run the available checks without changing the toolkit repository.

The limitation is that any newer upstream gates weren't included. Also, GATE MASTER couldn't run its duration check because `clock_check.py` wasn't available in that local version.

**Evidence:** `build/run_upstream_gates.sh` and `qc_reports/upstream/MASTERCHECK.md`

## 5. Some quality gates failed, and I had to decide how to fix them

After rendering the film, not everything passed on the first attempt.

Gate A initially crashed because of a problem in Claude Code's timing code. That was fixed in `scene.py`, not in the gate. After that, Gate A found an issue in B11 because the shapes weren't changing, and Gate T flagged B08.

Claude Code proposed fixes and asked for my approval.

For B08, I accepted the suggestion to shorten the green line slightly so it no longer touched the button and the card, which made Gate T read all three as one block of text. For B11, Claude Code suggested adding a new "not yet measured" label, but I didn't want to introduce additional text that wasn't part of my approved narration and visual plan. I asked it to keep the dashed amber marker without adding those words, since the screen already said "PROPOSED TARGETS — NOT RESULTS."

The first B08 fix caused another Gate A crash, so Claude Code corrected it and rendered B08 again.

After these changes, all the quality gates passed. Gate B still reported four warnings, including three intentional strike-throughs and one footer close to the safe-area edge in B03. I kept those documented rather than pretending there were no warnings.

This was one of the parts where I had to make decisions instead of just accepting everything Claude Code suggested.

**Evidence:** `qc_reports/gateA_static_scene_check.txt`, `qc_reports/upstream/TYPECHECK.md`, and `BUILD-PROMPT.md`

## 6. Claude Code fixed some problems without stopping to ask me first

While building the film, Claude Code fixed several rendering problems: zero-frame clips in B06, B08, and B10, the author tag losing its spaces (caught by the label gate), the B01 card pile and the B02 beam overlap, and some long end holds. I approved each edit in the manual-mode permission prompts, but Claude Code did not stop and ask me in words first. My safeguard said that after a gate failure it should report and stop before changing anything, and the author-tag fix came from a label-gate failure.

These changes didn't affect the narration, labels, or project numbers. I reviewed the final film and contact sheet and accepted the changes afterward.

One thing I couldn't fully verify was a timing-helper change made after the 4K render. Only B08 and B11 were rendered again afterward. Claude Code reported that the other beats were unaffected, but I didn't compare every frame myself.

I decided to keep that limitation documented instead of claiming I had checked something I hadn't.

**Evidence:** `BUILD-PROMPT.md` and `qc_reports/contact_sheet_6s.png`

## 7. My README's .gitignore statement was wrong

I originally thought the course repository's `.gitignore` would keep all generated media files out of GitHub, so I wrote that in the README.

When this was checked, I found that only `.mp4` and `.mp3` files were ignored automatically. The `build/` and `media/` folders weren't ignored.

I corrected the README and made sure only the selected 69 files were copied into the repository for the submission package.

Another issue was that some raw Gate B logs contained my local home-directory path. I left those 11 logs out of the repository copy because the corresponding Markdown and JSON reports already contained the results. The home-directory path in the copied `MASTERCHECK.md` was also shortened to `~`.

I kept the original quality-gate evidence separate from the cleaned submission copy.

One thing I left unchanged: my pitch film folder on GitHub still contains 13 Gate B logs with my home path. That submission is already graded, so I did not rewrite it.

**Evidence:** `README.md` (section "Media and git")
