# Render review — 2026-09-27

Reviewer: Codex (automated agent); this is not a claim of student or human approval.

## Final technical checks
- Encoded runtime: 170.000 seconds, exactly the user's revised 2:50 target.
- Final MP4: 6,480,243 bytes; contains video and audio streams, with 4080 video frames.
- Full FFmpeg decode completed successfully with no error output.
- Audio analysis: mean volume -23.4 dB, maximum -0.5 dB. This establishes a non-silent decoded track and no sampled peak at digital full scale; it does not certify spoken pronunciation or human comprehension.
- Audio timeline: 170.000 seconds. Shortened narration is 480 words, regenerated with Kokoro and conformed using approximately 3 percent pitch-preserving tempo adjustment. Captions and scenes follow the adjusted segment cues. The final encode uses a single PCM narration master and resets timestamps to avoid AAC segment-padding overrun.
- All six token round trips and per-fragment count checks passed. Measured character lengths are strawberry=10, banana=6, occurrence=10. Three r's in strawberry, three a's in banana and two r's in occurrence.

## Visual review actually performed
Extracted frames at 15%, 50% and 85% of each of 11 beats. Inspected the 33-frame contact sheet, then opened individual 1920×1080 frames for the opening, tokenizer comparison, occurrence, embedding, round-trip, prediction, limitation and closing scenes. Checked IDs against the JSON source, count arithmetic, visible limitations, vector-illustration labels, text readability and frame boundaries.

For the revised 2:50 cut, regenerated all 33 samples and inspected the updated contact sheet. The original layout fixes remain in place, with no new observed overlaps or clipping. The numerical examples, constructed-vector label and boundary callout remain visible.

Corrections made during review:
1. Replaced incorrect authored 'nine character positions' with measured '10 character positions', corrected the corresponding narration, and rerendered B00/B05.
2. Fixed the stale banana count overlapping the occurrence labels in B04.
3. Replaced unsupported text arrow glyphs in B05/B07/B10 with drawn vector arrows or plain separators; rerendered and inspected the repaired full-resolution frames. No missing arrow boxes or cut-off sentences remain in those inspected frames.

The final inspected frames show the correct IDs and sums, ten character boxes indexed 0–9, three highlighted r positions at 2, 7 and 8, and the narrow boundary statement. The final frames are readable and have no observed overlaps or clipped content.

## Review limits
Sampled-frame review is not a real-time human watch-through. Speech was generated locally and checked for duration, decodability and signal volume; no human listening or independent speech transcription is claimed. Before publication, the supplied course chapter and written policy were reviewed, and its example was run (see evidence/course-review.md). Instructor acceptance and student understanding remain unverified. These limits do not change the executed local measurements.
