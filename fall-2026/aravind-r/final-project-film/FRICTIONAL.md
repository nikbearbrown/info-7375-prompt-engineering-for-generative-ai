# FRICTIONAL — Readback: pitch film and project film

Machine: MacBook (Apple Silicon), macOS (Darwin 25.5.0). Claude Code 2.1.283. Project film (2026-11-23): Claude Code 2.1.323. Project film: macOS Darwin 27.2.
Entries were drafted by Claude Code from the session as it happened; decisions marked (Aravind) are mine; I reviewed all entries.
Toolkit: brutalist.art checkout at `/Users/aravindravi/Desktop/Northeastern/Coursework/Fall 26/Prompt_Engineering_Agentic_AI/Assignments/A01/brutalist.art`, starting commit `cd4bf20904be4e7d63babd9622b17963c2361b27`. Final toolkit commit: `cd4bf20904be4e7d63babd9622b17963c2361b27` (not pulled; see the 2026-10-14 entry "decision: no pull").

Claude Code ran the setup steps on my machine at my request. Command output quoted below is copied from its terminal.

---

## 2026-10-14 — Phase 0: where the submission folder lives

- **Repo:** my existing local clone of the course repo, `/Users/aravindravi/Desktop/Northeastern/Coursework/Fall 26/Prompt_Engineering_Agentic_AI/info-7375-prompt-engineering-for-generative-ai`. Remotes: `origin` = nikbearbrown (never pushed to), `fork` = aravindravi7/prompt-engineering-and-agentic-ai.
- **Week 1 branch check:** `git log --oneline -- fall-2026/aravind-r/week-01-video` → one commit, `e3fc591`. `git branch -r --contains e3fc591` → only `fork/week-01-video-aravind-r`. The local `main` also points at `e3fc591`, which is not on `origin/main`.
- **Decision:** cut a new branch `final-project-film-aravind-r` from `origin/main` (`42d8c48`), so a later PR to origin carries only this folder and not a duplicate of the Week 1 commit (Week 1 is already open as its own PR, #8).
- **Problem:** checking the new branch out in the existing working tree would have removed the tracked Week 1 files from disk while I'm on it, and the Week 1 folder is my read-only reference. **Did instead:** `git worktree add -b final-project-film-aravind-r ../info-7375-final-project-film origin/main`. Same clone and object store, second working directory at `/Users/aravindravi/Desktop/Northeastern/Coursework/Fall 26/Prompt_Engineering_Agentic_AI/info-7375-final-project-film`. The branch's upstream was unset so a bare `git push` can't go to origin.

## 2026-10-14 — Phase 0: Brutalist checkout state (no pull yet)

- `git status` shows the Week 1 local changes still in place: `runtime/remotion/src/scenes/ClaudeTitleOutro.tsx` (my 3-line `handle` patch), `runtime/remotion/package-lock.json`, 3,413 deleted files under `youtube/` (parked in `A01/_toolkit-youtube-parked/` to get past the setup ElevenLabs guard), untracked `.venv/` and `media/`.
- `git fetch`: upstream moved `cd4bf20..519fcbb` (2026-10-12), 46 commits, 1,837 files changed. `cd4bf20` is an ancestor of `origin/main`, so a pull would be a fast-forward apart from my local changes.
- Things in that range that affect this film:
  - `requirements.txt` now pins `manim>=0.20,<0.21`. The comment says 0.18 renders each scene one frame short and `compile.py` then refuses the film. My venv has manim 0.18.1 on Python 3.12.14, so a pull means reinstalling.
  - `ClaudeTitleOutro.tsx` changed upstream and now says the handle is `HARDCODED — no prop, no lookup, no override`. A pull will conflict with my Week 1 patch.
  - `youtube/` upstream still holds archived scene sources that mention ElevenLabs, and `setup` still has the guard, so restoring `youtube/` would bring the Week 1 setup failure back.
  - `show-tell` already exists in my checkout. Upstream added a card family, prop packs and more gate traps to it.
  - New `professor-bear/` folder and `runtime/scripts/professor_bear.py` (instructor portrait library). I won't use it, since the assignment forbids the instructor's persona.

## 2026-10-14 — Phase 0: conflict between show-tell and the assignment

The show-tell skill defaults to "Liam, in for Bear" (Kokoro `am_onyx`), a spoken "At Nik Bear Brown" outro and the `@NikBearBrown` handle. The assignment says to narrate as myself and not use the instructor's name, persona or credit line. The assignment wins: the persona lines, the greeting and the outro handle will need replacing. How I handle the outro (patch again, or drop the stock outro) is a decision for after the pull question.

## 2026-10-14 — Phase 0: is the name "Readback" free?

- PyPI: `https://pypi.org/pypi/readback/json` → 200. `readback` 0.1.0 is taken (coldbricks/readback, "Validation via echo-confirmation"). `readback-pm` → 404, free.
- GitHub: a repository-name search for "readback" returned 141 repos (e.g. cbothner/readback, borisdiakur/readback). A search for "readback-pm" returned 0. `aravindravi7/readback` doesn't exist.
- **Decision (from my instructions before the check):** "Readback" stays the display title, and `readback-pm` becomes the package/repo name.

## 2026-10-14 — Phase 0: commit attribution turned off

- The current Claude Code settings reference says `includeCoAuthoredBy` has been deprecated since v2.0.62 and replaced by `attribution` (`commit`, `pr`, `sessionUrl`).
- Set `{"attribution": {"commit": "", "pr": "", "sessionUrl": false}}` in `~/.claude/settings.json` (new file) and in `Assignments/A03/.claude/settings.json`, the project this session runs from. I'll still check `git log --format=%B` after every commit.

## 2026-10-14 — Phase 0: assignment file missing

`Assignments/A03/ASSIGNMENT.md` doesn't exist (A03 was empty). The assignment text was pasted into the session, so the prompt check before Phase 1 will use that copy unless I add the file.

## 2026-10-14 — decision: no pull, stay on `cd4bf20`

**Decided (Aravind):** don't pull upstream. Stay on `cd4bf20904be4e7d63babd9622b17963c2361b27`, the version Week 1 already built on, and record it as the final toolkit commit for this film.
**Why it's workable:** the show-tell skill is already in this checkout. The working install from Week 1 (manim 0.18.1 on Python 3.12.14, Homebrew espeak-ng via `A01/brutalist-env.sh`) stays as it is, and the Week 1 outro `handle` patch doesn't conflict with anything.
**What I give up:** upstream's later show-tell changes (card family, prop packs, extra gate traps) and its Manim 0.20 pin. The film has to be rebuilt against `cd4bf20` with manim 0.18.x, not against current upstream.
**Side note:** this checkout's show-tell `SKILL.md` says "Short, 60–180 s". The assignment requires 2–4 minutes, and the assignment governs, so the film will run longer than the skill suggests.

## 2026-10-14 — Phase 1: brief drafted, not final

- Claude drafted `PROJECT-BRIEF.md` from the appendix answers in my build prompt. Every sentence taken from that draft is marked `<!-- draft -->`, and I'll rewrite them in my own voice.
- **Gaps left for me (TODO markers):** the date I check the alternatives; which one or two alternatives go in the film; which "out" item leads; confirming the Week 1 links open.
- **Flagged, not changed:** Q1's first sentence says Readback "shows" (present tense) although nothing exists yet.
- "Exists today" lists only real things: the draft brief, this log, the toolkit checkout, and the Week 1/Week 2 PRs (#8 and #23, both open). It says explicitly that nothing of Readback is built yet.

## 2026-10-14 — Alternative check: Maxim AI (Aravind)

   Looked at: getmaxim.ai FAQ "What is LLM-as-a-Judge evaluation" and the Maxim article "LLM as a Judge: a practical, reliable path...".
   What it does: multiple LLMs as judges with compared assessments; judge–human agreement via percent agreement, Cohen's kappa, Krippendorff's alpha; human annotation.
   Clause-level disagreement localization: not found in these docs.
   Effect on Q2: measuring agreement is not a differentiator; claim narrowed to clause attribution.

## 2026-10-14 — Alternative check: orq.ai (Aravind; added, found while checking Maxim)

   Looked at: docs.orq.ai "Align an Evaluator with Human Judgement" cookbook.
   What it does: compares a pass/fail evaluator against human labels, measures self-consistency by re-running, then proposes a rewritten evaluator prompt.
   Clause-level localization: the docs describe a rewritten prompt, not attribution to a specific rubric clause.
   Effect on Q2: Readback's difference is clause attribution plus returning a question to the PM instead of auto-rewriting, which matches my Q5 "out" item.

## 2026-10-14 — Alternative check: Spec Kit clarify (Aravind)

   Looked at: github.com/github/spec-kit.
   What it does: an optional /speckit.clarify step that resolves ambiguity in a spec before planning. Applies to specs, not eval rubrics.
   Effect on Q2: kept only as the spec-side comparison for the later PRD module.

## 2026-10-14 — Braintrust and Confident AI (Aravind)

   Not checked in time; removed from the brief's claims.

Note for all four entries: Claude found and summarized these pages; I opened each one on 2026-10-14 and confirmed the summary.

## 2026-10-14 — Q5 lead "out" item decided (Aravind)

My decision, in my words: "Readback will never rewrite a rubric itself; it only asks the PM clarifying questions, and the PM decides." It goes into the brief as the lead "out" item. "No UI" and "PRDs and system prompts are later modules" stay as secondary lines, still in draft.

## 2026-10-14 — brief marked final too early (Aravind)

Marked the brief final before editing it; Claude Code caught it by comparing file timestamps and didn't proceed. Brief stays draft until my rewrite is on disk.

## 2026-10-14 — decision: outro, greeting and persona (Aravind)

Outro: reuse my Week 1 patched ClaudeTitleOutro with my handle. Also replace show-tell's 'Liam, in for Bear' greeting and the spoken 'At Nik Bear Brown' outro line with my own narration. Drop the 'Liam' persona name. The Kokoro voice choice is decided in Phase 3. No instructor name, persona or credit anywhere in the film or its metadata.

## 2026-10-14 — Phase 1 complete: brief final (Aravind)

Replaced `PROJECT-BRIEF.md` with my final text, with no draft markers left. It was drafted by Claude from my inputs and reviewed by me (noted in `SOURCES.md`). Changes from the draft:
- Q2 now names Maxim AI and orq.ai, checked 14 October 2026, and narrows the claim to clause attribution plus returning a question to the PM.
- Braintrust and Confident AI are out.
- Spec Kit stays as the spec-side comparison for the later PRD module.

## 2026-10-14 — Phase 2: AMI annotations downloaded; summaries are CC BY 4.0

- **Downloaded** `ami_public_manual_1.6.2.zip` from the official download page into `case-study/data/raw/` (git-ignored; `git check-ignore` confirms it). 22,887,865 bytes, HTTP 200, `Last-Modified: Mon, 10 Apr 2017`, SHA-256 `b56e5bab…9f9d`.
- **Licence check:**
  - The licence page and the `LICENCE.txt` inside the zip both say "The AMI corpus and its annotations are released under … CC BY 4.0".
  - The annotation documentation lists abstractive and extractive summaries as annotations.
  - The zip contains them: 142 `abstractive/*.abssumm.xml` files (headings ABSTRACT, DECISIONS, PROBLEMS/ISSUES, ACTIONS) and the `extractive/` files.
  - **Conclusion:** the summaries are clearly covered, so there is no reason to STOP.
- **Small inconsistencies, logged rather than resolved:**
  - The download page says v1.6.2, but the README inside says "release 1.7" (16 June 2014). The download page says the annotations are unchanged since 2014 and only the licence changed.
  - `LICENCE.txt` opens with the CC BY 4.0 statement but includes the older CC "THE WORK (AS DEFINED BELOW)…" preamble before the 4.0 sections. Neither affects coverage.
- **Recorded in `SOURCES.md`:** licence, attribution, URLs and hash.

## 2026-10-14 — Phase 2 step 2: whole meetings instead of cut segments (Aravind)

- **Change:** my build prompt asked for 10–20 decision-heavy segments of 10–15 minutes each. I changed that to **10 whole scenario meetings under about 35 minutes with a non-empty DECISIONS section**.
- **Reason:** the AMI abstractive summaries are written per meeting, so a cut segment wouldn't match its reference summary.
- **What Claude Code had done before the change:** extracted the zip and inspected the formats. It was considering a window-based selection that used the summary-to-dialogue-act links (`extractive/*.summlink.xml`). That approach was dropped before any segment was cut.
- **Result** (`case-study/scripts/select_ami_sample.py`):
  - 73 meetings were eligible, across 35 teams.
  - The selection takes one meeting per team, ranked by DECISIONS count, and keeps the top 10: IS1004d, ES2006d, IS1009d, ES2008c, ES2010b, ES2011b, ES2013d, IS1003c, IS1005c, ES2007a.
  - The sample is 412 KB. The full rule is in `case-study/data/sample/README.md`.
- **Hit while building:** `meetings.xml` stores durations as decimals (`972.64`), so the first run crashed on `int()`. Fixed by parsing them as floats.
- **Borderline case:** ES2008c is 2098 s (34.97 min). It's inside the "under 35 minutes" cut, but only just.
- **Reproducibility:** a second run produced byte-identical files.
- **Phase 2 scope cap (Aravind, deadline):** steps 1–5 only. Step 6 (my labels) and step 7 (judges) are skipped and stay "will".

## 2026-10-14 — Phase 2 step 3: constructed docs drafted

- Claude drafted three files in `case-study/constructed/`: `recap-prd.md`, `recap-system-prompt.md` and `rubric-v0.md`.
- Each starts with the line `CONSTRUCTED — drafted with Claude, edited by Aravind on <date>`; I fill in the date after my edit pass.
- **Rubric v0** has five pass/fail clauses:
  - C1 decisions complete;
  - C2 claims trace to the transcript;
  - C3 action items have owners;
  - C4 unresolved stays unresolved (subjective);
  - C5 useful to someone who missed it (subjective).
- **The PRD** doesn't name any meeting product, and it says the feature is unaffiliated.
- **Next:** my 5-minute edit pass on the rubric and the system prompt (STOP), then the feature run.

## 2026-10-14 — Phase 2 step 5: script written, not run

- Re-checked before the run: `recap-system-prompt.md`, `rubric-v0.md` and `recap-prd.md` were still Claude's 13:55 drafts, and their headers still read `<date>`. My edit pass wasn't on disk yet, so Claude Code didn't run the feature.
- It wrote `case-study/run_feature.py` in the meantime:
  - It uses headless `claude -p --output-format json` with my system prompt as `--system-prompt`, tools disabled, no session persistence, and an empty temporary working directory. No API key is involved.
  - It doesn't use `--bare`, because that mode skips the subscription login.
  - It saves one JSON file per meeting, with the date, `claude --version`, the model(s) reported and SHA-256 hashes of the prompt and transcript.

## 2026-10-14 — Phase 2 step 4: my edit pass (Aravind)

- **C1 rewritten:** "Every decision listed in the AMI human summary's DECISIONS section appears in the recap in substance (paraphrase is fine). Reference: that meeting's summary.txt." Still objective-leaning.
- **C5 is my wording**, kept exactly. C2–C4 stay as Claude drafted them.
- **Leakage rule:** the recap feature gets the transcript only, never `summary.txt`. Only the C1 judge gets the AMI DECISIONS list. It's stated in `recap-prd.md` and `run_feature.py`; the script reads only `transcript.txt`.
- **Known tension:** 250-word cap vs C1 on dense meetings (IS1004d has 12 decisions). Kept deliberately; expected to cause C1 failures.
- **Header on all three constructed files:** "CONSTRUCTED — drafted with Claude; clause decisions by Aravind, 2026-10-14".
- My edits arrived as instructions in chat; Claude Code wrote them into the files.

## 2026-10-14 — Phase 2 step 5: feature run on all 10 meetings

- Ran `python3 -I case-study/run_feature.py`. It did one test meeting first (ES2007a, 17.7 s), then the other nine in the background, between 18:00:29 and 18:03:22 UTC.
- **Nested `claude -p` worked from inside this session**, so no second terminal was needed.
- **Every record** reports `claude-opus-5-5` and `2.1.283 (Claude Code)`, with `is_error: false`. All ten used the same system-prompt SHA-256 (`6a047888…`). That hash covers only the prompt text below the `---` line; my header edit isn't part of the prompt.
- **Recap lengths** by plain whitespace count, which includes headings and timestamps: 224–276 words. This is a crude count, not a rubric judgment. Pass/fail on any clause waits for my labels, which are out of scope for this deadline.
- **Updated** "Exists today" in `PROJECT-BRIEF.md` to list the AMI sample, the constructed docs and the feature outputs, with dates.

## 2026-10-14 — Phase 3: beat sheet drafted (awaiting my narration review)

- **Generator:** `make_sheet.py` writes `beat_sheet.json` in the show-tell format: the hesitant-writer hook, then 8 drawn Manim body beats (Q1 to Q7, then exists vs will), then the outro.
- **Extra fields** `question_ids`, `claim_status`, `evidence` and `on_screen_label` sit inline on each beat. The toolkit schema (`runtime/schema/beat_sheet.schema.json`) allows additional properties on a beat, so no `beat_claims.json` sidecar is needed.
- **Bookends:** `bookend_exempt: ["cold-open", "bvdt", "bhtf"]`. These are valid values in `bookend_check.py` and drop the Claude.ai composer and verdict card. The outro check can't be exempted, so BOUT keeps `ClaudeTitleOutro` with my handle (`channel_title` "Aravind Ravi · INFO 7375"). The terms card is left out, because my beat order doesn't include it.
- **Too long at first:** the first draft was 703 words, about 4:40 at 150 wpm, which is over the 4:00 limit. Tightened to 567 words.
- **Expected runtime:** Week 1's sheet measured 604 words over 203.5 s of audio including added holds, about 2.97 words per second. At that rate this script comes to about 3:10 before holds.
- **Kokoro pronunciation:** written out as "A I", "P M", "A M I", "Ork dot A I", "Tech for Dev", "Koine Arth" and "Claude Opus five point five". The whisper check comes after audio.
- **Still mine to decide:** the Kokoro voice. The sheet uses `am_onyx` as a placeholder (it's the toolkit default; the "Liam" persona name is dropped).

## 2026-10-14 — Phase 4: audio, pronunciation, scenes, paperwork

- **Narration approved as written (Aravind); voice `am_onyx`.** It's synthesized locally with Kokoro: `generate_audio_kokoro.py`, then `add_holds.py` (my Week 1 script, copied in) adds a 1.0 s hold after each beat and 1.5 s after B08.
- **First whisper check (base.en) found real mispronunciations:**
  - "A I" came out as "eye" ("an eye feature", "IPM").
  - "Maxim A I" came out as "Maxima I".
  - "to-dos" came out as "Todas".
- **Testing variants** with `small.en` showed that plain "AI", "AMI", "Maxim AI" in context, "E-vals" and "to-do items" are voiced correctly. I applied only those spelling changes; the wording is unchanged except "to-dos" → "to-do items".
- **New runtime:** 557 words, 171.6 s of speech, 181.66 s with holds (about 3:02).
- **scenes.py:** the show-tell iso kit pasted unchanged, plus 8 scenes, a midpoint guard (`P()`), a question marker top-left and an honesty tag bottom-left on every beat.
  - B08's excerpt is asserted as a verbatim substring of `case-study/outputs/feature-run/ES2007a.json`.
- **Low-res stills** (`manim -ql -s`) showed overlaps and fixes were needed:
  - "per clause" was on top of the table (B03).
  - "10 AMI meetings" was on top of the pages, and the B05 tag ran off-frame.
  - The B06 padlock shackle was hidden behind its body; fixed with `arc_center`.
  - The B07 PR tags collided.
  - The B08 excerpt overflowed its card.
  - The judge blocks were packed so tightly they'd fuse under GATE T.
  - All fixed and re-rendered.
- **Week 1 claim checked before it went in FACTCHECK:** "verified every on-screen number". Week 1's `verify_numbers.py` docstring says "Print every number that appears on screen in the video, from a real run", and every Week 1 FACTCHECK row is PASS, CORRECTED or EXEMPT.
- **Wrote** `FACTCHECK.md` (20 rows; future-tense lines marked EXEMPT), `SHOTLIST.md` and `PROMPTS.md` before the first `art run`, because Gate F refuses to render without them.
- **Render height 1080, not the skill's 2160:** that's what Week 1 used, and it's quicker against the deadline.

## 2026-10-14 — Phase 4: first `art run` blocked by Gate A

- **Broke:** `GATE A FAILED: B02_Difference has static errors — nothing rendered`. Running `static_scene_check.py` on each class showed the cause in B02 and B08: "explicit coord(s) outside the frame, e.g. (7.8,-3.0) in move_to". My `tag()` and `marker()` helpers placed text at `-6.0 + t.width / 2`. Gate A's stub gives text a placeholder width that's far too big (the same stub quirk as Week 1), so the computed x landed off-frame.
- **Fix:** `move_to([0, y, 0]).align_to([-6.0, 0, 0], LEFT)`. Real Manim left-aligns the text exactly, and the stub treats `align_to` as a no-op. All 8 scenes are then clean in Gate A. The log is kept as `gates/art-run-1-gateA-fail.log`.

## 2026-10-14 — Phase 4: render–gate–fix cycles (logs in `gates/`)

1. **`art-run-2`: Gate B (strict) didn't slot B05.**
   - Problem: "outside safe area": the B05 tag text box ran to x = 6.92, past the ±6.3 limit.
   - Fix: shortened it to "AMI data · CC BY 4.0 · downloaded 14 Oct 2026" and moved "CONSTRUCTED" under B05's rubric page. The B08 tag, which was almost as long, was shortened too; it now reads "real output · Claude Opus 5.5 · 14 Oct 2026 · grey = will". The model ID `claude-opus-5-5` stays in FACTCHECK and the output JSON.
2. **`art-run-3`: Gate V MAJOR.**
   - Problem: `low-contrast` 0.28 < 0.30 on the B02 midpoint frame, caused by the pale grey tool boxes.
   - Fix: kraft fill (`BOX_R`); the old clip was moved to `_superseded/`. **`art-run-4`: Gate V clean** (20 frames, 0 BLOCKER, 0 MAJOR).
3. **Watching the review cut found two problems no gate caught:**
   - **(a) The hook never corrected.** The hesitant writer stayed on "Does my feature pass the rubric". `BrutalistHesitantWriter` matches `triggerWords` one word at a time (comma-separated list), so my three-word trigger never fired. Changed the typed line to "Does the judge score my rubric", with `score` → `misread`. The narration is unchanged.
   - **(b) The stock outro draws the Claude mascot.** That conflicts with my no-logos / no-affiliation rule, and `ClaudeTitleOutro` had no switch for it. I extended my Week 1 toolkit patch with an optional `hideMascot` prop and set it on BOUT. The combined patch against `cd4bf20` is in `toolkit-patches/ClaudeTitleOutro-handle-hideMascot.patch`.
   - **`art-run-5`: all gates clean.** Frames confirm "Does the judge misread my rubric" and an outro with no mascot.
4. **`art-final-1`: GATE T FAIL.**
   - Problem: B02 "bbox-overlap §8.6b … two labels are printing on top of" each other. The tool names sat inside ink-outlined boxes, which breaks the show-tell law "labels beside objects, never inside an outline".
   - Fix: names moved above the boxes. Then `art-run-6` was clean, and **`art-final-2` gave GATE T: PASS**.
5. **Master:** `exports/landscape/aravind-r-readback-pitch.mp4`, copied to `aravind-r-readback-pitch.mp4`.
   - 1920×1080, 24 fps, H.264/AAC, 181.92 s (3:02).
   - SHA-256 `4ed0aba1…f8e60e`; `verified.json` status "ready".
   - Advisory only: "SKIN LINT: COLD OPEN LAW" on BIDEA, which the skill says to expect under `bookend_exempt`.

## 2026-10-14 — Phase 5: gates, runtime, honesty audit, frame spot-check

- **Toolkit gates on the final build, reports in `gates/`:**
  - F: paperwork present; `factcheck_check.py` clean, 20 rows.
  - L: clean.
  - A: 8/8 clean.
  - W: 8/8 clean.
  - B: 0 errors, 0 warnings.
  - V: 20 frames, 0 BLOCKER, 0 MAJOR.
  - T: PASS.
  - `bookend_check.py`: PASS.
  - Master: `verified.json` status "ready".
- **Runtime:** 181.92 s (3:02), inside 2:00–4:00.
- **Honesty audit** (`gates/honesty-audit.md`, my own check, not a toolkit gate): every narration sentence and on-screen claim is checked. It raises 10 flags, none applied yet: 5 medium (F3, F5, F7, F8, F9) and 5 low. **I decide the fixes.**
- **Frame spot-check:** one frame per beat from the master, in `gates/frames/` and `gates/frame-spotcheck.png`. Every label is legible, there are no logos, and no review overlays remain in the master.

## 2026-10-14 — Phase 5: audit fixes, then re-render and re-gate (Aravind's decisions)

- **Decided:**
  - Fix F3 (B03 "the question Readback asked" → "will ask").
  - Fix F5 (B04 "That I evaluate" → "That I'll evaluate").
  - Reword F8 as my own view (B07: "I think e-vals are becoming core to AI PM work").
  - Fix F9 (B05: "3 judges · planned" and a "planned" label before the commit line).
  - Keep F7 as disclosed.
- **Rebuilt:**
  - Re-ran `make_sheet.py`, Kokoro, `add_holds.py` and `align.py`. Only B03, B04 and B07 changed length; whisper hears all three as written.
  - Moved `manim/B03`, `B04`, `B05` and `B07` and the Manim media cache to `_superseded/`.
  - `art-run-7`: the four scenes were re-rendered; Gate B 0/0, Gate V 0 BLOCKER, 0 MAJOR.
  - Gate A and Gate W re-run on all 8 scenes, all clean (`gates/gateA-gateW-all-scenes.txt`).
  - `art-final-3`: GATE T PASS. Bookend check PASS; factcheck clean (row 20a added for the reworded B07 line).
- **New master:** 1920×1080, 182.46 s (3:02), SHA-256 `18f0d50c…581c131c`, `verified.json` "ready".
- **Updated:** `gates/honesty-audit.md` (second pass and a Resolution table) and `gates/frames/` + `gates/frame-spotcheck.png` (re-extracted from the new master).

## 2026-10-14 — v2 visual upgrade started (Aravind's decision); timebox set

- **Decision (Aravind):** v1 passes every gate but doesn't hold attention when watched without audio. I'm building a visuals-only v2 to a new file, `aravind-r-readback-pitch-v2.mp4`. The narration clips and durations stay locked, and v1 (`31005a1`) stays untouched.
- **Timebox:** the deadline is 2026-10-14 23:59 EDT, so the hard stop is **22:44 EDT**. If v2 isn't fully gated by then, v1 gets submitted. Started 15:10 EDT.
- **v1 baseline (Claude Code, measured):** `ffmpeg freezedetect n=0.003 d=3` on the clean master finds 23 holds of ≥3 s, totalling 163.7 s of 182.46 s (89.7 %). The `-slate` review copy measures 90.6 %.
- **Clean master confirmed:** the committed `aravind-r-readback-pitch.mp4` (SHA-256 `18f0d50c…`) is the `art final` export with no overlays. The copy I watched was the git-ignored `-slate` review cut (`4186bbe0…`).
- **Beat IDs:** the sheet's BIDEA, B01–B08 and BOUT are kept, and my brief's B01–B10 map onto them (Aravind). BIDEA becomes a Manim scene.
- **Plan:** `gates/v2-visual-plan.md`. It flags two adjustments for my review: text stays ink because red and grey type fail the 4.5:1 floor, and the 250-word cap goes on its own word-count axis.

## 2026-10-14 — v2 probe: B05 (the real-data beat), built first

- **Setup:** v2 is built in its own reel folder, `v2/`. It holds copies of `beat_sheet.json`, `mp3/` (all ten clips byte-identical to v1, checked by SHA-256) and the paperwork, plus a new `scenes.py` with the v2 design system. v1's sources and outputs aren't touched.
- **Real numbers come from files at render time.** `scenes.py` reads `selection.csv` and the ten feature-run JSONs and asserts every DECISIONS count, duration and recap word count shown on screen.
- **Fix cycles on the probe (each Gate A/W/B-checked and rendered at 1080p):**
  1. **First render:** one 3.5 s freeze at 12.5–16.0 s, and another from 16.0 s to the end. After 12.5 s only small text and grey outlines were added, which is under `freezedetect`'s n = 0.003 threshold.
  2. **Focus dims added:** the chart dims at "Out", the rubric block at "agreement table", the plan at "commit", and everything is restored for the closing state. That left a 3.2 s freeze, because the dims are only meaningful at those cues; I moved the rubric-block dim to "agreement table". Result: 0 holds of ≥3 s.
  3. **Gate B:** 6 warnings, then 1 error. "Why me" and "OUT" ran outside the safe area. "CONSTRUCTED" touched the PM ring, and the commit line crossed "labels". The rubric page, scaled up at "asks", ran into "OUT"; I replaced the scaling with an arrow from the red C4 dot to the "?" chip, which also says what the question comes from.
  4. **The last frame showed a black disc:** `set_opacity(1)` had filled the outline-only PM ring. Switched to `save_state()` / `Restore`.
  5. **Overlaps Gate B didn't flag:** the C1–C5 labels stacked on the small page, "PM" overflowed its ring, and "my labels", "250 cap" and the checklist arrow collided. Small pages now label only C4 (the clause in question); the cap label is "250".
- **Result:** 19.33 s against 19.35 s of audio. Gates A and W clean; Gate B 0 errors, 0 warnings. `freezedetect` d = 3: **0 holds**. At d = 2 there are 2 holds, of 2.5 s and 2.2 s.
- **Contact sheet:** `gates/v2-probe-B05-contact.png`, 1 frame every 2 s.

## 2026-10-14 — v2 built and gated; it isn't swapped in until I approve it

- **Timebox:** v2 is fully gated by about 16:35 EDT, well before the 22:44 hard stop.
- **Building the other eight scenes, what broke (all logged in `gates/v2/`):**
  1. **The first full pass still froze for 4–6 s in most beats.** `freezedetect` measures against a reference frame and averages over the luma and chroma planes, so a new word, a thin line or a grey outline barely registers.
     - Fix, using only meaningful changes:
       - a dark header band on the rubric page (its moves now register);
       - larger tan judge discs and filled pass/fail stamps;
       - real evidence on larger tan cards;
       - focus dims at topic changes;
       - a light grey fill under planned outlines;
       - the on-screen synthetic-voice disclosure in the hook.
     - B06's `Rotate` on the revise loop was removed (no spinning).
  2. **Gate A:** `Intersection` and zero-length text don't exist in its stub. Replaced with a drawn lens and string-based timing.
  3. **Gate B:** about a dozen labels-on-lines and overlaps across B01, B03, B07 and B08. Fixed by re-laying them out:
     - B01's diagram collapses into the rubric icon, and B02 opens by growing it back (a match-cut).
     - B08's closing fades the rest out instead of dimming it under the growing page.
  4. **`AddTextLetterByLetter` keeps its own per-letter clock,** which delayed B03's cues by about 1 s per row. Headers now fade in; the two typed lines get an explicit per-letter time.
  5. **The midpoint guard pushed some cues late.** It now shortens a move to finish before the midpoint when there's room.
  6. **Gate V MAJOR (low contrast) on B01, B02 and B06.** Large pale fills pulled the average under 0.30. Pale fills were lightened, then the clips superseded and re-rendered.
  7. **Gate T, several rounds:**
     - Ink-outlined containers holding text are read as overlapping text runs (the README window, the excerpt card), so text containers now get grey outlines.
     - A tiny padlock in the held-out box read as 39 px type; removed.
     - The bullet dots; removed.
     - The small rubric icon's header band was too thin; it now has a minimum height of 0.19 units.
     - A slightly slanted connector read as sub-floor type; it's now level.
     - The B04 title touched the first chip; moved.
  8. **Found by my own frame checks (no gate flags these):**
     - B04's "AI features" label collided with the anchor.
     - The "verification" connector crossed the rubric icon.
     - Both fixed and re-rendered.
- **Final v2:** `aravind-r-readback-pitch-v2.mp4`, 182.458 s, SHA-256 `513e26d0…`.
  - Every gate is clean in strict mode: F, L, A, W, B and V in `art run`, then T in `art final`, plus bookend, factcheck (37 rows) and `verified.json` "ready".
  - **freezedetect:** v1 had 23 holds of ≥3 s, 163.7 s (89.7 %). v2 has 5, 17.1 s (9.4 %), longest 3.9 s, plus the static outro card.
  - The narration audio PCM is identical to v1.
- **Paperwork for v2:** `v2/FACTCHECK.md` (rows 21–36), `v2/SHOTLIST.md`, `gates/v2/honesty-audit-v2.md` (3 low flags: V1–V3), `gates/v2/GATES.md`, and a v2 section in `SOURCES.md`.
- **v1 is untouched:** `aravind-r-readback-pitch.mp4` still matches commit `31005a1`. Nothing is committed.

## 2026-10-14 — v2 approved after a frame-by-frame overlap pass; swapped in (Aravind's decision)

- **Decision (Aravind):** "Avoid all text overlaps. Everything else look good to go. Check every frame by frame."
- **The check:** Claude Code wrote `overlap_check.py`. It runs each Manim scene at 24 fps and, on every frame, inspects the live geometry: text-box against text-box intersections, and any visible line, outline or shape boundary inside a text box.
- **First run:** overlaps in all nine scenes. Most were transient (an exit fading while an entrance slid through it, text sliding across the rail, a transforming page passing over labels). A few were static:
  - B05's checklist rows touched;
  - B02's header grazed the column panel and its rule;
  - the B04 anchor met "held-out";
  - B08's first row crossed the divider;
  - B07's requirements icon met the role line, and one link crossed "KoineArth".
- **Fixes:** exits finish before entrances begin; no shift passes through text; rows are spaced and bands made taller; emphasis scaling is gentler; the bracket ticks point down; the role line moved up; B07 got a single bracket-to-Readback arrow; a few labels moved.
- **Second run:** 4 scenes still had 1–2 cases each. After fixing those, a third run gave **0 overlaps on every frame of all nine scenes** (`gates/v2/overlap-check.txt`). The outro card and the toolkit's small name line on the hook were checked by eye; neither overlaps anything.
- **Full strict rebuild:** every gate clean (A, W, B, V, T, bookend, factcheck 37 rows, `verified.json` "ready").
  - freezedetect: 8 holds of ≥3 s, 26.3 s (14.4 %), longest 3.9 s. That's up from the first candidate's 9.4 %, because the overlap fixes removed some slide-ins; still under the 25 % target, with no hold over 4 s.
  - Runtime 182.458 s; narration PCM identical to v1.
- **Swap:**
  - The v2 sources (`scenes.py`, `beat_sheet.json`, `FACTCHECK.md`, `SHOTLIST.md`, `overlap_check.py`) were promoted to the top-level folder, and `make_sheet.py` now emits the v2 sheet.
  - Rebuilding from the top level with the toolkit's commands gave a file **byte-identical** to the gated v2 candidate: SHA-256 `4334b59e…`, all 4,378 decoded frames identical. That file is now `aravind-r-readback-pitch.mp4`.
  - The `v2/` build folder was retired (git-ignored under `_superseded/`). v1 remains in git history at `31005a1`.

## 2026-10-14 — PR #18 opened to the course repo (Aravind)

- **What I did:** I approved the PR title and body as drafted (Claude Code wrote them to `Assignments/A03/PR-DRAFT.md`, outside the repo; no attribution line). Claude Code opened GitHub's compare page, and I signed in and created the PR myself: https://github.com/nikbearbrown/info-7375-prompt-engineering-for-generative-ai/pull/18. It merges `aravindravi7:final-project-film-aravind-r` (3 commits, 126 files, all under `fall-2026/aravind-r/final-project-film/`) into `nikbearbrown:main`.
- **Title:** I used "final-project-film: add aravind-r pitch film : Readback" (a colon where the draft had a dash).
- **CI:** the PR showed 0 checks when I opened it. The course workflow (`scripts/validate_course.py`) normally waits for a maintainer to approve workflows on a fork's PR. It passes locally on this branch (13 tests, OK).
- **Status:** open, not merged. The Week 1 film is PR #8 (open) and the Week 2 recipe is PR #23 (open, not merged).
- **This entry:** added after the PR opened, in its own commit. PR #18 picks the commit up automatically, and the Canvas zip is rebuilt from it.

## 2026-11-23 — Project film (four-part brief), Phase 0: orientation and timebox

- **New assignment:** a project film in four parts, in this order:
  1. executive summary;
  2. introduction (prior work);
  3. methods;
  4. evaluation.
- It's a new film, not a re-cut. The pitch films (v1 `31005a1`, v2 in `636c77e`/`2cad8ba`) stay untouched. Output: `aravind-r-readback-project-film.mp4`, built in `film/project/`.
- **Timebox (Aravind):** the deadline is tonight, 2026-11-23 23:59 EST, so the **hard stop is 22:29 EST**. If the film isn't fully gated by then, the best gated cut gets submitted and logged here. Phase 0 started at 05:19 EST.
- **Runtime cap (Aravind):** 4 minutes.
- **Resources for Methods (Aravind):**
  - claude -p on my subscription;
  - Anthropic API credits and OpenAI API credits (accounts held, project keys not yet created);
  - local open-weight models via Ollama (installed later on 2026-11-23, after Claude Code's checks; see my judgment-calls entry).
- **What Claude Code verified on this machine:**
  - `claude` CLI 2.1.323 is installed (it produced the 10 recaps on 14 Oct).
  - No `ANTHROPIC_API_KEY`, `OPENAI_API_KEY` or `GEMINI_API_KEY` in this shell's environment.
  - Ollama isn't installed yet.
- **Toolchain after the macOS update (Darwin 27.2):** the Brutalist venv (Python 3.12.14, manim 0.18.1) works; a Kokoro smoke test synthesized audio, and Manim renders.
  - faster-whisper, ffmpeg 9.0.2 (with `freezedetect`, `blackdetect`, `ebur128`, `loudnorm` and `silencedetect`), Node 20 and Remotion's `node_modules` are present.
  - The toolkit is still at `cd4bf20` with my outro patch.
  - **False alarm:** my first check reported `No module named 'kokoro_onnx'`. It had piped `source brutalist-env.sh` into `tail`, which ran the activation in a subshell; re-run properly, the import works.
- **Repo:** branch `final-project-film-aravind-r` in the course-repo fork (not a Brutalist fork). **PR #18 has been merged**: `2cad8ba` is in `origin/main`, so pushing to this branch doesn't change a PR.
- **AMI annotations for the 10 selected meetings:**
  - all 10 have the human-written abstractive DECISIONS list (86 decisions in total) and the summary-to-dialogue-act links (`extractive/*.summlink.xml`);
  - only 3 (ES2010b, IS1003c, IS1004d) have AMI's separate `decision/manual` annotations.
  - The DECISIONS list is a reference; it isn't a pass/fail label on our recaps. Judge-vs-human agreement on the decisions clause still needs coverage labels for those 86 decisions. To be settled in Phase 1.

## 2026-11-23 — Project film, Phase 1: script and claims ledger drafted (awaiting my review)

- **Pacing, measured rather than guessed:** the pitch film's Kokoro clips (`mp3/`, `am_onyx`, speed 1.0) ran 554 words over 169.0 s of speech, which is **3.278 words/s (197 wpm)**; beats ranged from 3.01 to 3.61 words/s.
  - The 4:00 cap was budgeted roughly 20/20/35/25 across the four parts, with 0.5 s holds and a 4 s outro.
  - The draft comes to 675 words, about 3:39: summary 123, introduction 147, methods 249, evaluation 156.
- **Files:**
  - `film/project/make_sheet.py` generates `film/project/beat_sheet.json`, with 19 drawn beats plus the patched outro.
  - `film/project/CLAIMS.md` has 53 narration sentences (N01–N53) and 15 intended on-screen numbers (O01–O15), each mapped to an evidence path or marked PLANNED.
  - `film/project/EVAL-PLAN.md` (PLANNED · DRAFT) is where planned settings like κ ≥ 0.6 and "3 judges" come from, so no number on screen lacks a repo source.
- **Wording kept honest:**
  - "nobody can tell which clause caused it" became "it's hard to tell";
  - everything Readback does is "will";
  - "the compute is my laptop" was cut, because the judge pipeline isn't tested locally;
  - only the three alternatives I verified on 2026-10-14 are named.
- **Open decisions for me (marked "(decide)"):**
  - how the human labels get made;
  - the κ threshold;
  - the planted-ambiguity variants;
  - the held-out split.

## 2026-11-23 — Project film, Phase 1 approved; Phase 2 storyboard built (awaiting my review)

- **Phase 1 approved (Aravind), as drafted:**
  - the narration;
  - human labels by proposal A: I mark the 86 decisions myself and commit them before any judge runs;
  - κ ≥ 0.6;
  - one planted variant per clause (C1–C5);
  - the held-out split fixed before any revision.
  - Recorded in `film/project/EVAL-PLAN.md` and `film/project/CLAIMS.md`.
- **Outro background (Claude Code):** the toolkit's `ClaudeTitleOutro` picks light or dark from a hash of the slug, and paints `#FAF9F5` or ink. Neither matches the film's stage colour `#F2F0E9` at the last cut.
  - It now takes two optional props, `polarity` and `background`. When they're omitted, it behaves as before.
  - Patch: `toolkit-patches/ClaudeTitleOutro-handle-hideMascot-polarity-bg.patch`, a superset of the pitch film's patch, which is untouched.
  - Measured: the outro still's ground is `#F2F0E9`, the same as every scene.
- **Narration voiced early, for timing only (Claude Code):**
  - Kokoro `am_onyx`, same settings as the pitch film, from the approved script.
  - 20 clips, **232.43 s with holds (3:52, cap 4:00)**, against the 3:39 estimate.
  - This is not a film render. `mp3/` is git-ignored.
  - Whisper heard every line as written except two:
    - In B13, "clause by clause: Claude, …" came back as "clause by clause, clause".
    - In B16, "Readback" came back as "Reidbeck", although B02 and B14 transcribed it correctly.
- **Design system and storyboard (Claude Code):**
  - `film/project/DESIGN.md` covers the colour roles, the type scale, the grid, the motion rules, the C4 clause chip as the object that runs through the film, and every number on screen with its source.
  - The scenes are in `film/project/scenes.py` (19 beats). The checks are `film/project/overlap_check.py` and `film/project/make_storyboard.py`.
  - The deliverables are `film/project/storyboard.png` and `film/project/style-frames/` (one frame per part).
- **Checks (Claude Code):**
  - Gate A: 19 of 19 scenes clean, 0 warnings.
  - Frame-by-frame text-overlap check: 19 of 19 scenes, 0 overlaps at 24 fps. The first pass flagged 99, from morphs crossing type, a crowded rail and entrances sliding into the tag line.
  - One stacking bug was found by eye: pulsing a meeting card raised it above its own ID and length, which hid them.
  - κ is spelled out as "kappa" on screen, because EB Garamond draws κ as ϰ.
- **Open decisions for me:**
  1. B15 puts "compute · this Mac · local judge untested" on screen. I cut a compute claim from the narration in Phase 1.
  2. B13 "Claude" may be misheard as "clause". The judge is labelled "Claude" on screen. The alternative is rewording that line and re-voicing B13 only.
  3. The constructed illustrations: B01–B03 (the judges' split, "what the PM meant ≠ how a judge reads it", the misgraded C4) and B14 (✓ ✗ ✓). All of them carry CONSTRUCTED or PLANNED tags.
  4. The on-screen wording for Maxim AI, orq.ai and Spec Kit (B04–B07). It's limited to what my 2026-10-14 checks above record.

## 2026-11-23 — Project film, Phases 3–4: build, fixes, and the gate table (Claude Code; awaiting my review)

- **Approval (Aravind):** I approved the Phase 2 storyboard as shown ("Approve, go to Phase 3"). The four open decisions stayed as drafted:
  - the B15 compute line;
  - B13 as voiced;
  - the constructed illustrations;
  - the wording for the three tools.
- **Gate F paperwork:**
  - `film/project/FACTCHECK.md` has 72 rows, 49 narration and 23 on-screen, and the factcheck gate is clean.
  - `SHOTLIST.md` and `PROMPTS.md` are in place.
- **Gate V, first run:** 14 MAJOR "low contrast" findings and one "underfill".
  - Cause: Gate V averages every non-background pixel as "ink", so large pale fills pulled the average toward the cream. Those fills were the light-kraft cards and nodes and the grey-filled planned cells.
  - Fix:
    - real-evidence cards in the deeper kraft `#C7AE86`, with ink on it at 5.4:1;
    - planned grid cells as dashed outlines only;
    - the tool nodes 0.4 shorter, re-entering with each tool;
    - B10's recap card on screen before the clip's midpoint.
  - Every later run: 0 defects.
- **Freeze:**
  - ffmpeg's `freezedetect` averages the change over all three colour planes, so even a 36-pt line fading in stays under n=0.003.
  - The first per-scene measurement found 50.9 s frozen, 22 % of the runtime.
  - Every static window got a change tied to its line: the judges stepping back and returning, page, card and tile flashes, the judges' rows pulling apart, names and rows pulsing, the feature leaving the frame and coming back, inverted flashes on the "—" results.
  - On the delivered file: 7.04 s frozen (3.0 %), with three holds of 2.5 s or more, each on a key line and listed in `SHOTLIST.md`.
- **Gate T, first `art final`:** 12 FAILs, all the same cause. The chip's closed terracotta ring around "C4" read as terracotta *text*.
  - The toolkit only exempts that pattern by listing scene names, for other reels.
  - I didn't add exemptions. Instead, the outline is drawn as four open strokes (two flat edges and two end caps) with hairline gaps. It looks the same, and the type stays ink.
  - Then: PASS, 20 of 20 beats.
- **Flashes that hid text:** the contact sheet caught an ink flash on B17's fail zone that hid the word "fail" for a moment. B09, B18 and B19 had the same pattern. Those flashes now change only the box (or invert box and text), so the type stays readable throughout.
- **Loudness:** the toolkit doesn't normalise, and its publish window is −28 to −18 LUFS (the pitch film measured −24.7). My brief asks for −16.
  - `film/project/normalize_audio.py` rebuilds the narration timeline the way `compile.py` does and runs a two-pass loudnorm to −16 LUFS / −1.5 dBTP.
  - `art final --audio` uses that track, so the verified master is the delivered file.
  - Measured: −16.1 LUFS, −1.4 dBTP.
- **Result:**
  - `film/project/aravind-r-readback-project-film.mp4`, 3:52.8 (232.83 s), SHA-256 `b763e8c4…`.
  - Toolkit gates: F, factcheck, L, A, W, B, V, T and bookends all pass, and the verified record is `ready`.
  - My overlap check: 19 of 19 scenes, 0 overlaps.
  - The full table was in `film/project/gates/GATES.md` (since rewritten for later cuts).
  - 7 `art run`s and 5 `art final`s. The superseded clips are in `film/project/_superseded/` (git-ignored).
  - The storyboard and style frames show the Phase 2 state: the kraft is lighter there and some motion has been added since.

## 2026-11-23 — Project film, revisions before Phase 5 (my review requests; Claude Code made the changes)

- **Not approved yet (Aravind).** Before Phase 5 I asked for seven things:
  1. B15 shows "have" only for what is set up on this machine.
  2. The human labels read as my planned work, not AMI's.
  3. Prior work is scoped to the tools I checked.
  4. B13 is reworded, and Readback respelled for the voice.
  5. The storyboard is regenerated.
  6. Every gate is re-run.
  7. The PR options are laid out.
- **Checked on this Mac (15:50 EST):**
  - `claude` 2.1.323 is installed.
  - No API key for Anthropic, OpenAI, Gemini, Google or Mistral is set in the environment.
  - Ollama is not installed.
- **B15 checklist:**
  - Ticks only for AMI data, the 10 recaps and `claude -p`.
  - API credits and the second provider are marked "account, not yet wired".
  - The local model and my human labels are "planned".
- **Narration changes:**
  - B15 now says "Claude runs here on my subscription. My API credits and a second provider account aren't wired in yet. Still to come: the local model, and my human labels."
  - B13 and B17 say "my human labels".
  - B12, B13, B17 and the scorecard say "my human labels … marked by me · planned" on screen.
  - B07 is scoped ("So the tools I checked give you…", title "From the tools I checked").
  - B03's "nobody notices" became "the wrong grading goes unnoticed".
- **B13** was reworded so "Claude" and "clause" are never adjacent: "…every recap: Claude, a second provider's model, and a local open-weight model, each one going clause by clause." Speech-to-text still writes the homophone "clawed" for "Claude" there.
- **Pronunciation:**
  - "Reedback" still came back as "Reidbeck" inside B16's sentence.
  - "Reed-back" came back as "read back" there and everywhere else.
  - So the Kokoro input uses "Reed-back" in all 7 beats that say the name. On screen and in the paperwork it stays Readback.
  - 11 beats were re-voiced with the same voice and settings. The transcripts are in `film/project/gates/review-cut-1/stt-revoiced-beats.txt`.
- **Two fixes along the way:**
  - Regenerating the sheet dropped `audio_file`, and `align.py` then wrote an empty `words.json`. `make_sheet.py` now writes `audio_file` itself.
  - Pulses that grew text into its box, and the new B13/B15 wording, needed re-cueing. The overlap check found these first.
- **Result:**
  - `film/project/aravind-r-readback-project-film.mp4`, 3:55.4 (235.38 s), SHA-256 `79aa3ec6…`.
  - 4.6 % frozen; five holds of 2.5 s or more, all on key lines and listed in `SHOTLIST.md`.
  - −16.1 LUFS and −1.2 dBTP; no black frames or dead air; one ground colour at every cut.
  - Toolkit gates F, factcheck, L, A, W, B (all 19), V, T and bookends all pass, and the verified record is `ready`.
  - My overlap check: 19 of 19 scenes, 0 overlaps.
  - `film/project/gates/GATES.md` was updated; that version is kept as `film/project/gates/review-cut-1/GATES.md`. The storyboard and style frames were regenerated from this master.

## 2026-11-23 — Project film, checks before Phase 5 (my requests; Claude Code ran them)

- **Submission route (my choice, item 7):** a new branch from the current head (`2cad8ba`), named `project-film-aravind-r`.
  - No merge or rebase of `origin/main`.
  - Commit only the project-film work and push it to my fork.
  - No PR until I say so.
  - Nothing is committed, branched or pushed yet. That waits until I approve the cut.
- **The 9 clips that weren't re-voiced** (B01, B04, B05, B06, B09, B10, B11, B12, B19): all 9 SHA-256 hashes match the pre-revoice backup (`film/project/gates/review-cut-1/unchanged-clips-sha256.txt`).
- **Speech-to-text on the full master:**
  - Method: `film/project/stt_check.py`, faster-whisper small.en, one diff over the whole film.
  - Words: 697 in the script, 697 heard.
  - 4 of 20 beats differ: B02 and BOUT ("Aravind" heard as "Eravind"), B06 ("GitHub's" heard as "GitHub") and B19 ("this scorecard" heard as "the scorecard").
  - Transcribed alone, B06, B19 and BOUT match the script. B02 still gives "Eravind".
  - In the full film, B13's "Claude" is heard as "Claude".
  - Results: `film/project/gates/review-cut-1/stt-full-master.txt` and the table in `review-cut-1/GATES.md`.
- **B15 checklist:** the code and B15's last frame in the delivered master match word for word (the frame at 3:00.25 is `film/project/gates/review-cut-1/B15-final-frame.png`).
- **Full gate re-run:** 16:14–16:19 EST, on the same master (`79aa3ec6…`). Every gate passes with the same values as the table (`film/project/gates/review-cut-1/gate-rerun.txt`, `review-cut-1/GATES.md`).

## 2026-11-23 — Project film, positioning revision (my review of the cut; Claude Code made the changes)

- My feedback on the review cut (Aravind): remove the four-part section bar; rubric isn't PM vocabulary, so define it or use a PM term; remove the "CONSTRUCTED illustration · no judge has run yet" clutter from the opening; lead with why Readback matters and its long-term impact (the real consequence of a wrong ship decision) rather than the mechanism; position Readback as application-agnostic, with the AMI meeting-recap feature as the test case only.
- Claude (chat) turned that into the P0/P1 list, added the frame-by-frame production items and proposed the positioning-audit gate. Claude Code made the changes.
- **Drafts approved as shown ("OK, go", Aravind).** That includes the lines flagged in the drafts:
  - "Every AI feature ships against acceptance criteria a PM wrote" (a generalisation);
  - "evals are becoming the launch gate" (a trend claim with no source in the repo);
  - the ES2010b example and my phrase "two quick yeses";
  - C4's plain-English version, which drops "disagreements";
  - the hook ending near 0:14, because it carries the rubric definition.
- **Real-evidence search (Claude Code):** all 10 recaps' Decisions lists, checked against AMI's DECISIONS and PROBLEMS/ISSUES and the transcripts.
  - **Used: ES2010b.** Asked "Do we want this thing to be able to be found easily?", the PM said "I think so" and ME said "Sure, yeah"; how to do it was left for later. The recap lists "The remote should be easy to find if lost" as a decision. AMI's annotators wrote that the group "will consider" a locator function. The film shows it as a line where C4 is hard to call, not as a recap error.
  - **Ruled out:** IS1005c's "5 cm by 10 cm" (the transcript shows it was agreed) and IS1009d's "well within budget" (the recap's own Unresolved list flags the open cost).
  - **Not used:** several recaps go the other way and list AMI decisions as unresolved (for example ES2008c's kinetic battery). That is a C1 story, not this one.
- **Narration:** 13 beats were re-voiced with the same voice and settings: B01, B02, B03, B08, B09, B11, B13, B14, B16, B17, B19, the new B20, and BOUT. The other 8 clips keep their speech; only their edge silence was trimmed.
  - `add_holds.py` now trims each clip's edges to 0.05 s, so the silence between beats is 0.35–0.55 s, varied, instead of about 1.1 s.
  - Speech-to-text on the new clips: `film/project/gates/stt-revoiced-beats.txt`.
- **Scenes (`film/project/scenes.py`):**
  - The section bar is gone. Chapter cards open each part; card 1 is also the poster frame.
  - Corner tags (illustration, planned, vision, test case) are set in `#6B675C`, which is 4.9:1 on the stage.
  - A generic "criterion" chip appears in the summary and the introduction; C4 is written in plain English from B11 on.
  - New or rebuilt beats: B01–B03, B09 (the test bench), the ES2010b example in B14, B15 in three columns, and B20 (the close).
  - The end card uses a new `tagline` prop in my outro patch (`toolkit-patches/ClaudeTitleOutro-handle-hideMascot-polarity-bg-tagline.patch`). The bookend gate's no-subline rule still applies, and `subline` stays empty.
- **New gate:** `film/project/positioning_check.py`. It reads the narration and every on-screen string on every frame (`strings_dump.py`) and writes `film/project/gates/positioning-audit.md`.
- **Fixes along the way:**
  - Gate A's stub over-measures text, so the vignette criterion pills and the B03 bubble now have fixed widths.
  - Gate B's safe area is ±3.4, so the corner tag moved to y 3.12.
  - My overlap check found 34 overlaps across 10 scenes: transitions crossing text, widths I had estimated instead of measured, and a key collision in B10 where the corner tag overwrote the Claude label. All are fixed; 0 remain.
  - Gate V flagged B03 and B09 as under-filled at their midpoints, B09 with its meeting cards still fading in at the 85 % sample, and later a B15 flash at the 85 % sample. All were re-timed or re-laid out; Gate V is 0/0.
  - The freeze gate first measured 47.62 s (20.0 %), over the 15 % cap, because the new scenes change in small steps that ffmpeg's detector doesn't count. Colour flashes on large cards and soft bands, each on a spoken word, brought it to 5.08 s (2.1 %); only the end card is static.
  - The toolkit's compile step prints `channel_title` over the whole first beat. With the voice credit inside the channel title, it would have been back on the opening frames, so the channel title is again "Aravind Ravi · INFO 7375" and the voice credit is its own end-card line (outro patch `credit`).
- **P1 items:**
  - Done: 8 (gaps), 10 (B10's transcript and recap at hero size), 11 (B15 in three columns), 12 (poster frame 0; voice credit off the opening) and 13 (end card).
  - **Not done:** 9, scaling Methods and Evaluation content about 1.3–1.4× with a 34 px type floor. Those frames already span the full width, so it needs a per-scene re-layout, which didn't fit before the stop.
- **Speech-to-text (`film/project/gates/stt-full-master.txt`):** 732 of 732 words heard in the full film. One line differs: B06 "GitHub's" heard as "GitHub" (full film only).
  - Transcribed alone, B02's clip gives "the valves" for "evals" and B13's gives "clawed" for "Claude". Both are heard correctly in the full film.
  - This needs my ear, not a gate: if "evals" sounds unclear, it can be respelled for the voice, the way "Reed-back" was.
- **Result:**
  - `film/project/aravind-r-readback-project-film.mp4`, 3:58.5 (238.46 s), SHA-256 `8ed1366a…`, verified `ready`.
  - Freeze 2.1 %; −16.1 LUFS, −1.2 dBTP; no black frames or dead air; one ground colour at all 20 cuts.
  - Toolkit gates F, factcheck (81 rows), L, A, W, B (all 20 scenes), V (0/0 on the review cut and the clean master), T (21 of 21) and bookends all pass.
  - My overlap check: 20 of 20 scenes, 0 overlaps.
  - The new positioning audit passes: 110 of 110 test-case mentions are in Methods or Evaluation under the "test case" tag, and the summary has 0.
  - The tables are in `film/project/gates/GATES.md`.
  - Rebuilt from this master: `film/project/storyboard.png`, `film/project/style-frames/` and the contact sheets `film/project/gates/contact-*.png`.
  - Nothing is committed. That waits for my approval of this cut.
- **Cut approved ("Approve cut", Aravind).**

## 2026-11-23 — Project film, Phase 5: paperwork, commit and push (Claude Code; my route)

- **Paperwork:**
  - `film/project/CLAIMS.md`, `FACTCHECK.md`, `SHOTLIST.md`, `DESIGN.md` and `PROMPTS.md` describe the approved cut.
  - `SOURCES.md` has a project-film section.
  - The first review cut's records are kept in `film/project/gates/review-cut-1/`, and the earlier entries above point there.
  - The judgment-call entries, and anything drafted in Claude chat, are marked TODO for me to write (written later the same evening; see the entries at the end of this log).
- **Commit:**
  - A new branch, `project-film-aravind-r`, cut from `2cad8ba` (no merge or rebase of `origin/main`).
  - Only the project-film work goes in: `film/project/` (sources and records, plus the film via `git add -f`), the two outro patches, `FRICTIONAL.md` and `SOURCES.md`. The build caches (mp3, manim, clips, media, exports, _qc, _superseded) stay ignored.
  - No attribution trailers, checked with `git log -1 --format=%B` after the commit.
- **Push:** to my fork only (`fork`, aravindravi7/prompt-engineering-and-agentic-ai). No PR until I say so. This entry is part of that commit.

## 2026-11-23 — Project film, final fix pass (my requests; Claude Code made the changes)

- **My requests (Aravind):**
  - B01 opens "AI features ship against acceptance criteria a PM wrote."
  - B02 says "And where an eval is the launch gate, a misread criterion ships wrong behaviour at scale, with a passing score attached."
  - CLAIMS N01 and N05 match; N05 is a conditional POSITION with no trend claim.
  - B07's label reads "names the criterion behind a disagreement".
  - B15 shows "compute: this Mac" under "have", and "my human labels" under "planned" beside the open-weight model.
  - Re-voice B01 and B02 only. Commit and push by 22:45 ET, or keep `6aadb5a`.
- **Voice:** B01 and B02 re-voiced, same voice and settings. "eval" is heard as "eval", so no respelling. The other clips are byte-identical.
- **Scenes:**
  - B07's label changed.
  - B15's columns were re-measured: "AMI data · 10 meetings" fits on one line, the local model wraps to two, and compute lands on "here" ("Claude runs here").
  - B01's new timing opened a 3.04 s static stretch, so it gained two colour flashes, on "meant" and "and".
  - B01, B02, B07, B08, B15 and B16 were re-rendered; B08 and B16 open on B07's and B15's last frames.
- **Result:**
  - `film/project/aravind-r-readback-project-film.mp4`, 3:56.8 (236.79 s), SHA-256 `4d790803…`, verified `ready`.
  - Freeze 2.15 % (the end card only); −16.1 LUFS, −1.2 dBTP; no black frames or dead air; one ground colour at all 20 cuts.
  - Toolkit gates F, factcheck (81 rows), L, A, W, B (20 of 20), V (0/0 on the review cut and the clean master), T (21 of 21) and bookends all pass.
  - Overlap 0 in 20 of 20 scenes; positioning audit PASS (108 of 108); speech-to-text 728 of 728 words.
  - Tables: `film/project/gates/GATES.md`.
  - Committed as d3b87e9 on project-film-aravind-r and pushed to my fork; master SHA-256 4d790803…

## 2026-11-23 — Project film, B15 Ollama line and paperwork pass (my requests; Claude Code made the changes)

- **Ollama check (22:11 EST):**
  - `ollama --version` gives 0.40.17;
  - `/Applications/Ollama.app` is present;
  - Homebrew lists the cask `ollama-app`;
  - `ollama serve` is running;
  - `ollama list` shows no model, and there is no judge code in the repo.
- **B15:**
  - The planned line now reads "local open-weight model · Ollama installed, judge not wired". The narration is unchanged, so nothing was re-voiced.
  - B15 and B16 were re-rendered, and every gate was re-run with the same values: 3:56.8, freeze 2.15 %, −16.1 LUFS, −1.2 dBTP, A/W/B and overlap 20 of 20, Gate V 0/0, positioning 108 of 108, speech-to-text 728 of 728.
  - Master SHA-256 `535fe61b…`, committed as `8424a49`.
  - `film/project/EVAL-PLAN.md`'s Ollama status was updated to match.
- **Paperwork:**
  - My judgment-calls entry and the Claude (chat) entry went in word for word.
  - My feedback bullets, the Phase 0 resources, the header and the final-fix-pass commit line were corrected, and `SOURCES.md` was updated as I asked.
  - This entry and those edits are in the commit after `8424a49`, pushed to my fork. No PR.

## 2026-11-23 — Project film PR #54 opened (Aravind)
- I opened PR #54 myself: aravindravi7:project-film-aravind-r into nikbearbrown:main.
- Head at opening: 8fb0730. Final master SHA-256 535fe61b…, 3:56.8, built in commit 8424a49.
- **PR at opening** (recorded by Claude Code from the public GitHub API; `gh` isn't logged in on this Mac):
  - opened 2026-11-24 04:01:02 UTC (2026-11-23 23:01:02 EST);
  - 4 commits and 100 changed files (+41,442 / −3);
  - a local compare against `2cad8ba` gives the same 4 commits and 100 files, all under `fall-2026/aravind-r/final-project-film/`.
- **CI as the PR showed it** (recorded by Claude Code):
  - The "Python course" workflow runs `scripts/validate_course.py` on Python 3.11, 3.12 and 3.13. It started at 04:02:21 UTC and was still in progress at 23:03 EST, so it was not waiting for maintainer approval. GitHub listed the PR as "unstable" while the checks ran.
  - The same workflow fails on `main` itself: its last three push runs (`d0ef02a`, `8d8e92f9`, `0801bc2c`) all concluded "failure".
- **`scripts/validate_course.py` run locally on `8fb0730`** (Python 3.12.14, and again on 3.9.6): exit 1.
  - All 13 week lessons and the 13 integration tests pass.
  - The 17 findings are broken local links or non-Python files in other students' folders: deepak-s 11, suketh-p 2, and one each in nik-bear-brown, pavithra-p, sreevarshan-s and yudan-z. None is under `fall-2026/aravind-r/`.
- This entry goes in its own commit; PR #54 picks it up automatically.

## 2026-11-23 — Project film, my judgment calls (Aravind, my words)
Written 2026-11-23 evening, after the final fix pass; moved here so the log reads in order.
1. Film subject: Readback is the final project, so that's why the video was created for that.
2. Application-agnostic positioning: I didn't want people to mistake that Readback is applicable just for a meeting note taker application. So to emphasize that, I positioned it for any AI feature's acceptance criteria and kept the AMI meeting-recap feature as the test bench only.
3. PM vocabulary first: PM vocabulary would make the project easily relatable for PMs, who are the target audience for the project. I didn't want to make it sound too technical. I believe if you really understand something, or if you want people to understand your concepts, it's important to share it in a simpler language, which makes it relatable and understandable. I focussed on that aspect.
4. Cutting the section bar and full-sentence labels: I made sure only relevant and necessary information was kept on every page.
5. Consequences before mechanism: Before jumping into how it's built, it's very important to communicate the relevance, or the why, of the project. That's why I decided to focus on that first before getting into the solutioning and mechanism.
6. ES2010b as the real example: Using a real example from the test data was the right approach, rather than a synthetic one.
7. Softening the two flagged claims in the final pass: "Every AI feature" overgeneralised and the "launch gate" trend had no source in the repo. I didn't want unverifiable claims in the opening, which gets the most scrutiny, in a course that grades fact-checking.
8. Skipping P1 item 9 and B15's tight spacing: The video was looking good without that, and I didn't want to spend time on unnecessary fluff.
9. Listening checks: Whisper flagged B13's "Claude"/"clause" line and "Readback" on the first review cut; I listened, confirmed them and approved rewording and re-voicing. The speech-to-text slips logged on the final cut I left as logged.

Resources: I hold Anthropic and OpenAI API credits from other projects. I'll create project-specific keys at implementation time, which is why the film shows them as "account, not yet wired". OpenAI is the second provider. Ollama: Claude Code's checks at 05:19 and 15:50 EST found it not installed. I then installed Ollama 0.40.17 with Homebrew (brew install --cask ollama-app), and it's running. Outcome: Claude Code confirmed the install at 22:11 EST (`ollama --version` 0.40.17, `/Applications/Ollama.app`, Homebrew cask `ollama-app`, `ollama serve` running; `ollama list` empty). B15's planned line was updated to "local open-weight model · Ollama installed, judge not wired" and re-gated; new master SHA-256 535fe61b…, commit 8424a49.

## 2026-11-23 — Project film: what Claude (chat) contributed (Aravind)
Written 2026-11-23 evening, after the final fix pass; moved here so the log reads in order.
I used Claude.ai chat in my "Prompt Engineering & Agentic AI" project alongside Claude Code. It:
- recommended Readback as the film's subject over the job-search agent, mapped to the four-part brief;
- drafted the Claude Code prompt "Readback project film (four-part brief)" from my request;
- reviewed Claude Code's Phase 4 report and flagged honesty risks before Phase 5: B15 claiming resources not set up, human labels reading as AMI's, prior work not scoped to the tools I checked, the B13 "Claude"/"clause" adjacency, the Readback pronunciation, and the merged PR #18; it recommended the new branch from 2cad8ba;
- reviewed the first review cut and the revised cut frame by frame, from timestamped contact sheets plus ffmpeg freeze and silence detection, and listed the production issues by timestamp: the empty poster frame, the 0:09 credit, uniform ~1.15 s gaps, small type and dead zones in Methods and Evaluation, near-empty boundary frames, the small evidence beats, the B15 checklist, the end card;
- turned my feedback (removing the section bar, rubric vocabulary, cutting the clutter labels, consequences and long-term impact, application-agnostic positioning) into the P0/P1 revision prompts, and proposed the positioning-audit gate;
- on the revised cut, caught the missing compute line and the two unsourced opening claims, and drafted the final fix-pass prompt;
- listed what FRICTIONAL.md and SOURCES.md still needed, and drafted this prompt from my answers.
The decisions are mine. Claude chat never touched the repo; everything it drafted reached Claude Code through me.

## 2026-11-23 — Project film, documentation fix pass and appendix
Documentation fix pass and appendix (Aravind's requests; Claude Code made the changes; appendix reviewed by me).

## 2026-11-24 — Project film, B15 spacing re-layout (my request; Claude Code made the change)
B15 was re-laid out, with no wording change: a baseline grid; the heads 0.37 higher; "this Mac" 0.36 clear of the footer, against a largest row gap of 0.34; "local open-weight model" on one line, with the planned column's names at 32, the film's smallest size. B15 and B16 were re-rendered and every gate was re-run. Every value matches `535fe61b` except the SHA (now `37cbfaa6…`) and a positioning count corrected from 108 to 107, where the old table held a stale B11 row; the first `art final` of this pass wrote the master and it was then missing from `exports/landscape/` (cause not found), so `art final` was run again and gave the same SHA.
