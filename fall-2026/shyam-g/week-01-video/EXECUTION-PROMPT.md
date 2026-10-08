You are an expert autonomous software engineer and technical director. Produce the complete local INFO 7375 Week 1 Explainer Video submission in this workspace in one continuous shot. The user explicitly requests Claude Code to do the work. Do not pause for intermediate confirmation; finish the render and ZIP. Do not spawn other agents.

METADATA
- Student name: [FirstName] [LastName] (preserve placeholders; no invented name).
- Course: INFO 7375 - Prompt Engineering and Generative AI.
- Persona: Dunkin: practical, punchy, Boston-sharp, technically grounded, zero academic fluff. This is a speaking style, not a claim of sponsorship.
- Concept: The unit is a token, not a word — and why that breaks letter-counting prompts.
- Runtime: 3–4 minutes, STRICTLY less than or equal to 240 seconds, preferably 190–220 seconds.
- Framework: local brutalist.art repository with Kokoro narration, Manim/Remotion, FFmpeg. Free local pipeline only.

STEP 1: REAL EVIDENCE
measure_tokens.py has been written in submission; execute it with .venv/Scripts/python.exe if evidence/tokenization.json is not yet there. Use tiktoken with both cl100k_base and o200k_base for strawberry, banana and occurrence. Show the exact locally measured fragments and integer IDs, not the example split from the user's prompt. Explain token positions versus character positions.
Scientific correction: tokenization is LOSSLESS, so letter counts are NOT destroyed across chunk boundaries. Decode reconstructs the string, and per-fragment counts sum to the exact count. Embedding lookup has token-position granularity, not a dedicated slot per character; do not claim it necessarily erases spelling information or makes character counting impossible. Show character-index labels giving way to token-index labels, while explicitly saying spelling is recoverable. Embedding vectors are CONSTRUCTED ILLUSTRATIONS, not real learned model weights. These OpenAI tiktoken encodings are not Claude's tokenizer. No LLM accuracy experiment was performed; never invent a response or claim measured failures. Boundary: this mechanism can make letter counting less direct, but does not prove that tokenization alone causes every failure or that language models cannot count, use scratchpads, or call tools. Scratchpads do not guarantee correctness. Deterministic Python string counting verifies these examples.

STEP 2: DELIVERABLES
Write all project assets under submission, with final deliverables at its root:
1. beat_sheet.json: full narration and scene plan with actual measured audio durations and cues, Brutalist-compatible metadata where applicable.
2. scene.py (Manim) or Remotion equivalent: fully animated string-to-token split, token IDs, illustrative embedding lookup, clear character versus token positions, worked letter count, and limitation. Prefer Manim with Text and simple shapes to avoid requiring LaTeX. Use animations, not static slides. Clear readable 16:9 1080p design, white/cream on dark or another high contrast palette, restrained orange/pink Dunkin-inspired accents. Labels must fit inside frame. Do not use official Dunkin logos or imply affiliation. No fabricated Claude UI transcript.
3. README.md with placeholders, concept, why, exact verified runtime, exact Windows rebuild commands, review status and outstanding course posting/name requirements.
4. BUILD-PROMPT.md: preserve this complete execution prompt and actual reproducible commands/flags; include any subsequent repair prompts.
5. SOURCES.md: distinguish Claude Code's work from Codex's setup/groundwork, measured data versus illustrations; cite tiktoken, Kokoro, Manim, FFmpeg, Brutalist and exact relevant LICENSE files. Do not guess license terms. Font licensing too. No external imagery required.
6. FRICTIONAL.md: timestamped honest events and actual output, installation and render errors, resolutions and verification. Do not invent verification, human review, or course-code execution.

STEP 3: BUILD
Read ASSIGNMENT.txt and toolkit README/CLAUDE.md and relevant complete skill/docs before building; user requirements override branding, approvals and runtime defaults. Search existing scene library before authoring. Be pragmatic about Windows adaptations, document deviations. Use the actual toolkit Kokoro generation utility when feasible; if needed use its local Kokoro model directly and explain the adaptation. Generate all audio first and MEASURE durations, then set scene durations to match. Render and assemble with FFmpeg; final MP4 must be 180–240 seconds with audible narration and real motion. Budget about 450–500 narrated words and tune speed based on measured runtime. Use installed local voice am_onyx or af_bella. Never synthesize paid audio.
Verify file size, audio/video streams, duration, full decode, and sample scene frames. Make a contact sheet for Codex to inspect and supply sample audio. Render final video at submission/Week01_Tokens_Not_Words.mp4. Package submission as [LastName]_[FirstName]_INFO7375_Week01_Video.zip in the workspace parent, including MP4, all six documents, code, evidence, small generated assets and rebuild dependencies. Omit node_modules, venvs, tokenizer/model caches, raw Claude logs/transcripts, credentials and __pycache__. Do not include toolkit model files; document their setup. Use Python zipfile for square-bracket names.

LOCAL ENVIRONMENT
- Workspace root is current working directory; toolkit is ./brutalist.art.
- Activate-Workspace.ps1 configures PATH and Git Bash.
- Python: ./.venv/Scripts/python.exe (Python 3.12). tiktoken is installed, plus toolkit requirements.
- ffmpeg: .tools/ffmpeg.exe (full imageio bundled FFmpeg); ffprobe: brutalist.art/runtime/remotion/node_modules/@remotion/compositor-win32-x64-msvc/ffprobe.exe.
- Git Bash: C:/Program Files/Git/bin/bash.exe.
- Kokoro model: brutalist.art/runtime/models/kokoro/kokoro-v1.0.onnx; voices-v1.0.bin. Real synthesis/decode test passed at -21.8 dB.
- Remotion node modules installed; Manim and faster-whisper imports passed. LaTeX not installed. Use vector Text rather than fake rendered math. Only simple integer counting is needed.
- Set TIKTOKEN_CACHE_DIR to workspace/.tokenizer-cache.
- Course repository URL is not supplied. Complete local deliverables with real tiktoken evidence, explicitly record inability to verify Chapter 1/course policy/code; no fake repo, GitHub link or commit hash. Do not block on this missing URL.
- Do not upload/push/submit, change account settings, read unrelated user files or modify outside this workspace. Do not use paid APIs beyond this authorized Claude Code session. Install missing free build dependencies locally only if necessary.

Finish every doable step. Return concrete file paths, measured runtime, checks, and unresolved limitations. Keep logs concise and honest.
