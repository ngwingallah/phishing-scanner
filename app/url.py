"""A small value object that parses a raw URL into inspectable parts.

Keeping parsing in one place means every heuristic check works from the
same, already-validated view of the URL instead of re-parsing strings.
"""

from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import urlparse


@dataclass
class ParsedUrl:
    """An immutable, parsed view of a URL used by the heuristic checks."""

    raw: str
    scheme: str = ""
    host: str = ""
    path: str = ""
    query: str = ""
    port: int | None = None

    @classmethod
    def parse(cls, raw: str) -> "ParsedUrl":
        candidate = (raw or "").strip()
        # urlparse needs a scheme to reliably find the host component.
        if "://" not in candidate:
            candidate = "http://" + candidate
        parsed = urlparse(candidate)
        # parsed.port raises ValueError on a malformed port; treat as none.
        try:
            port = parsed.port
        except ValueError:
            port = None
        return cls(
            raw=(raw or "").strip(),
            scheme=parsed.scheme.lower(),
            host=(parsed.hostname or "").lower(),
            path=parsed.path or "",
            query=parsed.query or "",
            port=port,
        )

    @property
    def labels(self) -> list[str]:
        """The dot-separated parts of the host, e.g. ['mail', 'google', 'com']."""
        return [label for label in self.host.split(".") if label]

    @property
    def tld(self) -> str:
        """The top-level domain, e.g. 'com'. Empty for bare hosts/IPs."""
        return self.labels[-1] if len(self.labels) >= 2 else ""

    @property
    def registered_domain(self) -> str:
        """A rough registered domain: the last two labels, e.g. 'google.com'.

        Not a full public-suffix parse, but enough to tell whether a brand
        name sits in the real domain or only in a subdomain/path.
        """
        return ".".join(self.labels[-2:]) if len(self.labels) >= 2 else self.host

    @property
    def length(self) -> int:
        return len(self.raw)
