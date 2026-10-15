# FRICTIONAL — dated log

Who did what: **[Me]** is my own action or decision. **[Claude]** is work Claude Code (Opus 5.5) did in the Claude desktop app at my request. **[Both]** means Claude proposed it and I decided. I can explain every entry.

## 2026-10-14
- **[Claude] The toolkit clone failed with "Filename too long".** On Windows, cloning brutalist.art into a deep folder failed. Re-cloning to a short path with `git -c core.longpaths=true` worked: 14,298 files at commit `4115560`.
- **[Claude] The toolkit scripts had CRLF line endings.** `art` and `setup` were checked out with CRLF line terminators because global `core.autocrlf=true` is set on this machine. The plan was to re-clone with `core.autocrlf=false` inside WSL. That later worked.
- **[Claude] ffmpeg was not installed** on Windows (Python 3.12.5, Node 22.12.0 and git 2.47.1 were). The film could not render on Windows.
- **[Claude] The toolkit defaults conflict with "narrate as yourself".** The show-tell and ai-explainer skills require an "in for Bear" greeting, OUTRO-LOCK.md hard-codes the instructor's handle, and `bookend_check.py` checks the outro handle against `channel_title`. Plan: set my own persona and `channel_title`, avoid the `claude-liam-*` slug, and put no person on screen.
- **[Claude] The beat sheet is generated, not hand-written.** Show-tell expects a `make_sheet.py` to produce `beat_sheet.json`, so `film/make_sheet.py` was written for that.
- **[Claude] One of Claude's tests expected the wrong number.** The evidence-validation test expected 4 errors, but the code correctly reported 5: the bad record had four problems, not three. Claude fixed the test, not the code.
- **[Both] Two known misses are kept deliberately.** INC-016 and INC-017 are cases the rules get wrong. They stay in the eval report as misses instead of being tuned away.
- **[Claude] The labels are not independent.** Claude wrote both the rules and the labels. Some test cases should be written by someone else.

- **[Me] Target role chosen: supply chain manager.** The project is framed around lot holds and release decisions, which is where quality and supply meet. At this point I described coding as mostly new to me, and said I hadn't combined supply chain with AI before.
- **[Me] Code not yet reviewed.** Claude Code wrote it. The film and the brief said so until I had reviewed it.

- **[Both] "Why this project" revised from "mostly new" to "a mix".** After reading my résumé, Claude pointed out that it shows more existing skill than I first said: SAP supplier work, Six Sigma Green Belt, and earlier work on human-in-the-loop decision tools. Only the degree, the certification and the analyst role are cited. The résumé itself is kept out of the repository. **[Me] Confirmed 2026-10-14:** the new wording is accurate.
- **[Claude] Alternatives researched.** The candidates were SAP QM usage decision (QA11) and a free 8D non-conformity spreadsheet. The film's "why care" beat stayed blank until I compared them myself.

- **[Me] Compared against SAP QM: StopLine does not beat it yet.** From my SAP experience, the usage decision already checks the recorded results, the lot and the timing, and it can refuse or warn. Both tools check structured data only. I chose to say this plainly in the film rather than invent a difference. The next real test is whether checking written claims adds anything.

- **[Me] Code review, exercise 1 (changing a value).** I changed INC-005's bore mean from 12.08 to 12.04, and the result moved to ACCEPT FOR REVIEW. That is correct, because 12.04 is inside the limit. One test failed, because the label still expected HUMAN REVIEW: the expectation was wrong, not the code. I had also left the claim *text* saying "12.08 mm" while the value said 12.04, and StopLine didn't notice. That is the same blind spot as INC-016. **[Claude]** put the original values back at my request, and all 12 tests pass.

- **[Me] Code review, exercise 2 (removing a rule).** I deleted `severity_gate` from `ALL_CHECKS`. INC-006, a critical crack with clean paperwork, went from HUMAN REVIEW REQUIRED to ACCEPT FOR REVIEW, and the labelled-case test failed for INC-006. This time the code was wrong, not the label, and the test caught it. I put the rule back, and all 12 tests pass. Weakness: INC-006 is the only case covering this rule.
- **[Me] Code review, exercise 3 (explaining the misses).** INC-016: the 400 quarantined units are quoted correctly, but the lot size of 1,200 exists only in free text, so no check can compare them. INC-017: the claim cites sample size, not defects, and that record's spec has no defect limit, so 2 defects get through. In both cases a check is only as strict as the information and limits it is given. Possible fixes: for a release, require `units_in_lot` and require it to equal `units_quarantined`; treat a missing limit as a gap (NEEDS MORE EVIDENCE) instead of no limit. **[Claude]** corrected one mistake in my answer: INC-003 is caught by `claims_match_evidence`, not by the spec limit, because `within_spec` does not apply to rework.

