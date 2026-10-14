# Fact check

- strawberry: 10 ASCII characters; r at zero-based indices 2, 7, 8; count 3.
- cl100k_base: [496, 675, 15717] → [str, aw, berry]; fragment r counts [1, 0, 2].
- o200k_base: [302, 1618, 19772] → [st, raw, berry]; fragment r counts [0, 1, 2].
- banana: [88847] in cl100k_base; [183143] in o200k_base; a count 3.
- occurrence: [14310, 21201] and [16533, 29194], respectively; [occ, urrence]; r count 2.
- All six encode/decode round trips and additive count checks execute as assertions in measure_tokens.py. Input context matters; these examples omit leading spaces.
- Corrected the requested premise: no character counts disappear from this reversible representation. Character positions are not individually indexed as model input tokens; that differs from information being destroyed.
- Learned vectors shown are invented diagrams and always labeled. Spelling-related information may be learned. No embedding weights were inspected.
- No model counting experiment was run, so neither a failure rate nor causation for a particular response is established. Claude tokenizer behavior is not established by OpenAI tiktoken.
- Scratchpads can help but do not guarantee truth. Python's string count returns verified answers for these ASCII strings; Unicode grapheme counting is outside this demonstration.
