# Did I run `lessons/01-randomness-and-first-prompts/code/main.py`?

**Yes.** Checked 2026-09-23. Recording it here because the assignment names that
file specifically, and "I assumed it wasn't relevant" is not a good enough answer.

Source: `nikbearbrown/info-7375-prompt-engineering-for-generative-ai`,
branch `main`, path `lessons/01-randomness-and-first-prompts/code/main.py`
(fetched via `raw.githubusercontent.com`, HTTP 200).

## What it actually prints

```
$ python3 main.py
{
  "probabilities": [
    0.09003057317038046,
    0.24472847105479764,
    0.6652409557748218
  ],
  "counts": {
    "1": 268,
    "2": 630,
    "0": 102
  }
}
```

## What it contains

Three functions — `probabilities(logits, temperature)`, `sample(logits, count,
seed, temperature)`, `demo()`. Imports are `math`, `random`, `collections.Counter`
only. It is the softmax / temperature / seeded-sampling reference implementation.

```
$ grep -in "token\|tiktoken\|encode\|bpe\|char" main.py
(no matches)
```

**There is no tokenization code in it.** No tokenizer, no token IDs, no character
handling — nothing my concept could draw a number from.

## Why its numbers are not the ones this video needs

Its output *is* the source for several Part 2 concepts on the assignment's own
eligible list:

| From the assignment's concept list | Where it comes from in `main.py` |
|---|---|
| "Expected count (665.24) versus observed count (630)" | `1000 × 0.6652409557748218 = 665.24`; `counts["2"] = 630` at `seed=7` |
| "Why subtracting the maximum changes the intermediates but not the distribution" | `peak = max(logits)` inside `probabilities()` |
| "Temperature as a concentration control — via the ratio" | the `temperature` divisor |
| "A seed makes a run repeatable; it does not make the answer true" | `random.Random(seed)`, default `seed=7` |

I verified both figures directly:

```
P(index 2)     = 0.6652409557748218
expected count = 665.24   (1000 * p[2])
observed count = 630      (seed=7)
```

My chosen concept — **"The unit is a token, not a word"** — is from **Part 1**, and
is about tokenization, not sampling. Quoting `665.24` or `630` in a video about token
IDs would be citing a real number that has nothing to do with the claim on screen,
which is worse than citing none.

## What I did instead

I generated the Part 1 equivalent — reproducible tokenizer numbers — with `tiktoken`
locally, and shipped the probes so anyone can re-run them:

```bash
python3 code/tokenize_probe.py
python3 code/embedding_probe.py
```

Same standard the instruction is asking for: real output from code that runs,
not plausible-looking figures. The probe scripts assert `decode(encode(w)) == w`
and print the result, so the round-trip is checked rather than assumed.
