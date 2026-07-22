"""Unit tests for individual checks and the risk analyzer.

These need no database — they test the pure business logic directly.
"""

from app.analyzer import RiskAnalyzer
from app.checks.rules import (
    AtSymbolCheck,
    BrandImpersonationCheck,
    IpAddressCheck,
    NoHttpsCheck,
    NonStandardPortCheck,
    PunycodeCheck,
    RiskyTldCheck,
    ShortenerCheck,
    SuspiciousFileExtensionCheck,
)
from app.url import ParsedUrl


def u(raw: str) -> ParsedUrl:
    return ParsedUrl.parse(raw)


# --- individual checks ---------------------------------------------------

def test_ip_address_triggers_on_raw_ip():
    assert IpAddressCheck().evaluate(u("http://192.168.0.1/login")).triggered


def test_ip_address_passes_on_domain():
    assert not IpAddressCheck().evaluate(u("https://google.com")).triggered


def test_at_symbol_triggers():
    assert AtSymbolCheck().evaluate(u("http://safe@evil.com")).triggered


def test_risky_tld():
    assert RiskyTldCheck().evaluate(u("http://foo.xyz")).triggered
    assert not RiskyTldCheck().evaluate(u("http://foo.com")).triggered


def test_punycode_triggers():
    assert PunycodeCheck().evaluate(u("http://xn--pple-43d.com")).triggered


def test_shortener_triggers():
    assert ShortenerCheck().evaluate(u("http://bit.ly/abc")).triggered


def test_no_https():
    assert NoHttpsCheck().evaluate(u("http://example.com")).triggered
    assert not NoHttpsCheck().evaluate(u("https://example.com")).triggered


def test_brand_impersonation_triggers_on_fake_domain():
    assert BrandImpersonationCheck().evaluate(u("http://paypal.secure-login.xyz")).triggered


def test_brand_impersonation_passes_on_real_domain():
    assert not BrandImpersonationCheck().evaluate(u("https://www.paypal.com/signin")).triggered


def test_file_extension_triggers():
    assert SuspiciousFileExtensionCheck().evaluate(u("http://x.com/setup.exe")).triggered


def test_non_standard_port():
    assert NonStandardPortCheck().evaluate(u("http://x.com:4444/")).triggered
    assert not NonStandardPortCheck().evaluate(u("https://x.com/")).triggered


# --- analyzer end to end (scoring + verdict) -----------------------------

def test_clean_url_is_safe():
    assert RiskAnalyzer().analyze("https://www.google.com").verdict == "Safe"


def test_obvious_phish_is_dangerous():
    report = RiskAnalyzer().analyze(
        "http://paypal-verify.secure-update.xyz@192.168.0.10/login-confirm-account"
    )
    assert report.verdict == "Dangerous"
    assert report.score > 45


def test_score_is_capped_at_100():
    report = RiskAnalyzer().analyze(
        "http://paypal-login-verify-account.secure-signin.xyz@10.0.0.1:4444/confirm/setup.exe"
    )
    assert report.score <= 100


def test_only_triggered_flags_are_reported():
    report = RiskAnalyzer().analyze("https://www.google.com")
    assert all(o.triggered for o in report.triggered)
