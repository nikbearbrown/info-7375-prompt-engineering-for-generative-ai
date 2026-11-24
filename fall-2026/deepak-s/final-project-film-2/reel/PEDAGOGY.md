# PEDAGOGY: CueGate film 2 (the project film, show-tell, two voices)

A film about a final project that does not exist yet as code. It follows the professor's announcement (inputs-film2/ASSIGNMENT-FILM2.md, which governs until the Canvas text is added): four parts, in order: executive summary, introduction, methods, evaluation. The honesty rule holds: past tense only for what exists and can be shown, "will" for everything else.

## The four parts → beats
| Part (announcement) | Beats | What it answers |
|---|---|---|
| 1. Executive summary: what and why | B01–B06 (E1–E4b) | What CueGate is (B04), why anyone should care (B03), why trust it over an AI button (B06). No "how" in this part. Ends at about 0:52, inside the first minute. |
| 2. Introduction: what others have done | B07–B11 (I1–I4b) | Three tools (B08), two papers (B09), what's missing and why CueGate still matters (B11). |
| 3. Methods: how | B12–B18 (M1–M5b) | Data (B13), the pipeline step by step (B14), what happens when the model fails (B15, B16), resources: model access, compute, data, accounts (B18). |
| 4. Evaluation: how I'll know | B19–B25 (V1–V5b) | Four versions on the same lines (B20), worked-if and failed-if (B21), the meaning check's own miss count (B23), what exists vs will (B25). |

## The two voices
- DEEPAK (am_onyx) narrates as Deepak.
- SKEPTIC (af_bella) is a constructed voice that asks the announcement's questions out loud. It is labelled on screen at its first line ("SKEPTIC · a voice I wrote to ask the hard questions"), every beat carries its speaker tag, and every caption cue starts with its speaker.
- Pauses: by the fixed rule in pad_audio.py, the act-card questions hold their card to 3.0 s, the first SKEPTIC line holds to 4.0 s, and every other SKEPTIC line gets at least 0.5 s of silence after it (at least 2.6 s in all). The voice is never sped up or cut.

## Evidence discipline
Every claim is in FACTCHECK.md with a kind (exists / will / external fact / reading), a verdict and a dated source. The two IWSLT papers were fetched on 2026-11-23 and checked against their first pages. RESOURCES facts come only from inputs-film2/RESOURCES.md (Deepak, 2026-11-23). The model-download check (2026-11-23) is in FACTCHECK.md as evidence for RESOURCES item 4; the narration names no model.

## Narration review
Narration is NARRATION-FILM2.md: Deepak's script (inputs-film2/FILM2-SCRIPT.md, 2026-11-23) with branch A for E3 and V5b, Deepak's override-3 rewordings (M3, M4a, V2, V3), the resources line (M5b) filled from RESOURCES.md, and Deepak's STOP A decisions (E2b and E3 corrected; M5b shortened to 61 words; M2, V4a and V4b reworded so Kokoro says them cleanly). Runtime is measured from a Kokoro probe of this text: 220.7 s of speech, 234.7 s (3:54.7) with the pauses and the outro tail, under the 4:00 limit Deepak set until the Canvas limit is known. No trims were needed.

Narration sign-off: Deepak signs GATE P below, in his own words, at STOP A.

GATE P: I checked the narration, evidence, resources, visual previews, captions and pauses. The film clearly separates what already exists from what I plan to build, without presenting unfinished CueGate features as completed. VERDICT: PASS

Note, 2026-11-23: there is no separate Canvas assignment for film 2; the professor's announcement is the available instruction.
