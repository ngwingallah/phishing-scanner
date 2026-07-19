"""The abstract base every phishing heuristic inherits from.

This is the heart of the OOP design. Each concrete check is a *strategy*
that the RiskAnalyzer runs through one common interface (`evaluate`),
so the analyzer never needs to know how any individual rule works.
Adding a new rule = adding a subclass; no existing code changes.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass

from ..url import ParsedUrl


@dataclass
class CheckOutcome:
    """What a single check reports back after inspecting a URL."""

    name: str
    triggered: bool
    points: int
    reason: str


class Check(ABC):
    """Abstract base for every heuristic check.

    Subclasses set a ``name`` and a ``weight`` (risk points added when the
    check triggers) and implement :meth:`evaluate`.
    """

    #: Human-readable name shown in the scan results.
    name: str = "check"
    #: Risk points contributed when this check triggers.
    weight: int = 0

    @abstractmethod
    def evaluate(self, url: ParsedUrl) -> CheckOutcome:
        """Inspect the URL and return a :class:`CheckOutcome`."""
        raise NotImplementedError

    def _outcome(self, triggered: bool, reason: str) -> CheckOutcome:
        """Helper so subclasses don't repeat the CheckOutcome wiring."""
        return CheckOutcome(
            name=self.name,
            triggered=triggered,
            points=self.weight if triggered else 0,
            reason=reason,
        )
