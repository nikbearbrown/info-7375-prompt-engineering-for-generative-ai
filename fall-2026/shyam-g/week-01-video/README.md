# Tokens, Not Words

Student: **Jayaraman Gopalakrishnan Shyam Sundar**<br>
Course: INFO 7375 — Prompt Engineering and Generative AI<br>
Concept: The unit is a token, not a word — and why that can trip up letter-counting prompts.<br>
Why: A tiny spelling task exposes the difference between token-level representation and a verified character-counting operation.<br>
Persona: Dunkin — practical, punchy, technically grounded; no brand affiliation or logo.<br>
Runtime: **170.000 seconds** (2 minutes 50.000 seconds), as measured by FFprobe. The user's later request for exactly 2:50 supersedes the original 3–4 minute preference.<br>
Video: `Week01_Tokens_Not_Words.mp4` — 1920×1080, 24 fps, H.264 video, AAC narration.<br>
Captions: matching `.srt`; each cue is aligned to an actually synthesized narration segment.

## Watch and inspect
Open the MP4 in a normal video player. Put the SRT beside it and enable subtitles if desired. Read `beat_sheet.json` for narration, visual descriptions, measured durations, and per-segment cues. `qc/contact-sheet.jpg` shows three actual frames from each scene. See `qc/REVIEW.md` for the review performed.

## Rebuild in this workspace (PowerShell)
Run these commands from the `submission` folder:

```powershell
$env:PYTHONIOENCODING = 'utf-8'
$env:TIKTOKEN_CACHE_DIR = (Join-Path (Split-Path -Parent $PWD.Path) '.tokenizer-cache')
& ../.venv/Scripts/python.exe measure_tokens.py
& ../.venv/Scripts/python.exe prepare.py
& ../.venv/Scripts/python.exe build.py audio --speed 1.25
& ../.venv/Scripts/python.exe build.py fit
& ../.venv/Scripts/python.exe build.py render
& ../.venv/Scripts/python.exe build.py assemble
& ../.venv/Scripts/python.exe build.py verify
```

For a fresh extracted copy on Windows, install Python 3.12, Node.js 20+ and Git, then run `pwsh -File ./setup.ps1` from this folder before those commands. Setup downloads the toolkit at commit `cd4bf20904be4e7d63babd9622b17963c2361b27`, its Remotion dependencies (for FFprobe), free Kokoro models, and Python dependencies into the parent workspace. No API key is needed. The setup helper has been inspected, but was not tested in a separate clean machine; the commands above were executed against the current workspace. Hardware/library changes can change synthesis timing slightly. The fit stage conforms measured narration to 4080 video frames using pitch-preserving tempo adjustment; verification requires 170 seconds within 25 milliseconds.

To rebuild visuals from the included audio without regenerating speech, skip `prepare.py` and the `audio` command; run render, assemble and verify against the included measured beat sheet. Do not run prepare.py alone and expect timings to remain: it intentionally resets the script to its unmeasured form.

## Evidence and scope
`measure_tokens.py` checks both encodings for all three lowercase ASCII words without leading spaces. `evidence/tokenization.json` contains actual IDs, fragments, letter positions and counts. These are OpenAI tokenizer measurements, not Claude tokenizer measurements. Tokenization is reversible: the spelling and counts are preserved. The embedding graphics use made-up vectors labeled as constructed illustrations; no learned model weights or model accuracy results are claimed. See `FACTCHECK.md`.

## Course posting and review
Assigned folder: `fall-2026/shyam-g/week-01-video`. Source baseline reviewed: `62992c08bbd0c72efc692ace3210baa7bf6be138`. See `evidence/course-review.md` and `evidence/course-example.json` for the late course-source check. Human understanding and a human watch-through are not claimed. Canvas submission and instructor acceptance remain the student's responsibility.

## Video and matching package
[Watch/download the exact 2:50 MP4](https://github.com/contactshyam14-code/info-7375-prompt-engineering-for-generative-ai/releases/download/shyam-g-week01-video-v1/Week01_Tokens_Not_Words.mp4)

[Download the complete submission ZIP](https://github.com/contactshyam14-code/info-7375-prompt-engineering-for-generative-ai/releases/download/shyam-g-week01-video-v1/Jayaraman_Gopalakrishnan_Shyam_Sundar_INFO7375_Week01_Video.zip)

[Release and checksums](https://github.com/contactshyam14-code/info-7375-prompt-engineering-for-generative-ai/releases/tag/shyam-g-week01-video-v1). Generated media is kept in that release rather than Git, following the course's media exclusions. The ZIP includes the identical MP4, audio masters and source files. Extract it into a **separate workspace outside the course checkout** before running the rebuild commands. Do not install the toolkit stack in the course tree.

## Pipeline adaptation
This is a Brutalist audio-first build using its actual `generate_audio_kokoro` loading/normalization helpers and downloaded Kokoro models, custom Manim scenes, and FFmpeg assembly. Its native approval-gated `art final` was not used; no human approval was fabricated. The user requested autonomous generation and allowed FFmpeg assembly. The custom 1080p layout and persona follow that request rather than the toolkit's stock branded 4K bookends. Source scripts and dependency models are referenced rather than bundled.
