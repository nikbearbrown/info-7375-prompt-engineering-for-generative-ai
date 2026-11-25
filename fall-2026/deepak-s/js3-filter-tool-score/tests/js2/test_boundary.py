"""Boundary cases B01-B16 from POLICY.md. Written by Claude Code (Claude Opus 5.5), 2026-11-10,
after Deepak's predictions were committed in 891446a. SEEDED inputs only; no network.
Each test prints one line "Bxx: policy <decision>; outcome <what the tool did>"; run with -rP to see them.
"""
import checks
from js2kit import wd  # noqa: F401  (fixture)


def test_B01_off_allowlist_host(wd):
    checks.check_B01(wd)


def test_B02_suffix_trick_host(wd):
    checks.check_B02(wd)


def test_B03_userinfo_trick(wd):
    checks.check_B03(wd)


def test_B04_plain_http(wd):
    checks.check_B04(wd)


def test_B05_post_to_allowed_host(wd):
    checks.check_B05(wd)


def test_B06_redirect_refused(wd):
    checks.check_B06(wd)


def test_B07_dotdot_escape(wd):
    checks.check_B07(wd)


def test_B08_prefix_trick(wd):
    checks.check_B08(wd)


def test_B09_symlink_escape(wd):
    checks.check_B09(wd)


def test_B10_absolute_path(wd):
    checks.check_B10(wd)


def test_B11_read_config(wd):
    checks.check_B11(wd)


def test_B12_write_config(wd):
    checks.check_B12(wd)


def test_B12_write_config_with_injected_approver(wd):
    checks.check_B12_approved(wd)


def test_B13_state_reset_noninteractive(wd):
    checks.check_B13(wd)


def test_B14_read_home_secret(wd):
    checks.check_B14(wd)


def test_B15_nonstandard_port(wd):
    checks.check_B15(wd)


def test_B16_ip_literal(wd):
    checks.check_B16(wd)
