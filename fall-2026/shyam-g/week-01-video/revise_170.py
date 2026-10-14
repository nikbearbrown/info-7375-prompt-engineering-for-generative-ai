"""Apply the user's 2:50 revision to the authored script and documentation."""
import json, pprint
from pathlib import Path
from prepare import DATA
ROOT=Path(__file__).resolve().parent
NARRATION=[
["How many r's are in strawberry? Three. Why can a language model stumble on that? Start with the ruler it uses.","Models process tokens, not a separate position for every letter. Counting becomes less direct, not impossible.","Let's inspect two real tokenizers and check the count."],
["A tokenizer converts text into integer IDs. A token can cover a word, part of a word, or other text.","We ran tik token locally with both encodings shown here: lowercase inputs, no leading spaces.","These are OpenAI encodings, not measurements of Claude's tokenizer."],
["First, strawberry in c l one hundred k base: str, aw, berry. These are the exact measured IDs.","Count r inside each chunk: one, zero, two. Add them: three.","Three tokens matching three r's is a coincidence. Token count is not a letter-counting rule."],
["Switch encodings. Strawberry now splits into st, raw, berry. Different boundaries and IDs; same spelling.","The r counts become zero, one, two. Still three. The first r moved into another chunk, not out of the text.","Token boundaries depend on the encoding."],
["Banana is one token in both encodings. Different IDs, but still three a's. One token does not mean one letter.","Occurrence splits into occ and urrence. Both r's are in the second chunk. These IDs are also measured.","Counting chunks and counting characters are different operations."],
["Embedding lookup selects a learned vector for each token ID. These colored vectors are constructed illustrations, not real model weights.","Ten character positions become three token positions for strawberry. Internal letters have no separate input token position.","But vectors can carry spelling-related information. Lookup does not prove spelling was erased."],
["Tokenization is reversible. Decode these IDs and every letter of strawberry comes back.","All six word-and-encoding pairs passed our Python round-trip checks. Counts across decoded fragments also matched the original strings.","Less direct access does not mean lost characters."],
["Predicting an answer is not automatically the same as running a character-counting loop.","We tested tokenizers, not model responses. This experiment gives no model failure rate and cannot diagnose a particular wrong answer.","Keep the conclusion as narrow as the evidence."],
["Run Python's count operation. Strawberry has three r's; banana has three a's; occurrence has two r's.","These results were executed locally. This code view reconstructs recorded output; it is not a live screen capture.","Run the operation. Inspect the result. Fluency alone verifies nothing."],
["Tokens do not make models unable to count. A model may answer correctly, use a scratchpad, use character-level representations, or call tools.","Scratchpads still do not guarantee correctness. Two encodings do not establish how every model works.","Our claim: token positions differ from character positions. Not a universal failure diagnosis."],
["Try another word: encode it, inspect the IDs, decode it, then count the target letter.","A token is a processing unit, not a spelling unit. Use the right ruler.","Strawberry: three r's. Verified locally."]
]
source=(ROOT/'prepare.py').read_text(encoding='utf-8')
start=source.index('DATA = [');end=source.index('\ndef main():',start)
new=[(d[0],d[1],n,d[3]) for d,n in zip(DATA,NARRATION)]
source=source[:start]+'DATA = '+pprint.pformat(new,width=110,sort_dicts=False)+'\n\n'+source[end:]
source=source.replace('target_duration_s=[180,240]','target_duration_s=[170,170]')
(ROOT/'prepare.py').write_text(source,encoding='utf-8')
print('Revised word count:',sum(len(t.split()) for n in NARRATION for t in n))
with (ROOT/'USER-PROMPT.md').open('a',encoding='utf-8') as f:
    f.write('\n\n## Later user revision (supersedes earlier runtime)\n\nneed at 2 minutes and 50 seconds\n')
