# BUILD-PROMPT — Agentic Retrieval Lab (final film)

How this film was made: Rithika's prompts to Claude Code on 2026-11-23, verbatim, followed by the commands that rebuild it from a fresh clone.

## 1. Rebuild from a fresh clone

Tested setup: macOS (Apple M5, 16 GB), Python 3.12.12, Manim Community 0.18.1, ffmpeg on PATH. Free pipeline only: no API keys, no paid services.

```bash
# 1. Toolkit at the commit used for this film
git clone https://github.com/nikbearbrown/brutalist.art
cd brutalist.art
git checkout b21f625

# 2. Python env + dependencies + Kokoro model files
python3.12 -m venv .venv
source .venv/bin/activate
./setup --install

# 3. Local toolkit patch: moves the beat-1 name stamp inside title-safe (same patch as the October pitch).
#    The package-lock.json hunk in the diff is npm-install noise and can be skipped.
git apply --include=runtime/scripts/compile.py /path/to/final-project-film-final/toolkit-local-patch.diff

# 4. Reel folder (the folder name is the slug)
REEL=~/agentic-retrieval-lab-final
mkdir -p $REEL
cd /path/to/final-project-film-final
cp beat_sheet.json scenes.py word_times.json SOURCES.md FACTCHECK.md SHOTLIST.md PROMPTS.md $REEL/
cp -R evidence $REEL/
cd -   # back to brutalist.art

# 5. Narration (Kokoro af_bella, speed 1.0): writes mp3/beat-*.mp3 and measured durations
python runtime/scripts/generate_audio_kokoro.py $REEL --speed 1.0

# 6. Silences: 1.2 s head on each part's first beat (title card), 1.0 s tail on the outro
cd $REEL/mp3
mkdir -p _raw
cp beat-*.mp3 _raw/
for b in B01 B06 B10 B18; do ffmpeg -y -i _raw/beat-$b.mp3 -af "adelay=1200:all=1" -c:a libmp3lame -b:a 192k beat-$b.mp3; done
ffmpeg -y -i _raw/beat-BOUT.mp3 -af "apad=pad_dur=1.0" -c:a libmp3lame -b:a 192k beat-BOUT.mp3
cd $REEL
python3 - <<'EOF'
import json, subprocess
p = 'beat_sheet.json'; s = json.load(open(p)); t = {}
for b in s['beats']:
    d = float(subprocess.check_output(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'csv=p=0', b['audio_file']]))
    b['actual_duration_s'] = t[b['beat_id']] = round(d, 2)
json.dump(s, open(p, 'w'), indent=2, ensure_ascii=False)
json.dump(t, open('mp3/timings.json', 'w'), indent=2)
EOF
cd -   # back to brutalist.art

# 7. Review cut (Gates F, L, A, W, B, V), then the clean master (Gate T)
./art run $REEL --height 2160
./art final $REEL --height 2160 --out $REEL/exports/landscape
shasum -a 256 $REEL/exports/landscape/agentic-retrieval-lab-final.mp4
```

Notes:
- **Timing source.** `word_times.json` (faster-whisper small.en word times of the original narration) is what times every on-screen cue in `scenes.py`. Use the copy in this folder: re-transcribing can shift a cue by a few hundredths of a second.
- **Don't re-run `make_sheet.py` for a rebuild.** It writes `beat_sheet.json` from `../FILM-BRIEF.md` and drops the measured audio fields. It's here as the record of how the sheet was made, including the narration-equals-brief check and the on-screen-numbers-in-brief check.
- **Byte-identical output isn't guaranteed.** Kokoro and the encoders may differ across machines, so a rebuild can produce a master whose sha256 differs from the submitted `c7b9d6ae…bf23`. The submitted MP4 is the reviewed one.
- **Source data.** The numbers come from https://github.com/rithika-sr/agentic-retrieval-lab at commit `71c42ce` (`results/foundation/`, `results/m2/`). The film build only reads them; it never re-runs the experiments.

## 2. Rithika's prompts (2026-11-23, verbatim)

Short replies (button answers) are included. Two messages were images only: Rithika sent back contact sheets of review frames during the build.

