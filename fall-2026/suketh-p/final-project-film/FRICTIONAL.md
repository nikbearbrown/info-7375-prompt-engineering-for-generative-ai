# FRICTIONAL — honest log · Final Project Pitch Film

Suketh Reddy Produtoor · INFO 7375 · Fall 2026

## How this log is organised

The course rule is plain: an AI may organise notes, but the experience must come from the student. So:

- **My entries** are written by me, dated, and placed here word for word. They were written *while* the film was being
  made (entry 1 before anything was built, entry 2 after the script, entry 3 after the first render, entry 4 before
  submission), because my Assignment 3 feedback said my entries were short and came after the build.
- **The factual timeline** is reconstructed by Claude Code from the chat and file timestamps. Times are Eastern. A
  time is given only where a file or a command output fixes it.
- **Claude Code's contributions** are listed separately at the end, with what I accepted, changed or rejected.

---

## My entries

### Entry 1 — 2026-10-14, before the film was built (choosing the project, my skills, my prediction)

*Pasted by me into the chat on 2026-10-14, before 15:09 EDT, as answers to six questions Claude Code asked. Placed here
unchanged. I wrote it myself, based on my résumé, project records and the choices I supplied (my statement to Claude Code,
2026-10-14). I chose to keep the employer figures in it.*

1. Why this project, and why I chose to say F-1 on camera
I chose this project because I want to know whether a role deserves my time before I start tailoring an application. A relevant ML title and a company’s sponsorship history are useful signals, but the actual posting can change the decision.
That gap showed up in Assignment 3. The review found experience requirements or graduate exclusions in six of eight postings that initially looked relevant. After reviewing the findings, I kept all eight held because important evidence was still unresolved.
I chose to say I’m on F-1 because it explains why I need to examine both role eligibility and sponsorship evidence. It gives the project a concrete purpose. I want an agent that helps me make that decision with the source text in front of me.

2. Skills I already have, their proof, and what is new

* Production ML engineering and Python — Amazon. I worked on shipment ETA inference, feature validation, retraining pipelines, and controlled A/B experiments. One concrete example is sustaining below 180 ms p99 inference latency against a 200 ms SLO using cached features and bounded fallbacks. That experience matters here because successful execution also has to include predictable failure behavior.
* Data contracts and human review — Vertex. I worked with 47 GxP-regulated Snowflake datasets, enforced assertion tests before publication, and routed low-confidence retrieval matches to human sign-off. Those are practical foundations for checking evidence and stopping when it is insufficient.
* Agent orchestration and evaluation — AgentOS. My open-source runtime includes typed provider interfaces, deterministic failover, budget ceilings, a kill switch, and append-only logging. Its evaluation harness incorporates statistical regression checks within 285 CI tests. I already have experience building controls around model behavior.
* Verification and judgment — Assignment 3. I personally reran the 36 tests, reproduced the sample, exercised the broken authorization profile, and compared the source CSV with the report. Claude Code wrote the implementation. My contribution was reviewing the evidence, choosing the rules and holds, and performing the recorded checks.

The new challenge is interpreting job requirements while preserving their meaning. “Preferred,” “required,” and “either qualification pathway” need different representations. I need to develop a labeled posting dataset, evaluate extraction and interpretation separately, and measure both unsupported clearances and false exclusions. Presenting those distinctions clearly in a short film is also something I still need to demonstrate.

3. Alternatives I have actually used or looked at
I have used LinkedIn for my job search. I also worked with the Reallocation Engine in Assignment 3 and reviewed its sample report, rules audit, and posting review on October 2.
The specific limitation I can substantiate comes from that A3 work: matching the title and finding sponsorship history did not establish that the posting fit the applicant. Requirements inside the description could change the recommendation substantially.
That is the improvement I want in my own workflow: each extracted requirement shown beside its exact source sentence, with ambiguity left visible for review. My comparison with LinkedIn is still incomplete; I need to document its relevant capabilities before claiming that this project offers something existing tools do not.

