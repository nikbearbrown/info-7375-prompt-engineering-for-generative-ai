# SOURCES — Agentic Retrieval Lab (final film)

**Film:** *Agentic Retrieval Lab*, INFO 7375 final project film by Rithika Sankar Rajeswari. Final master, 2026-11-23 (sha256 c7b9d6ae515f0e550137beb2eb7fc30c46a51e4ab6dfc766682852e8eeb4bf23).

## Script
- `../FILM-BRIEF.md`: Rithika's brief; the narration is used word for word (`make_sheet.py` checks this).

## Project evidence (read-only)
- `~/agentic-retrieval-lab/results/foundation/` (`2026-10-08_rewrites_300/`, `2026-10-08_bm25/`, `2026-10-08_leak_v3/`, `2026-10-09_corpus/`) and `results/m2/` (`2026-11-23_bm25_subcorpus/`, `2026-11-23_dense_bge-small-en-v1.5/`, `2026-11-23_dense_e5-small-v2/`, `2026-11-23_hybrid_bm25_bge/`).
- `~/agentic-retrieval-lab/docs/FRICTIONAL.md` (hardware), `README.md`, `config.yaml` copies in each results folder, `src/arl/eval/metrics.py` (bootstrap interval).
- Test count from `uv run --frozen --no-sync pytest -q -p no:cacheprovider`, 2026-11-23 ("135 passed").

## Evidence excerpts (in `evidence/`)
- `example_846513.jsonl`: query 846513 ("what is the shingles jab?") and its main rewrite 846513_p ("what is the shingles vaccine"), copied verbatim from the git-ignored `data/processed/queries_human.jsonl` line 93 and `queries_agent.jsonl` line 369.
- `example_846513_bm25_per_query.csv`: the header and lines 94 and 670 of `results/m2/2026-11-23_bm25_subcorpus/per_query.csv`.
- Other real MS MARCO question on screen (B07): "when is ski season over", `queries_human.jsonl` line 108. Leak example (B11): `results/foundation/2026-10-08_leak_v3/leak_v3_sanity.json`.

## Paper
- M. Schall, S. Eslami, M. Krimmel, A. Chaffin, L. Milliken, B. Wang, D. Bykov. *Q2D-Web: A Large-Scale Benchmark for Retrieval in Agentic RAG Systems.* arXiv:2609.08887v2, 2026 (Perplexity AI). https://arxiv.org/abs/2609.08887v2. Cited only; CC BY-NC-ND 4.0. Facts reused from the October fact-check (rows 17–20).

## Dataset
- MS MARCO Passage Ranking: P. Bajaj et al., *MS MARCO: A Human Generated MAchine Reading COmprehension Dataset*, arXiv:1611.09268, 2016 (Microsoft). Dev/small queries and official qrels, used under Microsoft's MS MARCO terms (non-commercial research use).
- BM25: S. Robertson & H. Zaragoza, 2009 (cited in the repo's `docs/SOURCES.md`).
- Models: `BAAI/bge-small-en-v1.5`, `intfloat/e5-small-v2` (Hugging Face Hub). Rewrites by `claude-haiku-4-5-20251001`.

## Third-party assets
Same set as the October reel (licences checked there, 2026-10-11): kokoro-onnx 0.6.1 (MIT), Kokoro-82M voice `af_bella` (Apache-2.0), EB Garamond (SIL OFL 1.1), Manim Community 0.18.1 (MIT), brutalist.art toolkit (licence not stated by the repository).

## Toolkit and voice
- **brutalist.art**, `show-tell` skill: Manim drawings in the house isometric style. Free local pipeline; no API keys, paid services or uploads.
- **Narration:** synthetic voice, Kokoro af_bella (kokoro-onnx, speed 1.0), reading Rithika's script in the first person. It is not a recording of Rithika.
- **No external media.** Every picture is drawn in Manim. No stock images, photos, music, or AI-generated images or video.
- **Cartoon people:** the October reel's generic flat figures (Rithika's avatar, the keyword librarian, the meaning librarian), copied verbatim into `cast_october.py` with her permission (2026-11-23). None is a portrait or likeness of a real person. No instructor name, portrait, voice, handle or mascot.

## Contributions
- **Rithika:** project, brief and narration, wording decisions, review and approval.
- **Claude (chat):** helped draft the brief and the pass/fail rules (adopted by Rithika).
- **Claude Code:** fact-check, beat sheet, paperwork, gates.