### Prompt 1
```
Set up the final film brief. Do not render anything yet.

1. Create ~/final-project-film-final/ and save FILM-BRIEF.md there with the exact content between the ===START=== and ===END=== lines below.
2. Read my October fact-check: ~/info-7375-prompt-engineering-for-generative-ai/fall-2026/rithika-s/final-project-film/FACTCHECK.md and the SOURCES.md next to it. Replace the first bullet of section 2 (the Q2D-Web sentence) with wording that matches only what that file verified. Quote the exact FACTCHECK lines you relied on.
3. Check every number in sections 3 and 4 against the result files in my agentic-retrieval-lab repo (results/foundation/ and results/m2/). If you can't find the repo, ask me for its path. Make a table: claim → file → value in file → match yes/no.
4. Count the narration words per section and estimate the runtime at 150 words per minute. The hard cap is 4:00; aim for 3:45 or less. Section 1 must be 45 seconds or less, and must not mention BM25, embeddings, recall, corpus, or MS MARCO.
5. Report steps 2, 3 and 4. Then STOP. Do not start a beat sheet or a render.

===START===
# FILM-BRIEF — Agentic Retrieval Lab (final film, under 4:00)
Rithika Sankar Rajeswari · INFO 7375

## 1. Executive summary (0:00–0:45) — what and why, no "how"
In RAG systems, AI agents now write the search queries, not people. If an agent's query finds the wrong passage, the answer built on it is wrong, and nobody sees why. I built Agentic Retrieval Lab to measure, on public data, whether agent-written queries find the right passage as well as the original human question, and which search method handles them best. So far, the agent's rewrites never did better than the human question. This matters to anyone choosing a search method for an AI agent: it's a cheap, repeatable check, and every number in it traces back to a file.

## 2. Introduction (0:45–1:25) — what others have done
- Q2D-Web studied human versus agent-written queries, but its data is private: there's a public leaderboard, but you can't inspect the queries.
- MS MARCO, from Microsoft, is the standard public set of real search questions with a marked correct passage, but its queries are human only.
- BM25 is the classic keyword search. bge and e5 are widely used small embedding models that search by meaning.
- The gap: there's no small, open experiment that compares human and agent queries across these search methods, that anyone can rerun on a laptop. That's what this project is.

## 3. Methods (1:25–2:40) — how
- Data: 300 MS MARCO questions (fixed seed 42). Claude Haiku 4.5 rewrote each one into 1 main and 3 supporting agent queries, 1,200 in total. A leak check flagged rewrites that gave away the answer.
- Test corpus: 200,000 passages, made of every correct passage, BM25's top-100 near-misses, and random fill.
- Four retrievers: BM25, bge-small, e5-small, and a BM25+bge hybrid.
- Measures: whether the correct passage is in the top 100, and how high it ranks. Each comparison is query by query, with 95% bootstrap intervals.
- Resources, all in hand: one M5 laptop with 16 GB (each embedding model ran in about 8 minutes), my own Anthropic API credits (the logged cost for all rewrites was $0.63), and a free Hugging Face account. 135 automated tests.
- Next: a length-matched control corpus, harder distractors chosen by dense models, two larger embedding models, and an LLM relevance judge.

## 4. Evaluation (2:40–3:45) — how I'll know it worked
I wrote the pass/fail rules before seeing the results:
1. Trust: every test passes and every number links to a dated results folder. Met.
2. Length: if picking the shortest passages beats random, dense results are provisional. It did, by a small margin, so they're provisional.
3. Dense beats BM25 only if the 95% interval is above zero. It was, by +0.32 recall, but my corpus is made of BM25's near-misses, so it flatters dense models.
4. Human vs agent: agent queries never beat human ones. The gap shrank from 5 points with BM25 to about 1 point with dense models.
It worked if: the numbers reproduce and the limits are stated. It failed if: a fixed corpus erases the dense advantage. Next, I'll build that fixed corpus.
===END===
```

### Prompt 2
```
Yes, fix them
```
(Approves three wording fixes: the $0.63 cost becomes "all LLM calls"; "on average" added to the never-did-better lines; "My pass/fail rules:" replaces "I wrote the pass/fail rules before seeing the results:".)

