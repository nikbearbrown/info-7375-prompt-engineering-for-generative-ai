"""WRONG VERSION 2b (CONTRACT.md): the state file is written once and never updated,
so later runs re-report postings already seen."""
import os
from jsagent import watch

_real_save = watch.save_state


def apply():
    def save_state(path, state):
        if not os.path.exists(path):
            _real_save(path, state)
    watch.save_state = save_state