4. One thing I would change in the draft brief
I would make the applicant’s documented background an explicit input to the requirements check.
I am targeting new-grad ML/AI roles, but I also have roughly two and a half years at Amazon and six months at Vertex. An experience requirement needs to be compared with that evidence. My search category alone cannot determine whether I meet it.
The A3 eight-posting review used a fictional profile without documented work-history evidence. Its findings demonstrate the weakness of title-based screening; they do not establish that the same six postings rule me out.
I would therefore preserve education-and-experience pathways separately, as in the PathAI example, and require an evidence-backed comparison before recommending exclusion.

5. My prediction: what will be hardest in making the film
I expect the hardest part to be making an interpretation error visible.
A quotation can be authentic while the conclusion drawn from it is wrong. If the agent finds “five years preferred” and treats it as mandatory, a green “quote found” indicator could make the output look more trustworthy than it deserves.
I want the film to show one example clearly: the original sentence, the extracted interpretation, and the reason the agent proceeds or stops for my review. The viewer should be able to spot the mistake without needing to understand the implementation.
I also need to keep the project’s stage clear. The A3 evidence exists; the proposed posting-reader agent has not been built. Any sketch of its future output should be identified as a sketch.

6. Voice and title
Voice: am_eric. I want conversational, measured narration that gives the viewer time to read the evidence.
Title: Fine Print. It fits because the information that changes my decision often appears inside the requirements, beneath a title that initially looks promising.

*Evidence and what came of it (added by Claude Code):* point 4 changed the design: the brief and the film now compare
each requirement with the applicant's documented background, and the repository will use a fictional profile (B05).
Point 5 became beat B04, the constructed "5 yrs preferred" example. The "285 CI tests" in point 2 did not match
AgentOS's public CI (run of 2026-09-19: 440 collected, 439 passed, 1 skipped), so the film names no test count
(FACTCHECK row 29). The internal Amazon and Vertex figures are not in the film or the brief.

### Entry 2 — 2026-10-14, reviewing the script

*Written by me and sent to Claude Code in chat on 2026-10-14 (between 16:10 and 18:43 EDT); placed here unchanged.*

For this review, I compared the narration with the project brief and the recorded A3 work. The checks covered attribution, existing versus proposed functionality, the six-of-eight finding, and the comparison with my documented background.

I want to keep the attribution that Claude wrote the A3 implementation while I chose the rules and performed the recorded checks. I also want to keep the required-versus-preferred example and the separate evaluation of false exclusions and unsupported clearances.

The wording I want changed is “the model’s until I approve it.” Approval should be a separate field, with the model’s contribution still visible. I would also clarify that the offline demonstration uses recorded outputs. These changes make the script more precise about what the evidence establishes.

*What came of it (added by Claude Code):* B07 now says "A value the model proposed will still say source: model, and my
approval will be recorded beside it, as its own field", and shows both tags; B09 now says the no-key demo "replays recorded
model outputs"; PROJECT-BRIEF §4 was changed to match.

### Entry 3 — 2026-10-14, reviewing the first render

*Written by me and sent to Claude Code in chat on 2026-10-14, with the change list below; placed here unchanged.*

I reviewed the render using frames across its full timeline and a transcription of its complete soundtrack. This entry records that review.

My earlier prediction was that a genuine quotation could look convincing even when its interpretation was wrong. The rendered example communicates that distinction: the quote check passes, while the reading of “preferred” as “required” is rejected. I want to keep that scene.

The review also found that the approval graphic replaces “model” with “approved.” I want both labels retained so the picture matches the intended provenance rule. I would keep the “constructed · not built” labels and the closing separation between existing A3 evidence and future Fine Print work. Name pronunciation remains a check to complete against the guide I supplied.

**My change list for the film** (sent with entries 2 and 3, unchanged):

I want to keep the overall structure, especially the example where “five years preferred” is incorrectly read as required. It makes the project’s main failure mode understandable.

I would make these changes:

⚬ Around 0:30: identify the fictional applicant used in the A3 review. The six-of-eight finding should not imply that six postings disqualified me personally.
⚬ Around 1:46: preserve the model’s source label after approval. Show “source: model” alongside “review: approved.” My approval records a decision; it does not change who generated the value.
⚬ Around 2:08: explain that the no-key demo replays recorded model outputs. That makes the demonstration’s scope clear.
⚬ B08: replace “comparison not done yet” with the specific LinkedIn findings below, crediting my research.

