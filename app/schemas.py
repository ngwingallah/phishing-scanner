"""Pydantic schemas for API requests and responses."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class ScanRequest(BaseModel):
    url: str = Field(
        ...,
        examples=["http://paypal-verify.secure-update.xyz@192.168.0.10/login"],
        description="The URL to analyze for phishing risk.",
    )


class FlagOut(BaseModel):
    name: str
    reason: str


class ScanOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    url: str
    score: int
    verdict: str
    flags: list[FlagOut]
    created_at: datetime
