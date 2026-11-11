"""Plausible-but-wrong loops from GATE.md section 6 (Saloni's wording).
Each changes exactly one hook. The tests run the same checks against Loop and against these,
and require every check to pass for Loop and to fail for its wrong version.
"""
from jsagent.loop import Loop


class WV1EmptyIsSuccess(Loop):
    """GATE 6.1: an empty job list is treated as a successful board with zero new jobs."""

    def classify(self, board, result):
        out = super().classify(board, result)
        return ("ok", []) if out[0] == "suspicious_empty" else out


class WV2SilentSkip(Loop):
    """GATE 6.2: a failed or timed-out board is skipped and the run still says finished."""

    def exit_status(self, flags, boards):
        return "finished" if not flags else super().exit_status(flags, boards)
