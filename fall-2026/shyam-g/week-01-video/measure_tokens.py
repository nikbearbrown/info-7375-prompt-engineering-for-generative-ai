"""Record actual tiktoken output; no model inference is performed."""
import json
import importlib.metadata
from datetime import datetime, timezone
from pathlib import Path
import tiktoken

def measure():
    rows = []
    for name in ('cl100k_base', 'o200k_base'):
        enc = tiktoken.get_encoding(name)
        for word, letter in [('strawberry', 'r'), ('banana', 'a'), ('occurrence', 'r')]:
            ids = enc.encode(word)
            fragments = [enc.decode_single_token_bytes(i).decode('utf-8') for i in ids]
            assert ''.join(fragments) == word
            assert enc.decode(ids) == word
            counts = [fragment.count(letter) for fragment in fragments]
            assert sum(counts) == word.count(letter)
            rows.append(dict(encoding=name, text=word, token_ids=ids, fragments=fragments,
                             letter=letter, character_length=len(word), character_count=word.count(letter),
                             counts_per_fragment=counts,
                             character_positions_zero_based=[i for i,c in enumerate(word) if c == letter]))
    return dict(timestamp_utc=datetime.now(timezone.utc).isoformat(),
                tiktoken_version=importlib.metadata.version('tiktoken'), rows=rows,
                finding='Tokenization is reversible. Character counts are preserved in decoded text, not destroyed. Token positions are not character positions. No LLM accuracy test was performed.')

if __name__ == '__main__':
    result = measure()
    dest = Path(__file__).parent / 'evidence'
    dest.mkdir(exist_ok=True)
    output = json.dumps(result, indent=2)
    (dest / 'tokenization.json').write_text(output, encoding='utf-8')
    print(output)
