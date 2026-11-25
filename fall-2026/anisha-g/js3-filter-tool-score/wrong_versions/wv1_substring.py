"""WRONG VERSION 1 (FILTER.md 4.1): substring match. 'BI' matches inside 'ability', 'analyst' inside 'psychoanalysts'."""
import sys
from wrong_versions._mutate import clone
def has_phrase(text, phrase):
    return bool(text) and phrase.lower() in text.lower()
sys.modules[__name__] = clone(__name__, has_phrase=has_phrase)