### Prompt 3
```
Two text fixes to ~/final-project-film-final/FILM-BRIEF.md, then the beat sheet. No render yet.

A. Text fixes:
1. Section 1: replace "So far, on average, the agent's rewrites never did better than the human question." with "So far, the agent's rewrites didn't beat the original human question with any search method."
2. Section 4, rule 4: replace it with "Human vs agent: the human question came out ahead with every search method; the gap shrank from 5 points with keyword search to about 1 point with the meaning-based models, too small to call for e5."
3. Section 4: replace "My pass/fail rules:" with "I set these pass/fail rules before the Milestone 2 runs (drafted with Claude, adopted by me):"
4. Update the section timestamps to match your word-count estimates, and recompute them after these edits.

B. Beat sheet (read the toolkit's skill/README in brutalist-v2 first and follow its conventions):
1. Create a new reel folder for this film. Do not modify the October reel. You may copy the October character assets (my character and the two librarians, keyword vs meaning) from the October reel folder.
2. Write beat_sheet.json using the brief's narration word for word, in four parts in this order. Each part opens with a short on-screen title card: "1 · Executive summary", "2 · What others have done", "3 · Methods", "4 · Evaluation".
3. Visual rules (lessons from October):
   - real readable text only, no placeholder squiggles
   - every key term labeled on screen when it is spoken
   - characters exit when their line ends
   - visuals enter and leave in sync with the narration
   - numbers on screen must match the brief exactly
4. One real example from my data: from agentic-retrieval-lab/results/m2/2026-11-23_bm25_subcorpus/per_query.csv, pick one question where BM25 found the correct passage for the human query but not for its primary agent rewrite. Show both query texts exactly as they appear in queries_human.jsonl and queries_agent.jsonl, and tell me the IDs.
5. In the Evaluation part, show the four rules as a checklist with their verdicts (Met / Provisional / Provisional-flattered / Human ahead).
6. Create SOURCES.md, FACTCHECK.md (reuse the claim → file table you just made), SHOTLIST.md and PROMPTS.md in the reel folder, then run Gate F only.
7. Report: the beat list (beat number, part, seconds, one-line visual), the example query IDs and texts, the Gate F result, and the updated brief timestamps. Then STOP.
```

### Prompts 4–9
```
Approve, do audio
```
```
Both sound fine
```
(After listening to B03, "Agentic Retrieval Lab", and B10, "300 em-ess Marco questions".)
```
Yes, write scenes
```
```
Yes, run review cut
```
```
Run art final
```

### Prompt 10 (this folder)
```
Assemble my submission folder. Do NOT git add, commit, or push.

1. cd ~/info-7375-prompt-engineering-for-generative-ai and run `git pull --no-rebase`. If there is any conflict or error, report it and STOP.
2. Create fall-2026/rithika-s/final-project-film-final/ (do not touch the October folder final-project-film/). Copy in:
   - the final master agentic-retrieval-lab-final.mp4; confirm its sha256 still equals c7b9d6ae515f0e550137beb2eb7fc30c46a51e4ab6dfc766682852e8eeb4bf23
   - FILM-BRIEF.md
   - beat_sheet.json, SOURCES.md, FACTCHECK.md, SHOTLIST.md, PROMPTS.md from the reel folder
   - gate-reports/ (including FINAL.md)
   - In brutalist-v2, run `git status --short`. If any toolkit file (outside the reel folder) was modified, save `git diff` of those files as toolkit-local-patch.diff. If none, say so.
3. Write BUILD-PROMPT.md: the prompts I gave you today and the exact commands that rebuild the film from a fresh clone (clone, venv/setup, patch if any, art run, art final at 2160).
4. Write README.md with:
   - Assignment: INFO 7375 Final Project Film. Student: Rithika Sankar Rajeswari.
   - Project: Agentic Retrieval Lab, public repo https://github.com/rithika-sr/agentic-retrieval-lab at commit 71c42ce, which holds every number shown in the film
   - Runtime 3:40.8, resolution 3840×2160, sha256
   - The film's four-part structure with each part's start time
   - A contents list, and how to rebuild (point to BUILD-PROMPT.md)
   - Contributions: Claude Code built the Milestone 2 code, tests and film, and drafted README/BUILD-PROMPT. Claude (chat) drafted the brief and the pass/fail rules. I chose the scope, adopted the rules, wrote predictions, reviewed results and the film, and made the final decisions.
   - License: MIT
5. Search every file in the folder for "[TO FILL]", "[WRITE", "TODO", "TBD" and "[YOU" and list any hits.
6. Report the folder tree with file sizes, the sha256 check, and the placeholder results. Then STOP.
```
