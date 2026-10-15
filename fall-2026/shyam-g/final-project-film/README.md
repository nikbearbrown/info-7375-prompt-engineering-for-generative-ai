# StopLine — Final Project Pitch Film (INFO 7375)

- **Name:** Shyam Sundar Jayaraman Gopalakrishnan (GitHub: contactshyam14-code)
- **Working title:** StopLine: checking the evidence behind a quality decision
- **Target role:** Supply chain manager
- **Canvas file:** `JayaramanGopalakrishnan_ShyamSundar_INFO7375_FinalProjectFilm.zip`
- **GitHub folder:** `fall-2026/shyam-g/final-project-film/`
- **Runtime:** 2:59 (178.75 s), 3840×2160, 8.8 MB
- **Film:** `film/stopline-pitch.mp4` (rendered 2026-10-15; SHA-256 `5b743436f5b37a8abb0a46735d7e258d0d079e2cbccd42740db77aa640da7710`).
  **Not in this GitHub folder:** the course repo's `.gitignore` keeps generated audio and video out of Git (`*.mp4`). The film is in the Canvas ZIP; its SHA-256 above lets you confirm the copy matches.
- **Quality gates:** all passed. See `film/gate_reports/`.

All incident data in this folder is **synthetic**. Claude Code wrote most of the code; the author reviewed every check on 2026-10-14 (see FRICTIONAL.md).

## Try the prototype (exists today)

Requires Python 3.10 or newer. Standard library only.

```bash
python data/build_synthetic.py              # regenerate synthetic data
python -m stopline data/incidents.json      # one outcome + one audit record per incident
python -m unittest discover -s tests -v     # 12 tests
python -m stopline.evaluate data/incidents.json data/evidence.json data/labels.json --out reports/eval_report.md
```

Saved output from the 2026-10-14 run is in `reports/`.

## Rebuild the film

See `BUILD-PROMPT.md`. In short:
1. `python film/build_reel.py <path-to-brutalist.art>` (sheet + scenes).
2. Run `python film/make_sheet.py --final`.
3. Copy the sheet into a Brutalist reel folder, then run the toolkit's audio, `run` and `final` steps.
4. Copy the `.mp4` and the gate reports into `film/`.

## Layout

```
stopline/   engine (schema, checks, engine, cli, evaluate)
data/       synthetic incidents, evidence, labels + generator
tests/      unit tests
reports/    real run outputs
film/       make_sheet.py, scenes_body.py, build_reel.py, wsl_setup.sh,
            reel/ (what the toolkit renders), gate_reports/, rendered film
```
