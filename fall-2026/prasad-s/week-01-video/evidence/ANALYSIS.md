| | Probability (top class) | Expected | Observed | Diff |
|---|---|---|---|---|
| Temp 1.0 | 0.6652 | 665.24 | 630 | ~35 (2.4 SD) |
| Temp 0.5 | 0.8668 | 866.8 | 849 | ~18 (1.7 SD) |

My prediction was: the gap would get closer.

What I saw: at temperature 1, the top class missed its expected count by about 35 (about 2.4 standard deviations -- the expected spread for 1,000 draws at that probability is about ±14.9). At temperature 0.5, it missed by about 18 (about 1.7 standard deviations, expected spread about ±10.7). So my prediction was right, both in raw count and in standard-deviation terms.

Why I think this happens: when one option is much more likely than the others, a random sample has less space to drift away from the big slice's exact math. That explains why the expected spread shrinks as temperature drops -- that part is guaranteed by the math. What it doesn't fully explain is why this specific run also landed closer in standard-deviation terms; a single sample could land anywhere in that spread, so part of this result could be this seed's luck rather than a guaranteed pattern.

What this run does not prove: that this holds at other temperatures I haven't tried, like 2.0 -- or with a different seed. Both runs here used seed 7, so they aren't independent draws; a different seed might show a smaller or larger gap either way.
