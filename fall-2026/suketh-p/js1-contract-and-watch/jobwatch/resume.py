"""Validation of the fictional persona résumé (CONTRACT.md 'In' and 'Refuses').

Error messages name the field and never repeat its value, so a real résumé that is
passed in by mistake is not echoed to the screen."""

import re

from jobwatch.errors import InputError
from jobwatch.normalize import tokens

TOP_FIELDS = {"fictional", "name", "email", "phone", "skills", "preferences"}
PREFERENCE_FIELDS = {"title_word", "focus_terms", "excluded_title_words", "location_terms"}
TERM_LISTS = ("focus_terms", "excluded_title_words", "location_terms")
_PHONE_555 = re.compile(r"^\d{3}-555-\d{4}$")


def _require(ok, message):
    if not ok:
        raise InputError(f"résumé rejected: {message}")


def _is_text(value):
    return isinstance(value, str) and bool(value.strip())


def _check_fields(obj, expected, where):
    _require(isinstance(obj, dict), f"{where} must be a JSON object")
    missing, extra = sorted(expected - set(obj)), sorted(set(obj) - expected)
    _require(not missing, f"{where} is missing {missing}")
    _require(not extra, f"{where} has fields the contract does not name: {extra}")


def _check_terms(value, where):
    _require(isinstance(value, list) and value, f"{where} must be a nonempty list")
    for i, item in enumerate(value):
        _require(_is_text(item), f"{where}[{i}] must be a nonempty string")
        _require(bool(tokens(item)), f"{where}[{i}] has no letters or digits to match on")


def validate_resume(data):
    _check_fields(data, TOP_FIELDS, "résumé")
    _require(data["fictional"] is True, "resume.fictional must be true; only a fictional persona is accepted")
    _require(_is_text(data["name"]), "resume.name must be a nonempty string")
    _require(_is_text(data["email"]) and data["email"].endswith("@example.com"),
             "resume.email must be an @example.com address")
    _require(isinstance(data["phone"], str) and bool(_PHONE_555.match(data["phone"])),
             "resume.phone must use the 555 exchange, in the form 202-555-0147")
    _check_terms(data["skills"], "resume.skills")
    prefs = data["preferences"]
    _check_fields(prefs, PREFERENCE_FIELDS, "resume.preferences")
    _require(_is_text(prefs["title_word"]) and bool(tokens(prefs["title_word"])),
             "resume.preferences.title_word must be a nonempty word")
    for key in TERM_LISTS:
        _check_terms(prefs[key], f"resume.preferences.{key}")
    return data
