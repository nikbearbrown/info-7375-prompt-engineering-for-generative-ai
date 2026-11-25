# Day-one findings (2026-10-14)

Fetched by Claude Code on 2026-10-14 with WebFetch, WebSearch, curl and the GitHub CLI. Each check has its own dated note in this folder, with the URL and only the few lines relevant to the claim. Quoted lines are as WebFetch returned them. WebFetch extracts page text through a summarising model, so check any line before quoting it on screen. No gap was filled from memory: where a page could not be fetched or did not say something, this file says so.

## 1. Subtitle Edit, AI Assistant (subtitle-edit.md)

- **What the source says:** The AI Assistant gives "AI help for the current line: fix errors, fit reading speed, change tone" and "works on the currently selected line only". Fit reading speed will "Rephrase the line shorter so it fits your maximum line length and characters/second settings, keeping the exact meaning". "Nothing changes until you press Apply to line." No accuracy figure.
- **Supports:** NARRATION B04 ("Subtitle Edit and Editsub offer AI that shortens one line when you ask"); PROJECT-BRIEF §2; plan §3 table row.
- **Contradicts:** nothing.

## 2. Editsub, AI shortening (editsub.md)

- **What the source says:** "Shorten lines, switch tone, fix typos, and retranslate cues with AI." "Shorten with AI" appears as a per-cue button in the page's mock-up. The page also says "Flags high CPS, long lines, overlaps, tiny gaps…" and "Snap overlaps, close gaps, pad short cues, and split long ones across the whole file." No accuracy figure.
- **Supports:** B04's first sentence; plan §3 row (per-cue "Shorten with AI", bulk timing fixes).
- **Partly supports:** B04 "In the tools I checked, shortening is something a person triggers, one line at a time." The per-cue button supports it. The fetched text doesn't say whether Editsub can shorten many cues in one action, so "one line at a time" rests on the mock-up rather than a stated limit.

## 3. EZTitles, QC and AI (eztitles.md)

- **What the source says:** "automated QC and direct delivery export"; "The QC pass that catches what the client would have flagged." Its Check Subtitles feature sets margins for reading speed and labels cues "Below reading speed" (too fast) and "Above reading speed". Its AI capabilities are listed as transcription, generated first versions of subtitles, machine translation and "reading-speed-aware segmentation". The fetched pages do not mention AI shortening. No accuracy figure.
- **Supports:** B04 "EZTitles runs automated QC that flags reading-speed problems"; plan §3 row on automated QC and reading speed.
- **Not confirmed:** the plan §3 row also claims "shot-change detection" and checks on "characters per line" for EZTitles. Neither appears in the pages fetched today. A search snippet describing shot-change snapping came from an EZTitles Netflix guide that wasn't fetched.

## 4. Published accuracy or meaning-change figures (accuracy-figures.md)

- **What was found:** none for Subtitle Edit, Editsub or EZTitles, either on their pages or in one web search. The search returned general academic work on subtitle compression only (FBK at IWSLT 2024; ACL W15-1818), not about these tools.
- **Supports:** B04's last sentence (CueGate "will publish how often its shortened lines changed meaning") as a difference; PROJECT-BRIEF §2 "I did not find a published figure of that kind for the tools I checked"; plan §3 point 3.
- **Resolves:** the re-check promise that PROJECT-BRIEF §2 used to carry, and plan §18 day-one item 2. Resolved 2026-10-14 (P4, P8 applied).
- **Limit:** one search plus three product pages. That isn't proof that no figure exists anywhere.

## 5. Netflix English TTSG and Timing Guidelines (netflix.md)

- **What the sources say:**
  - English (USA) TTSG: "Adult programs: Up to 20 characters per second", "Children's programs: Up to 17 characters per second", "42 characters per line".
  - General Requirements: "Minimum duration: 5/6 (five-sixths) of a second per subtitle event (e.g. 20 frames for 24fps)", "Maximum duration: 7 seconds per subtitle event", "2 lines maximum."
  - Timing Guidelines: "a minimum of 2 frames between them"; snap "within half a second past the shot change"; "set the out-time to two frames before the shot change"; "the out-time may be set to 12 frames after the shot change".
  - **Spaces:** none of the three Netflix pages fetched says whether spaces or punctuation count toward reading speed.
  - Subtitle Templates (a different document) gives template limits of 17 (adult) and 15 (children) CPS and says "Avoid condensing text unnecessarily and do not paraphrase."
