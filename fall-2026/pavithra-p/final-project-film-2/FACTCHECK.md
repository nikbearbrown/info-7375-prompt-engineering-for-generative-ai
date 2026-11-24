# FACTCHECK: DryRun Final Project Film (four parts)

Verdicts: PASS (checked), CORRECTED (changed after checking), EXEMPT (a plan, stated as "will" or "planned", not a fact). Beats B02–B04, B09, B11–B14, B16, B21 and B25 keep the pitch film's narration word for word; their checks carry over from the pitch's FACTCHECK (October 2026) and are repeated here.

| # | Beat | Claim | Verdict | Source | Fix |
|---|---|---|---|---|---|
| 1 | B01 | My name; DryRun will show what an AI's command will really do to my files before I run it, and warn when it isn't what I asked | EXEMPT | APPENDIX.md (a plan) | No "how" in part 1, as the brief asks |
| 2 | B02 | AI assistants suggest terminal commands and coding agents run them | PASS | Claude Code runs shell commands through its Bash tool; B03 is a real suggested command | none |
| 3 | B02 | One wrong character can delete files | PASS | General shell behaviour (e.g. a stray space before `*` in `rm -rf build/ *`) | Kept general |
| 4 | B03 | Claude replied `find logs -type f -name "*.log" -mtime +7 -delete` and advised previewing first | PASS | Real reply, claude.ai, 2026-10-11 (`evidence/claude-reply-2026-10-11.png`) | Shown as the real screenshot, cropped |
| 5 | B04 | On my Mac, the preview did not match a 7.5-day-old file | PASS | `evidence/mtime-test.md` (run 2026-10-11 by Claude Code; re-run by me 2026-10-13, same output; macOS find) | My own Terminal lines from 13 Oct, copied exactly |
| 6 | B05 | A delete command has no undo step | PASS | `rm` and `find -delete` remove files without a trash or undo step | CORRECTED after the GPT review: was "a deleted file can't be taken back", too absolute (a backup could restore it) |
| 7 | B07 | Coding agents like Claude Code can ask you to approve a command before it runs, and show the command, not what it will change | PASS | Claude Code's permission prompt for a Bash command shows the command and asks to allow it (my own use, 2026); whether it asks depends on its permission settings | CORRECTED after the GPT review: was "ask before they run a command", which is not true under every setting |
| 8 | B07 | `try` runs a command in a sandbox on Linux and asks whether to keep its changes; you still judge them | PASS | github.com/binpash/try README, read 2026-11-23: "Inspect, control, and manipulate a command's effects before modifying your live system"; Linux namespaces and overlayfs, "Linux 5.11 or higher"; it asks to commit the changes; nothing about checking them against the request | none |
| 9 | B08 | InterCode (Yang et al., 2023) found that letting the AI see the result of running its code helps | PASS | arXiv 2306.14898 abstract, read 2026-11-23: execution feedback as observations; "Our results showcase the benefits of interactive code generation" | Paraphrased, no number claimed (the abstract gives none for Bash) |
| 10 | B08 | NL2SH (Westenfelder et al., 2025) checked 600 commands by hand; its methods raised accuracy by up to 32% | PASS | arXiv 2502.06858 abstract, read 2026-11-23: "a manually verified test set of 600 instruction-command pairs"; methods "can improve NL2SH accuracy by up to 32%" | none |
| 11 | B09, B12–B19 | Everything DryRun will do | EXEMPT | APPENDIX.md | Future tense in narration and on screen; PLANNED chips |
| 12 | B11 | No DryRun code exists yet | PASS | My course folder and GitHub (no DryRun code, checked 2026-11-23) | none |
| 13 | B12–B15 | The AI's prediction, the simulated deletion, the WARN decision, the change report and the person's choice | EXEMPT | Constructed from my 11 Oct preview test (1 file matched) | Labelled CONSTRUCTED EXAMPLE / SIMULATION on screen |
| 14 | B19 | Token credits: none to buy, Claude through my Northeastern Claude Code account | PASS | `claude --version` 2.1.294, signed in through NEU; JS1 and JS2 ran Claude with `claude -p` on this account | none |
| 15 | B19 | My laptop is an M3 with 8 GB of memory, and already runs Docker and a small local model in Ollama | PASS | `sysctl` on 2026-11-23: Apple M3, 8 GB; `docker --version` 27.4.0; `ollama` 0.40.13 with the `qwen2.5` model downloaded | none |
| 16 | B19 | Keeping the task set small to stay inside usage limits | EXEMPT | A plan | none |
| 17 | B21–B24 | The measurement, the held-out set, the planted failures, the targets and the limits | EXEMPT | APPENDIX.md (a plan) | Labelled PLANNED / TARGETS · NOT MEASURED YET |
