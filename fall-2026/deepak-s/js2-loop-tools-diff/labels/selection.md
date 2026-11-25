# Selection of the 20 postings (committed before labeling)

Date: 2026-10-30 (ET)
Source: run 1 baseline raw response, evidence/raw/20261030T025837Z_stripe.raw (board stripe,
sha256 81de5fbf8e97a28e6b275be1289762e4ca4e3334dd82d3b669f9bdbb7a4722ce), parsed with
jobwatch.postings.parse_body: 736 postings, all judgeable.

## 4 postings the contract rule marks relevant
Computed with jobwatch.rule.apply_rule and examples/persona_resume.json.
- 8222149
- 8197886
- 7983456
- 8243617

## 8 chosen by me from titles
From the postings, other than the 4 above, whose title contains ML, AI, Machine Learning, Data or
Scientist as a whole word (CONTRACT.md whole-word match); chosen from id, title and location only.
- 8148653
- 8224915
- 8144196
- 5601879
- 8022713
- 8194283
- 7747640
- 8198323

## Exclusion set for the random draw (the 12 above)
8222149, 8197886, 7983456, 8243617, 8148653, 8224915, 8144196, 5601879, 8022713, 8194283, 7747640, 8198323

## 8 drawn at random
Seed: 7375. `remaining` is the sorted list of all other posting ids, as strings: 736 - 12 = 724
ids, all 7 digits long. Drawn with Python 3.15.0:

```python
random.seed(7375); random.sample(remaining, 8)
```

Result, in draw order:
- 8175661
- 8174963
- 7962437
- 8237540
- 8191708
- 8203220
- 8212314
- 8175828
