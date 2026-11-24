# Prior work, read 2026-11-23

What the three sources in part 2 of the film say, read on 2026-11-23 (the public pages, fetched in a Claude Code session). Quotes are short and exact. ShellCheck and explainshell, at the end, were added to the appendix after a final strict check; they are not in the film.

## try: https://github.com/binpash/try

- What it does: "Inspect, control, and manipulate a command's effects before modifying your live system."
- It runs the command in an overlay sandbox, then "will ask you to commit the changes made".
- Platform: Linux. It uses Linux namespaces (`unshare`) and overlayfs, and needs "Linux 5.11 or higher". macOS and Windows are not mentioned.
- Checking the effects against what the user asked for: not mentioned. The only review step is the commit prompt.

## InterCode: https://arxiv.org/abs/2306.14898

- John Yang, Akshara Prabhakar, Karthik Narasimhan, et al. Submitted 26 June 2023 (v3: 30 October 2023).
- A framework for interactive coding: code is the action, and the result of running it is the observation. Environments for Bash, SQL and Python (data from NL2Bash, Spider and MBPP).
- Finding stated in the abstract: "Our results showcase the benefits of interactive code generation." No Bash-specific accuracy number is in the abstract.

## NL2SH: https://arxiv.org/abs/2502.06858

- Finnian Westenfelder, Erik Hemberg, Miguel Tulla, et al. Submitted 7 February 2025 (NAACL 2025).
- "a manually verified test set of 600 instruction-command pairs".
- A heuristic that "can determine the functional equivalence of two Bash commands with 95% confidence".
- Parsing, in-context learning, in-weight learning and constrained decoding "can improve NL2SH accuracy by up to 32%".

## ShellCheck: https://github.com/koalaman/shellcheck

- README read 2026-11-23: "ShellCheck - A shell script static analysis tool" that "gives warnings and suggestions for bash/sh shell scripts".
- Its gallery of bad code lists `rm -rf "$STEAMROOT/"*` as "Catastrophic rm" and `find -name \*.bak -o -name \*~ -delete` as "Implicit precedence in find".
- It analyses the script text. Running the command or looking at the user's files: not mentioned.

## explainshell: https://explainshell.com

- README read 2026-11-23 (https://github.com/idank/explainshell): it explains a command line "by matching each argument to the relevant help text in the manpage".
- It parses the command into a syntax tree and matches each part to manpage text. Running the command or looking at the user's files: not mentioned.
