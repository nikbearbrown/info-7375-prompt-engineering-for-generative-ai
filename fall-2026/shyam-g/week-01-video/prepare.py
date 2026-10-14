"""Author the beat sheet. Audio timings are filled by build.py, never guessed."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = [('Wrong-sized ruler',
  'hook',
  ["How many r's are in strawberry? Three. Why can a language model stumble on that? Start with the ruler it "
   'uses.',
   'Models process tokens, not a separate position for every letter. Counting becomes less direct, not '
   'impossible.',
   "Let's inspect two real tokenizers and check the count."],
  'Reveal strawberry; highlight its three r characters; contrast ten character slots with three token '
  'slots.'),
 ('Text in. Token IDs out.',
  'pipeline',
  ['A tokenizer converts text into integer IDs. A token can cover a word, part of a word, or other text.',
   'We ran tik token locally with both encodings shown here: lowercase inputs, no leading spaces.',
   "These are OpenAI encodings, not measurements of Claude's tokenizer."],
  'Animate raw text through tokenizer box into real IDs; name both encodings and exact input conditions.'),
 ('One word. Three tokens.',
  'cl100k',
  ['First, strawberry in c l one hundred k base: str, aw, berry. These are the exact measured IDs.',
   'Count r inside each chunk: one, zero, two. Add them: three.',
   "Three tokens matching three r's is a coincidence. Token count is not a letter-counting rule."],
  'Reveal measured fragments and IDs in cl100k_base; reveal per-fragment counts 1, 0, 2; sum to 3.'),
 ('Same spelling. Different split.',
  'o200k',
  ['Switch encodings. Strawberry now splits into st, raw, berry. Different boundaries and IDs; same '
   'spelling.',
   'The r counts become zero, one, two. Still three. The first r moved into another chunk, not out of the '
   'text.',
   'Token boundaries depend on the encoding.'],
  'Compare measured cl100k_base and o200k_base chunks; show 0 + 1 + 2 = 3.'),
 ('One token can hide a whole word',
  'other_words',
  ["Banana is one token in both encodings. Different IDs, but still three a's. One token does not mean one "
   'letter.',
   "Occurrence splits into occ and urrence. Both r's are in the second chunk. These IDs are also measured.",
   'Counting chunks and counting characters are different operations.'],
  'Animate banana one-token cards for both encodings; occurrence two-token cards; highlight three a and two '
  'r characters.'),
 ('Lookup at token resolution',
  'embedding',
  ['Embedding lookup selects a learned vector for each token ID. These colored vectors are constructed '
   'illustrations, not real model weights.',
   'Ten character positions become three token positions for strawberry. Internal letters have no separate '
   'input token position.',
   'But vectors can carry spelling-related information. Lookup does not prove spelling was erased.'],
  'Replace visible character indices with token indices; animate ID-to-vector lookup; keep '
  'constructed-illustration label visible.'),
 ('The letters are still there',
  'lossless',
  ['Tokenization is reversible. Decode these IDs and every letter of strawberry comes back.',
   'All six word-and-encoding pairs passed our Python round-trip checks. Counts across decoded fragments '
   'also matched the original strings.',
   'Less direct access does not mean lost characters.'],
  'Animate token cards joining back into strawberry; show actual round-trip and count assertions from '
  'measurement script.'),
 ('Prediction is not a counting loop',
  'prediction',
  ['Predicting an answer is not automatically the same as running a character-counting loop.',
   'We tested tokenizers, not model responses. This experiment gives no model failure rate and cannot '
   'diagnose a particular wrong answer.',
   'Keep the conclusion as narrow as the evidence.'],
  'Contrast constructed model-answer pathway with deterministic counting pathway; no fabricated response '
  'text; label no model benchmark.'),
 ('Use the right tool',
  'code',
  ["Run Python's count operation. Strawberry has three r's; banana has three a's; occurrence has two r's.",
   'These results were executed locally. This code view reconstructs recorded output; it is not a live '
   'screen capture.',
   'Run the operation. Inspect the result. Fluency alone verifies nothing.'],
  'Reveal executable Python count expressions and measured outputs 3, 3, 2; replay character highlights.'),
 ('What this does not prove',
  'boundary',
  ['Tokens do not make models unable to count. A model may answer correctly, use a scratchpad, use '
   'character-level representations, or call tools.',
   'Scratchpads still do not guarantee correctness. Two encodings do not establish how every model works.',
   'Our claim: token positions differ from character positions. Not a universal failure diagnosis.'],
  'Reveal CAN count, tools and representations; distinguish possible aids from guarantees; state scope.'),
 ('Count characters. Not chunks.',
  'closing',
  ['Try another word: encode it, inspect the IDs, decode it, then count the target letter.',
   'A token is a processing unit, not a spelling unit. Use the right ruler.',
   "Strawberry: three r's. Verified locally."],
  'Return to ten character slots; highlight positions 2, 7, 8; show final answer and reproducible exercise.')]


def main():
    beats=[]
    for i,(title,kind,segments,visual) in enumerate(DATA):
        beats.append(dict(beat_id=f'B{i:02d}', title=title, kind=kind, engine='kokoro',
                          voice='am_onyx', narration_text=' '.join(segments),
                          segments=segments, visual_description=visual,
                          source='evidence/tokenization.json' if kind not in ('embedding','prediction','boundary','closing') else 'Constructed teaching graphic; see SOURCES.md',
                          timing_status='pending audio measurement'))
    sheet=dict(schema_version='2', metadata=dict(title='Tokens, Not Words',
        student_name='Jayaraman Gopalakrishnan Shyam Sundar',course='INFO 7375',persona='Dunkin (speaking style; no affiliation)',
        engine='kokoro',voice_kokoro='am_onyx',aspect_ratio='16:9',resolution='1920x1080',fps=24,
        human_review='pending',target_duration_s=[170,170],
        workflow='Brutalist audio-first; direct toolkit audio helpers, custom Manim scenes, FFmpeg assembly'),beats=beats)
    (ROOT/'beat_sheet.json').write_text(json.dumps(sheet,indent=2),encoding='utf-8')
    print('Narration words:',sum(len(b['narration_text'].split()) for b in beats))

if __name__=='__main__': main()
