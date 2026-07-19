"""The risk analyzer: composes the heuristic checks into one score.

Composition + Strategy in action. ``RiskAnalyzer`` holds a list of
``Check`` objects and doesn't care what any of them do internally — it
just runs each one and adds up the points. New rules drop in without
touching this class (open/closed principle).
"""

from __future__ import annotations

from dataclasses import dataclass, field

from .checks.base import Check, CheckOutcome
from .checks.rules import default_checks
from .url import ParsedUrl


@dataclass
class ScanReport:
    """The aggregated result of analyzing one URL."""

    url: str
    score: int
    verdict: str
    outcomes: list[CheckOutcome] = field(default_factory=list)

    @property
    def triggered(self) -> list[CheckOutcome]:
        return [outcome for outcome in self.outcomes if outcome.triggered]


class RiskAnalyzer:
    """Runs every check against a URL and turns the points into a verdict."""

    SAFE_MAX = 20
    SUSPICIOUS_MAX = 45

    def __init__(self, checks: list[Check] | None = None, max_score: int = 100) -> None:
        self._checks = checks if checks is not None else default_checks()
        self._max_score = max_score

    def analyze(self, raw_url: str) -> ScanReport:
        url = ParsedUrl.parse(raw_url)
        outcomes = [check.evaluate(url) for check in self._checks]
        score = min(sum(outcome.points for outcome in outcomes), self._max_score)
        return ScanReport(
            url=url.raw,
            score=score,
            verdict=self._verdict(score),
            outcomes=outcomes,
        )

    def _verdict(self, score: int) -> str:
        if score <= self.SAFE_MAX:
            return "Safe"
        if score <= self.SUSPICIOUS_MAX:
            return "Suspicious"
        return "Dangerous"