- **[Me] Review complete.** I have reviewed all 11 checks. **[Claude]** then updated the film, brief, README and SOURCES, which had said the code was unreviewed.

- **[Me] Moved the project to a permanent folder (OneDrive). [Claude]** wrote `film/wsl_setup.sh` to run inside Ubuntu. It installs ffmpeg, Node 22 and the cairo/pango libraries, clones the toolkit with Unix line endings, and runs the toolkit's own `./setup --install`. Claude also added `.gitattributes` so the script keeps Unix line endings.

- **[Me] WSL: Ubuntu would not install at first.** `wsl --install` said virtualization was not enabled, even though it was on in the firmware and Virtual Machine Platform was enabled. A restart fixed it.
- **[Claude] The film script was restructured into the show-tell format.** With the toolkit's four fixed bookends, the film would run past 4 minutes. `bookend_check.py` allows exempting the Your Turn section, so Claude dropped it and the terms card. The opening typing animation uses my own greeting, and the outro uses my title and handle. The narration was shortened to an estimated 3:41.
- **[Claude] Beat B03 became a drawing.** It was planned as a screen capture, but the skill only allows drawn scenes. B03 now redraws three real lines from `reports/` with the caption "real run · synthetic data".
- **[Claude] The pre-render checks pass.** factcheck, bookend, beat-lint and the Gate A static check all pass on all 11 scenes (`film/gate_reports/pre_render.txt`).

- **[Me] Ran the setup script in WSL. [Claude]** confirmed it worked: Manim 0.20.1, Kokoro 0.4.7, ffmpeg 8.0.1 and Node 22, with the toolkit's `art` script on Unix line endings. The readiness check warned about ElevenLabs references in the toolkit's own example folders. That isn't about my reel, so it was ignored.
- **[Claude] Narration generated: 13 clips, 2:58 total.** That is shorter than the 3:41 estimate. The outro was padded with 1.0 s of silence (BOUT is now 7.85 s).
- **[Claude] The pronunciation check needed a workaround.** faster-whisper could not open the mp3 files (a PyAV version mismatch, `metadata_errors`), so the audio is decoded with ffmpeg first. The transcripts match the script. Kokoro says my name roughly as "Shayam Sundar Jayaram-and Gopalakrishnan". **[Me]** That is close enough to keep.
- **[Claude] First low-res frames: two scenes needed fixes.** In B03 the real-output text ran past the panel edge. B08's crates, rope and gate overlapped. B08 was redrawn as two rows of six crates with the rope around four of them, then re-rendered and checked.

- **[Claude] First 4K render: all 11 scenes rendered, and the layout audit came back CLEAN.** The two Remotion bookends failed because headless Chrome was missing Linux libraries (`libnspr4.so`). Claude added them to `film/wsl_setup.sh`.

## 2026-10-15
- **[Me] Installed the libraries.** I first ran the install in Windows PowerShell, where `sudo` is disabled. Running `wsl -d Ubuntu -- sudo apt-get install ...` worked, and the bookends then rendered.
- **[Claude] Gate V failed on all 26 frames ("edge-bleed"), but not because of my scenes.** Ubuntu's ffmpeg has drawtext, so the toolkit burned a running timecode into the top-right corner of the review cut. Gate V excludes only the bottom-left label strip, so it read the timecode as content crossing the edge. Claude set the toolkit's own switch `ART_NO_DRAWTEXT=1` for the review cut (`film/wsl_reel.sh run`), and Gate V then passed: 26 frames, 0 defects. The master never carries the timecode.
- **[Claude] Gate T failed on B00 and B09** (smallest text run 40 px against a 41 px floor). Enlarging the labels did not help, because the "text" was the scribbled lines on the evidence pages. Claude made the scribbles taller (amp 0.07 to 0.11) and re-rendered B00, B01, B05 and B09. Gate T now passes on all 13 beats (smallest run 58 px).
- **[Claude] Master exported: `film/stopline-pitch.mp4`, 2:59, 3840×2160, 8.8 MB.** Checked with ffprobe; the SHA-256 is in the README. The toolkit's "SKIN LINT: COLD OPEN LAW" line is advisory, and the show-tell skill says to expect it when the cold open is exempted.
- **[Me] Watched the full film.** I checked every claim against what exists, and it is accurate.
- **[Both] Pre-submission review.** Claude reviewed the submission against the rubric. The weakest area is "unique value": StopLine doesn't beat SAP QM yet, which I chose to keep honest. Claude also flagged that this log said "I" for work Claude did, so I added these tags.
- **[Both] The film is not in the GitHub folder.** The course repo's `.gitignore` excludes `*.mp4` ("keep generated audio/video out of Git"), so git skipped it without warning. This conflicts with the assignment's file list. I chose to follow the repo rule: the film is in the Canvas ZIP, and the README gives its SHA-256.
