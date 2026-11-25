# Comparison `plain`: each traced run against the same server not traced

Each answer is compared line by line, session by session (times left out); where two lines differ, every JSON field that differs is listed, and a tool result's text is compared as the JSON it holds.

## `own-a` against `own-plain`

- Answers: **the same** (SHA-256 of all answers without times: `81e722ad72d6fb0b...` and `81e722ad72d6fb0b...`)
- The last line of each session's stderr: **the same**

## `other-a` against `other-plain`

- Answers: **the same** (SHA-256 of all answers without times: `3c9b99926cefa3e8...` and `3c9b99926cefa3e8...`)
- The last line of each session's stderr: **the same**; bytes: `UnicodeDecodeError: 'utf-8' codec can't decode byte 0xff in position 0: invalid start byte`; deep: `RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string`