For my name, use the pronunciation guide I supplied: सुकेत रेड्डी फ्रंदटूर. Both the introduction and closing should be checked against that pronunciation before marking them correct.

*What came of it (added by Claude Code):* B01 now names "Arjun Rao, a fictional applicant with no work history on file" and
its stamp says "fictional applicant"; B07 keeps "source: model" and adds "review: approved"; B09 mentions the recorded
outputs; B08 is my LinkedIn comparison, in my wording (`evidence/linkedin-check-2026-10-14.md`). For my name, Kokoro's
Hindi phonemizer turned my Devanagari guide into phonemes that am_eric speaks (`name_voice.py`); I listened to the
candidates and approved the intro ("This has perfect name pronunciation of mine"). The outro uses the same phonemes; I
check it in the final film (entry 4).

### Entry 4 — 2026-10-14, before submission

*Written by me and sent to Claude Code in chat on 2026-10-14 (after 19:00 EDT); placed here unchanged.*

Entry 4 — Before submission, October 14
Before submitting, I confirmed the title, narration voice, decision to mention F-1, and retention of my employer experience figures. I also supplied my name’s pronunciation guide. I performed a read-only review of FACTCHECK and the updated project records.
The updated table records the corrections I requested: identifying the fictional A3 applicant, preserving “source: model” alongside “review: approved,” and explaining that the offline demo replays recorded outputs. Those distinctions matter because the film should accurately describe both the evidence and the project’s current stage.
I still need to personally watch the revised 195-second master with sound, especially the closing pronunciation and the changed scenes. I have not independently repeated every source check in FACTCHECK. The AgentOS test counts also need version context: entry 1 mentions 285, while the recorded CI result lists 439 passed and one skipped. Fine Print’s extraction accuracy and handling of ambiguous requirements remain unverified because the agent has not been built.
For Update 1, due November 5, I will build one working slice: read one allowed public posting, extract requirements with verbatim quotes and required/preferred labels, verify the quotes, save the evidence, and stop at the human review gate. I will include a test that rejects a one-word quote alteration and a case showing that a valid quote can still be interpreted incorrectly. The update will report what actually ran, what failed, and what remains unresolved.

*Update, same message (my words in chat, 2026-10-14):* "Final cut is absolutely perfect." *My go-ahead to post it:* "Yes, you
do that." *(The submitted commit's hash is in the Canvas submission, not here: a commit cannot contain its own hash.)*

---

## Factual timeline (reconstructed by Claude Code; Eastern time)

