"""
Shared Pydantic data models for the Dark Pattern Auditor.
"""
from __future__ import annotations

from enum import Enum
from typing import Optional
import base64
from pydantic import BaseModel, HttpUrl


class Severity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class PatternType(str, Enum):
    ROACH_MOTEL = "roach_motel"
    CONFIRMSHAMING = "confirmshaming"
    HIDDEN_COSTS = "hidden_costs"
    TRICK_QUESTIONS = "trick_questions"
    DISGUISED_ADS = "disguised_ads"
    FORCED_CONTINUITY = "forced_continuity"
    MISDIRECTION = "misdirection"


class CrawlStep(BaseModel):
    """A single step captured by the Playwright crawler."""
    step_name: str          # e.g. "homepage", "signup_flow", "cancellation_flow", "cookie_consent"
    url: str
    page_text: str
    screenshot_b64: Optional[str] = None   # base64-encoded PNG
    screenshot_path: Optional[str] = None  # local path (not included in API response)


class Finding(BaseModel):
    """A classified dark pattern finding."""
    pattern_type: PatternType
    severity: Severity
    description: str
    quoted_ui_text: str
    statute_name: str
    statute_excerpt: str
    statutory_url: str
    step_name: str
    screenshot_b64: Optional[str] = None


class EnforcementCase(BaseModel):
    """A real FTC or EU enforcement precedent."""
    case_name: str
    company: str
    year: int
    outcome: str
    source_url: str


class PatternPrecedents(BaseModel):
    pattern_type: PatternType
    cases: list[EnforcementCase]


class AuditRequest(BaseModel):
    url: str


class AuditResult(BaseModel):
    task_id: str
    target_url: str
    findings: list[Finding] = []
    precedents: list[PatternPrecedents] = []
    status: str = "pending"   # pending | running | complete | error
    error: Optional[str] = None
