"""Run limits from GATE.md. Only Tushar changes these, through a dated decision-log entry.

The board config chooses which boards run within these limits; it cannot raise them.
"""

MAX_DISTINCT_BOARDS = 5          # GATE "5 distinct boards"; a sixth is invalid config (F6)
MAX_HTTP_ATTEMPTS = 12           # every transport call, including retries (GATE, F8)
RUN_SECONDS = 60                 # whole run, monotonic clock
NETWORK_WINDOW_SECONDS = 58      # network deadline from run start (F10)
FINALIZE_RESERVE_SECONDS = RUN_SECONDS - NETWORK_WINDOW_SECONDS  # 2 s for evidence and state
ATTEMPT_CAP_SECONDS = 10         # per transport attempt, or the network time left if smaller
RETRY_WAIT_SECONDS = 1           # wait before the single retry of a timeout or 5xx
RETRY_MIN_NETWORK_SECONDS = 2    # F11: network time needed before starting the wait
RETRY_MIN_ATTEMPT_SECONDS = 1    # F11: attempt time still needed after the wait
