# Comparison `python`: each run under one Python against the same run under the other

Answers compared line by line, session by session, times left out.

| Run | Pythons | Answers | What the trace saw that differs |
|---|---|---|---|
| `own-a` | 3.12.14 and 3.9.6 | the same | modules: 3.12.14 none, 3.9.6 _posixsubprocess, select, selectors, subprocess |
| `own-b` | 3.12.14 and 3.9.6 | the same | modules: 3.12.14 none, 3.9.6 _posixsubprocess, select, selectors, subprocess |
| `own-c` | 3.12.14 and 3.9.6 | the same | modules: 3.12.14 none, 3.9.6 _posixsubprocess, select, selectors, subprocess |
| `own-d` | 3.12.14 and 3.9.6 | the same | modules: 3.12.14 none, 3.9.6 _posixsubprocess, select, selectors, subprocess |
| `own-plain` | 3.12.14 and 3.9.6 | the same | nothing |
| `other-a` | 3.12.14 and 3.9.6 | the same | nothing |
| `other-c` | 3.12.14 and 3.9.6 | the same | nothing |
| `other-plain` | 3.12.14 and 3.9.6 | the same | nothing |
