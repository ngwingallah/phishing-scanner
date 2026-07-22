"""Concrete phishing heuristics.

Each class inherits from :class:`Check` and overrides ``evaluate`` — a
textbook example of inheritance + polymorphism. The weights are a simple,
explainable scoring model (your "proposed algorithm" for the report).
"""

from __future__ import annotations

import ipaddress

from .base import Check, CheckOutcome
from ..url import ParsedUrl

# Reference data the checks lean on.
SHORTENERS = {
    "bit.ly", "tinyurl.com", "goo.gl", "t.co", "ow.ly",
    "is.gd", "buff.ly", "cutt.ly", "rebrand.ly", "rb.gy",
}
RISKY_TLDS = {
    "zip", "mov", "xyz", "top", "tk", "gq", "ml", "cf",
    "ga", "work", "click", "link", "country", "kim", "rest",
}
SUSPICIOUS_WORDS = {
    "login", "verify", "secure", "account", "update", "confirm",
    "bank", "password", "signin", "webscr", "ebayisapi", "wallet",
}
# Brands frequently impersonated, mapped to their real registered domains.
KNOWN_BRANDS = {
    "paypal": "paypal.com",
    "google": "google.com",
    "apple": "apple.com",
    "microsoft": "microsoft.com",
    "amazon": "amazon.com",
    "facebook": "facebook.com",
    "netflix": "netflix.com",
    "instagram": "instagram.com",
    "whatsapp": "whatsapp.com",
    "mtn": "mtn.com",
}
# File extensions that are dangerous to download from a link.
RISKY_EXTENSIONS = (".exe", ".scr", ".msi", ".apk", ".bat", ".zip", ".rar", ".js")
# Ports that are normal for web traffic; anything else is worth flagging.
STANDARD_PORTS = {80, 443, 8080}


class IpAddressCheck(Check):
    name = "Raw IP address"
    weight = 25

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        try:
            ipaddress.ip_address(url.host)
            return self._outcome(True, "URL points at a raw IP address instead of a domain name.")
        except ValueError:
            return self._outcome(False, "Host is a normal domain name.")


class UrlLengthCheck(Check):
    name = "Excessive length"
    weight = 10
    threshold = 75

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        if url.length > self.threshold:
            return self._outcome(True, f"URL is unusually long ({url.length} characters).")
        return self._outcome(False, "URL length is within a normal range.")


class SubdomainCheck(Check):
    name = "Too many subdomains"
    weight = 12
    threshold = 3

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        depth = max(len(url.labels) - 2, 0)
        if depth >= self.threshold:
            return self._outcome(True, f"Host nests {depth} subdomain levels.")
        return self._outcome(False, "Subdomain depth looks normal.")


class AtSymbolCheck(Check):
    name = "@ in URL"
    weight = 18

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        if "@" in url.raw:
            return self._outcome(True, "URL contains '@', which can hide the true destination host.")
        return self._outcome(False, "No '@' character in the URL.")


class RiskyTldCheck(Check):
    name = "Risky TLD"
    weight = 12

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        if url.tld in RISKY_TLDS:
            return self._outcome(True, f"Top-level domain '.{url.tld}' is frequently abused for phishing.")
        return self._outcome(False, "Top-level domain is not on the risky list.")


class HyphenCheck(Check):
    name = "Hyphen-heavy domain"
    weight = 8
    threshold = 3

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        count = url.host.count("-")
        if count >= self.threshold:
            return self._outcome(True, f"Domain uses {count} hyphens, common in look-alike domains.")
        return self._outcome(False, "Hyphen usage is normal.")


class DeceptiveHttpsCheck(Check):
    name = "Deceptive 'https' token"
    weight = 10

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        if "https" in url.host:
            return self._outcome(True, "'https' appears inside the host name to look trustworthy.")
        return self._outcome(False, "No deceptive 'https' token in the host.")


class ShortenerCheck(Check):
    name = "URL shortener"
    weight = 8

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        if url.host in SHORTENERS:
            return self._outcome(True, f"Uses shortener '{url.host}', which conceals the real URL.")
        return self._outcome(False, "Host is not a known URL shortener.")


class PunycodeCheck(Check):
    name = "Punycode / homoglyph"
    weight = 15

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        if "xn--" in url.host:
            return self._outcome(True, "Host uses punycode, a common homoglyph (look-alike) technique.")
        return self._outcome(False, "No punycode in the host.")


class SuspiciousKeywordCheck(Check):
    name = "Suspicious keywords"
    weight = 10

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        haystack = url.raw.lower()
        hits = sorted(word for word in SUSPICIOUS_WORDS if word in haystack)
        if hits:
            return self._outcome(True, f"Contains phishing keywords: {', '.join(hits)}.")
        return self._outcome(False, "No suspicious keywords found.")


class NoHttpsCheck(Check):
    name = "No HTTPS"
    weight = 6

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        if url.scheme != "https":
            return self._outcome(True, "URL is not served over HTTPS.")
        return self._outcome(False, "URL uses HTTPS.")


class BrandImpersonationCheck(Check):
    name = "Brand impersonation"
    weight = 20

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        haystack = f"{url.host}{url.path}".lower()
        for brand, real_domain in KNOWN_BRANDS.items():
            # Brand name appears somewhere, but the real domain is not the host.
            if brand in haystack and url.registered_domain != real_domain:
                return self._outcome(
                    True,
                    f"Mentions '{brand}' but the domain is not {real_domain}.",
                )
        return self._outcome(False, "No brand impersonation detected.")


class SuspiciousFileExtensionCheck(Check):
    name = "Dangerous file extension"
    weight = 12

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        path = url.path.lower()
        for ext in RISKY_EXTENSIONS:
            if path.endswith(ext):
                return self._outcome(True, f"Link points to a '{ext}' file, risky to download.")
        return self._outcome(False, "No dangerous file extension in the path.")


class NonStandardPortCheck(Check):
    name = "Non-standard port"
    weight = 10

    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        if url.port is not None and url.port not in STANDARD_PORTS:
            return self._outcome(True, f"Uses non-standard port {url.port}.")
        return self._outcome(False, "Uses a standard web port.")


def default_checks() -> list[Check]:
    """The standard rule set, in the order they appear in results."""
    return [
        IpAddressCheck(),
        UrlLengthCheck(),
        SubdomainCheck(),
        AtSymbolCheck(),
        RiskyTldCheck(),
        HyphenCheck(),
        DeceptiveHttpsCheck(),
        ShortenerCheck(),
        PunycodeCheck(),
        SuspiciousKeywordCheck(),
        NoHttpsCheck(),
        BrandImpersonationCheck(),
        SuspiciousFileExtensionCheck(),
        NonStandardPortCheck(),
    ]