| When | What happened | Evidence |
|---|---|---|
| 2026-10-06 02:43 | `Assignment 4/` already existed, empty (folder timestamp) | file system |
| 2026-10-13, early | I asked Claude Code to create the Assignment 4 folder (it existed), pasted the assignment and asked to start, aiming for full marks | chat |
| 2026-10-13, before 00:38 | I chose: the posting-reader agent grown from my A3 recipe; target role new-grad ML/AI engineer; Kokoro narration of my own script; and **"Say I'm on F-1"**, which was not the option Claude Code recommended (it suggested "international student" only) | chat (answers to four questions) |
| 2026-10-13 00:35 | Fresh clone of `nikbearbrown/brutalist.art` at `519fcbb` (it has the `show-tell` skill; the older checkout did not) | `brutalist.art/.git` timestamp |
| 2026-10-13 00:38–00:40 | `./setup --install` installed everything, then exited 1 at its own ElevenLabs guard, which flags 10 files inside the toolkit's `youtube/` folder. Every feature was re-checked by hand: ready | `evidence/toolkit-setup-2026-10-13.txt` |
| 2026-10-13 00:43 | My A3 branch, fresh clone at `95d4982`: 36 tests OK. PR #12: open, no review | `evidence/a3-tests-rerun-2026-10-13.txt`, `evidence/a3-pr12-state-2026-10-13.txt` |
| 2026-10-13 00:46 | Six Kokoro voice samples made for me to choose from | `voice-samples/` (not submitted) |
| 2026-10-13, ~00:50 | I shared my Canvas feedback for Week 1 (24/25: my own reflections were unwritten) and A3 (88/100: status claim vs untyped proposals; defect D9; Frictional entries short and after the build, decisions mostly picks among AI options) and asked for zero mistakes | chat (screenshots) |
| 2026-10-13, after that | Claude Code re-checked its own draft brief and fixed three of its errors: it had said my A3 prototype uses a `model-judgment` label (it uses only `record` and `your-input`); it had dated the Codex review 09-30 and said all eight were read through the API (09-29 Eastern; OpenAI's through embedded page data); it had said no title showed the problem (PathAI's title has "II") | `PROJECT-BRIEF.md` history in this log |
| 2026-10-14, before 15:09 | My entry 1, voice `am_eric`, title "Fine Print"; I shared my résumé for reference only (not copied anywhere) | entry 1 above |
| 2026-10-14 15:09 | Claude Code checked AgentOS: public, Apache-2.0; README lists budget controls, permissions, kill switch, audit logging; CI 2026-09-19 collected 440 tests, not 285 | `gh` reads, FACTCHECK row 29 |
| 2026-10-14 15:17 | Pronunciation check: faster-whisper 1.2.1 cannot open audio with the installed PyAV 19 (`metadata_errors` argument). Re-run with ffmpeg decoding. Two lines reworded ("either-or paths" was heard as "pass"; "meaning" as "meeting") | `evidence/whisper-check-v1-failed-av-metadata_errors.txt`, `evidence/whisper-check-v1.txt` |
| 2026-10-14 15:19 | Script draft 1 (3:12) sent to me with the two bookend audio files | `SCRIPT-REVIEW.md` (not submitted) |
| 2026-10-14 15:22–15:34 | Low-resolution stills of all 14 drawn beats. Fixes: a cross touching text (B04), a tag over a word (B07), tally marks that would have read as invented error counts (B10), a large black panel the toolkit's GATE T is known to misread as text (B11), two lines that meant nothing (B05, B13). One re-render hung for 10 minutes: Claude Code passed all scene names as one argument (zsh does not split words), and Manim waited for keyboard input; stopped and re-run | stills in Claude's scratchpad |
| 2026-10-14 15:35–15:37 | Fact-check pass, three narration corrections: B00 "In my last assignment" → "Earlier this term …"; B07 "My last prototype" → "My earlier prototype"; B08 "Fine Print reads" → "will read" (present tense for something not built). B05 now says "documented background", my word | `FACTCHECK.md` rows 6, 23, 26 |
| 2026-10-14 15:38 | Gate A static pre-audit 14/14 clean; first `art run` at 2160p started | `gate-reports/art-run-1.log` |
| 2026-10-14 15:42 | First review cut: all 17 slots filled, Gate V 0 blockers / 0 major. Looking at the contact sheet showed the outro card reading **"@NikBearBrown"**: the toolkit's `ClaudeTitleOutro` hard-codes the instructor's handle and ignores the handle we passed. The assignment forbids the instructor's credit line, so the outro became our own drawn beat | `qc-sheet.png`, `gate-reports/art-run-1.log` |
| 2026-10-14 15:45 | Gate A rejected the new outro ("shapes never change"); a rule line was added. Gate W skips any class not named like `B07_Foo`, so it was run by hand on a copy renamed `B14_Outro`: clean | `gate-reports/art-run-2.log`, `gate-reports/gate-w-BOUT_Outro-manual.txt` |
| 2026-10-14 15:46–15:53 | `art final` blocked three times by GATE T on the terms card (BDEFS): the smallest text run measured 40 px against a 41 px floor. Removing the footer label did not fix it, nor did rewording. GATE T's own detector, run on the midpoint frame, showed why: letter runs with no ascender ("wor" in "work", "em" in "employers") in the card's fixed 48 px text are 40 px tall at 4K. Rather than patch the toolkit or the gate, the card was dropped and each term is defined where it is first spoken (show-tell law 3); B00 and B07 were re-voiced | `gate-reports/TYPECHECK-1…3-*.md`, `art-final-1…3.log` |
| 2026-10-14 15:56 | `art final`: **GATE T PASS**; master written (186.0 s). Master check (render integrity), loudness, sharpness and caption checks: all PASS | `gate-reports/art-final-4.log`, `MASTERCHECK.md`, `LOUDNESS.md`, `SHARPNESS.md`, `SRTCHECK.md` |
| 2026-10-14 15:57 | Looking at the master at 85% of each beat: in five beats (B00, B01, B04, B07, B08) the key picture landed in the last half-second, too late to read. The gates cannot see this. The cues were moved one sentence earlier and the five beats re-rendered | `scenes_body.py`; frames in Claude's scratchpad |
| 2026-10-14 16:02 | `art final` again: GATE T PASS; all master checks PASS; master SHA-256 `f3d847f9…5758`. Film sent to me for review | `gate-reports/art-final-5.log`, README.md |
| 2026-10-14, 16:10–18:43 | I watched the film and sent entries 2 and 3, a change list (B01, B07, B09, B08), my LinkedIn check of two postings, my name's pronunciation in Devanagari, and that I wrote entry 1 myself and keep its employer figures | entries 2–3 above; `evidence/linkedin-check-2026-10-14.md` |
| 2026-10-14 18:43 | Name candidates: a Hindi Kokoro voice reading my guide exactly as typed (for reference), and am_eric speaking phonemes that Kokoro's Hindi phonemizer made from it. I approved the am_eric intro by ear | `voice-samples/name/` (not submitted); `name_voice.py` |
| 2026-10-14 18:44–18:51 | My changes applied: B01 names the fictional applicant; B07 keeps "source: model" beside "review: approved"; B09 says the demo replays recorded outputs; B08 is my LinkedIn comparison. Gate A warned that a B07 label ran past the safe area (moved); Gate B, in strict mode, refused B08 until its label was inside the safe area (made smaller) | `gate-reports/art-run-7.log`, `art-run-8.log` |
| 2026-10-14 18:51–18:56 | Looking at the frames again: a grey tag overlapped "review" in B07, and B08's "unknown" mark came in the last half-second. Both fixed using measured text widths and an earlier cue. Final master: 195.0 s, GATE T PASS, master, loudness, sharpness and caption checks PASS, SHA-256 `75acbe18…b1cf` | `gate-reports/art-run-9.log`, `art-final-7.log`, README.md |
| 2026-10-14 19:00 | Final pronunciation transcript of every beat; course-CI checks (Python files parse; no .js/.ts/.tsx; local links) pass on the staged folder; final cut sent to me | `evidence/whisper-check-v2-final.txt` |
| 2026-10-14 19:00–19:09 | I watched the final cut ("Final cut is absolutely perfect."), wrote entry 4 after a read-only review of FACTCHECK, and said yes to posting it | entry 4 above |
| 2026-10-14, after 19:09 | Posting: the same staged folder goes into the Canvas zip and into `fall-2026/suketh-p/final-project-film/` on my fork's branch `final-project-film`, with a pull request to the course repository (the link and the commit hash are in my Canvas submission). The MP4 stays out of Git: the course repository's `.gitignore` excludes all MP4s ("Keep generated audio/video out of Git"); it is in the zip, and README.md gives its SHA-256 | `submission/stage_submission.sh` (not submitted) |

---

## Claude Code's contributions, and what I did with them

- **Claude Code did:** researched the assignment, the final-project spec (posted 2026-10-11, which requires the project to
  be agentic) and the classmates' pitches already posted; re-ran my A3 tests; drafted `PROJECT-BRIEF.md`, the script,
  `make_sheet.py`, `scenes_body.py` and every other file in this folder except my entries; ran the toolkit and its gates.
- **I decided:** the project, the role, the narration voice, the title, and to say I am on F-1 (against Claude's
  suggestion). I added the comparison with the applicant's documented background (entry 1, point 4), which Claude's draft
  did not have. After watching the film I changed four beats (entry 3's change list): the fictional applicant named in B01,
  approval kept as a separate field from the model's source label in B07, the recorded-outputs demo in B09, and my own
  LinkedIn comparison in B08. I supplied my name's pronunciation and approved the voiced result.
- **Accepted / changed / rejected:** see entries 2–4.