- **Supports:**
  - Plan §8 profile values: max_cps 20, kids 17, max_chars_per_line 42, max_lines 2, min_duration_s 0.8333, max_duration_s 7.0, min_gap_frames 2, snap_window_s 0.5, gap_from_cut_frames 2. They're now confirmed against the primary pages, not only secondary ones.
  - NARRATION B03 "publish hard, numeric rules for subtitles: how fast a line can be read, the gap between lines, how timing behaves at a cut".
  - Plan §2 "avoid condensing unnecessarily and not to paraphrase".
- **Does not resolve:** plan §8's open question on `include_spaces`. The primary guide doesn't state it, and EZTitles shows that tools make it a setting. Resolved 2026-10-14 by rewording the plan comment to say so (P7 applied).
- **Not supported by a Netflix page:** NARRATION B03 "Break them, and the file gets flagged." and PROJECT-BRIEF §2 "files that break them are flagged in automated QC". The four Netflix pages fetched say nothing about QC, flagging or rejection. Only the secondary Gotham Lab guide says "files that fail to meet these specifications are rejected before they reach a human reviewer" and "Reading speed is one of the most common reasons subtitle files are rejected by Netflix QC." Proposed attribution at STOP A.
- **Not modelled in the plan:** the Timing Guidelines also allow an out-time "12 frames after the shot change". The plan's §8 profile and §9.2 solver don't model that option. It's a design note, not a film claim.

## 6. Blender open movie with an English subtitle track (blender-open-movie.md)

- **What the sources say:** Tears of Steel (2012) has an English file at https://download.blender.org/demo/movies/ToS/subtitles/TOS-en.srt (HTTP 200, 4,764 bytes, last modified 17 Oct 2012, 76 cues). mango.blender.org/about says "Tears of Steel is licensed as Creative Commons Attribution 3.0". The folder's copyright.txt (CC BY-ND 3.0) covers only the soundtrack. No page fetched states a licence for the .srt files themselves.
- **Supports:** NARRATION B09 "on the English subtitles of an open Blender film" (a "will" statement), with Tears of Steel as the candidate; plan §11 corpus plan.
- **Open:** the subtitle file's own licence. Plan §16's risk row ("No subtitle tracks with usable licences") stays a real risk until it's confirmed. B09 needs no change.

## 7. Name check (name-check.md)

- PyPI `cuegate`: 404. GitHub: no repository named cuegate; DeepakKTS/cuegate: 404.
- **Resolves:** plan §18 day-one item 5.

## 8. OOONA (ooona.md), listed in plan §18 day-one item 1

- The support page could not be fetched (only its title loaded). Search listings only, nothing confirmed. OOONA is not named in the film. Proposed: record it as not checked in the plan's day-one item.

## 9. Reallocation Engine PR #25 (for B11 and PROJECT-BRIEF §7)

- **Checked:** 2026-10-14 with `gh pr view 25 --repo nikbearbrown/the-reallocation-engine` and `gh api …/contents/…?ref=edbac80…`.
- **PR facts:** title "opt-start-window: OPT start-window timeline gate for a December graduate (RUNNABLE-SAMPLE)"; author DeepakKTS; state OPEN, not merged; created 2026-10-03; head commit edbac80604162750743e04a2da7fa85c734c0780. Every commit lists DeepakKTS and Claude Opus 5.5 (noreply@anthropic.com) as co-authors.
- **Timeline gate, quoted:** `scripts/contrib/2026fa/deepakkts-opt-start-window/lib/gate.mjs`, lines 55–75:
  - lines 55–60: "A zero timeline gate must hold the composite at or below the scorer's own closed-gate threshold (CONFIG.gate_zero), no matter how strong the votes are."
  - line 61: `export function assertClosedGate(composite, threshold, detail) {`
  - lines 68–70: `if (composite > threshold) {` … `` `Timeline is behaving as a vote, not a gate: timeline=0 with strong votes produced composite ${composite}, above the closed-gate threshold ${threshold}.` ``
- The PR also adds `lib/timeline.mjs` (the Chapter 10 timeline factor computed from intake dates) and `test/opt-start-window.test.mjs`, plus a BROKEN-additive-gate-scorer fixture the gate is meant to catch. Neither the tests nor the code were run today.

## 10. PySceneDetect on false cuts (pyscenedetect.md), for NARRATION B10 and plan §16

- **What the source says:** the detector docs acknowledge "false detections in situations such as fast camera motions" and "camera movement". ThresholdDetector catches "slow fades so long as an appropriate threshold is chosen". `min_scene_len` blocks a new cut for a set time after one.
- **Supports:** plan §16 / PROJECT-BRIEF §6 response ("an adaptive detector with a minimum scene length"); B10's risk in general (cut detectors make false detections).
- **Not supported by this page:** "flashes" specifically. The page doesn't mention flashes. B10 says "Fades and flashes fool cut detectors" as a flat statement. Proposed wording at STOP A.
