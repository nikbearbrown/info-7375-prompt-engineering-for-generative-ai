import pytest

from confparse import ConfigError, parse

TEXT = r"""; settings for the demo
top = level

[server]
Host = example.org   ; inline comment
port = 8080
debug = Yes
# a full-line comment
banner = "  hello; world  "
quoted = "say \"hi\""
path = /srv/${name}
name = demo
tags = a, b,,c
description = first line
  second line
	third line

[Client]
url = http://${server:host}:${server:port}/
"""


@pytest.fixture
def cfg():
    return parse(TEXT)


def test_sections(cfg):
    assert cfg.sections() == ["", "server", "Client"]
    assert "client" not in cfg  # section names are case-sensitive


def test_unnamed_section(cfg):
    assert cfg.get("", "top") == "level"


def test_keys_are_case_insensitive(cfg):
    assert cfg.get("server", "host") == "example.org"
    assert cfg.get("server", "HOST") == "example.org"


def test_inline_comment_removed(cfg):
    assert cfg.get("server", "host") == "example.org"


def test_quoted_value_keeps_everything(cfg):
    assert cfg.get("server", "banner") == "  hello; world  "


def test_escaped_quote(cfg):
    assert cfg.get("server", "quoted") == 'say "hi"'


def test_escaped_quote_then_semicolon():
    cfg = parse(r'motto = "say \"hi; there\"" ; note' + "\n")
    assert cfg.get("", "motto") == 'say "hi; there"'


def test_continuation_lines(cfg):
    assert cfg.get("server", "description") == "first line second line third line"


def test_reference_same_section(cfg):
    assert cfg.get("server", "path") == "/srv/demo"


def test_reference_other_section(cfg):
    assert cfg.get("Client", "url") == "http://example.org:8080/"


def test_typed_getters(cfg):
    assert cfg.getint("server", "port") == 8080
    assert cfg.getbool("server", "debug") is True
    assert cfg.getlist("server", "tags") == ["a", "b", "c"]
    assert cfg.get("server", "missing", "x") == "x"


def test_bad_values_raise(cfg):
    with pytest.raises(ConfigError):
        cfg.getint("server", "host")
    with pytest.raises(ConfigError):
        cfg.getbool("server", "host")


@pytest.mark.parametrize("text", [
    "[]\n",
    "[unclosed\n",
    "no equals sign here\n",
    "key = \"unterminated\n",
    "a = ${missing}\n",
    "a = ${b}\nb = ${a}\n",
])
def test_errors(text):
    with pytest.raises(ConfigError):
        parse(text)
