# PROMPTS.md — per-beat prompts for open slots

**There are no open slots in this reel.** Every beat is rendered by the
pipeline from `beat_sheet.json` + `scenes.py`; nothing is requested from a
human, a stock library, or a generative video service.

This file exists because GATE F requires the paperwork set before a render.
What follows is therefore not a work order but the *generation* prompts —
the asks that produced the two on-screen Claude composer beats, kept here so
the reel's own ASK→RESULT pairs are reproducible.

## B00 — the cold open ask (shown on screen)

```
In main.py, why subtract max(logits) before exp() if the distribution is unchanged?
```

Running line: `reading lessons/01-randomness-and-first-prompts/code/main.py`

## BHTF — the Your Turn ask (shown on screen, for the viewer to run)

```
Run probabilities([1,2,3]) two ways - with and without the max shift - and
print both with repr(). Do the last digits match?
```

Commands offered to the viewer:

```
python3 lessons/01-randomness-and-first-prompts/code/main.py
python3 evidence/run_evidence.py --course <your clone> --compare <another python3>
```

## Not used

- No `higgsfield` / AI-video prompts. The free pipeline only.
- No image-generation prompts. No stills are used anywhere in the reel.
