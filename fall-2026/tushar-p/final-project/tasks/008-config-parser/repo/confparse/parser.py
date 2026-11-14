"""A small INI-style configuration parser.

Format
------
- Blank lines are ignored.
- A line whose first non-space character is ";" or "#" is a comment.
- "[name]" starts a section. Section names are case-sensitive. Keys that
  come before any section go in the unnamed section "".
- "key = value" sets a key in the current section. Whitespace around the
  key and around the value is removed. Keys are case-insensitive: they are
  stored lower case, and get() lower-cases the key it is given.
- A value may be wrapped in double quotes. Inside the quotes everything is
  kept as is, including ";", "#", and leading or trailing spaces, and \"
  stands for one double quote character.
- Outside quotes, ";" or "#" starts an inline comment, which is removed.
- A line that starts with a space or a tab, right after a key line or
  another such line, continues the previous value: its text is appended
  after a single space.
- "${name}" in a value is replaced by the value of key "name" in the same
  section, and "${section:name}" by the value of "name" in another section.
  References inside a referenced value are replaced too. A reference to a
  key that does not exist, or a loop of references, raises ConfigError.
- Anything else (a line with no "=", a bad section header, an unterminated
  quoted value) raises ConfigError, with the line number where there is one.
"""

import re


class ConfigError(Exception):
    """Raised for a malformed file or a bad reference."""


_TRUE = {"true", "yes", "on", "1"}
_FALSE = {"false", "no", "off", "0"}

# A reference: "${" then anything up to the first "}".
_REF = re.compile(r"\$\{([^}]*)\}")


class Config:
    """Parsed configuration: named sections of string keys and values."""

    def __init__(self, data):
        self._data = data  # {section: {key: value}}

    def sections(self):
        """Return the section names in the order they first appeared. The
        unnamed section "" is included only if it has keys."""
        return list(self._data)

    def items(self, section):
        """Return the (key, value) pairs of section, in file order."""
        return list(self._data.get(section, {}).items())

    def __contains__(self, section):
        return section in self._data

    def get(self, section, key, default=None):
        """Return the value of key in section, or default if it is not set."""
        return self._data.get(section, {}).get(key.lower(), default)

    def getint(self, section, key, default=None):
        """Return get() as an int. A value that is not an integer raises
        ConfigError."""
        value = self.get(section, key)
        if value is None:
            return default
        try:
            return int(value)
        except ValueError:
            raise ConfigError(f"{section}.{key}: not an integer: {value!r}") from None

    def getbool(self, section, key, default=None):
        """Return get() as a bool: "true", "yes", "on" and "1" are True, and
        "false", "no", "off" and "0" are False, in any case. Anything else
        raises ConfigError."""
        value = self.get(section, key)
        if value is None:
            return default
        word = value.strip().lower()
        if word in _TRUE:
            return True
        if word in _FALSE:
            return False
        raise ConfigError(f"{section}.{key}: not a boolean: {value!r}")

    def getlist(self, section, key, default=None):
        """Return get() split on commas, each item trimmed, empty items
        dropped: "a, b,,c" -> ["a", "b", "c"]."""
        value = self.get(section, key)
        if value is None:
            return default
        return [item.strip() for item in value.split(",") if item.strip()]


def parse(text):
    """Return a Config for text (see the module docstring for the format)."""
    return Config(_interpolate_all(_read(text)))


def _read(text):
    """Return {section: {key: value}} for text, before interpolation."""
    data = {"": {}}
    section = ""
    last_key = None  # the key a continuation line would extend
    for number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            last_key = None
            continue
        if stripped[0] in ";#":
            continue
        if line[0] in " \t" and last_key is not None:
            more = _value(line, number)
            data[section][last_key] = (data[section][last_key] + " " + more).strip()
            continue
        if stripped.startswith("["):
            if not stripped.endswith("]") or not stripped[1:-1].strip():
                raise ConfigError(f"line {number}: bad section header: {stripped!r}")
            section = stripped[1:-1].strip()
            data.setdefault(section, {})
            last_key = None
            continue
        if "=" not in stripped:
            raise ConfigError(f"line {number}: expected key = value: {stripped!r}")
        key, _, raw = stripped.partition("=")
        key = key.strip().lower()
        if not key:
            raise ConfigError(f"line {number}: empty key")
        data[section][key] = _value(raw, number)
        last_key = key
    if not data[""]:
        del data[""]
    return data


def _value(raw, number):
    """Return the value in raw: inline comment removed, whitespace trimmed,
    and the quotes removed if it is quoted."""
    value = _strip_comment(raw).strip()
    if value.startswith('"'):
        return _unquote(value, number)
    return value


def _strip_comment(raw):
    """Return raw without its inline comment: everything from the first ";"
    or "#" that is outside double quotes."""
    in_quotes = False
    for i, ch in enumerate(raw):
        if ch == '"':
            in_quotes = not in_quotes
        elif ch in ";#" and not in_quotes:
            return raw[:i]
    return raw


def _unquote(value, number):
    """Return the text inside a double-quoted value, with \" turned into "."""
    if len(value) < 2 or not value.endswith('"'):
        raise ConfigError(f"line {number}: unterminated quoted value: {value!r}")
    return value[1:-1].replace('\\"', '"')


def _interpolate_all(data):
    """Return data with every ${...} reference replaced."""
    return {
        section: {key: _interpolate(data, section, key, ()) for key in keys}
        for section, keys in data.items()
    }


def _interpolate(data, section, key, seen):
    """Return the value of section.key with its references replaced. seen
    holds the (section, key) pairs being replaced, to catch loops."""
    if (section, key) in seen:
        raise ConfigError(f"reference loop at {section}.{key}")
    seen = seen + ((section, key),)

    def replace(match):
        ref = match.group(1)
        ref_section, sep, ref_key = ref.rpartition(":")
        if not sep:  # no ":": the same section
            ref_section = section
        ref_key = ref_key.strip().lower()
        if ref_key not in data.get(ref_section, {}):
            raise ConfigError(f"{section}.{key}: unknown reference ${{{ref}}}")
        return _interpolate(data, ref_section, ref_key, seen)

    return _REF.sub(replace, data[section][key])
