"""
precedents.py — Perplexity enforcement case search.

For each unique dark pattern found, uses sonar-reasoning-pro with web search
to find 2 real FTC or EU enforcement cases.

Returns a list of PatternPrecedents objects.
"""
from __future__ import annotations

import json
import logging
from typing import Callable

import httpx

from models import EnforcementCase, Finding, PatternPrecedents, PatternType

logger = logging.getLogger(__name__)

PERPLEXITY_BASE = "https://api.perplexity.ai"

# ─────────────────────────────── prompts ────────────────────────────────── #

SYSTEM_PROMPT = """You are a legal research assistant specialising in consumer protection enforcement actions 
by the FTC (Federal Trade Commission) and EU regulatory bodies (European Commission, national Data Protection 
Authorities, consumer protection agencies).

Your job is to find REAL, VERIFIABLE enforcement cases — not hypothetical examples. Every case you cite must 
be a real action that actually occurred, with real case names, companies, years, and outcomes."""

USER_TEMPLATE = """Find 2 real enforcement actions by the FTC or EU authorities against companies for using 
the dark pattern known as "{pattern_label}".

Definition: {pattern_description}

For each case return a JSON object with EXACTLY these fields:
{{
  "case_name": "<Official case name or docket number, e.g. 'FTC v. Amazon.com, Inc.' or 'Case AT.40462'>",
  "company": "<Company or defendant name>",
  "year": <Year of action as integer, e.g. 2023>,
  "outcome": "<What happened: settlement amount, injunction, consent order, fine, etc. — 1-2 sentences>",
  "source_url": "<Direct URL to the FTC press release, court filing, or EU decision — must be a real URL>"
}}

Return ONLY a JSON array of 2 objects. Do not include any text outside the JSON array.
Use web search to verify each case is real before including it."""


PATTERN_DESCRIPTIONS = {
    PatternType.ROACH_MOTEL: "Easy to subscribe or sign up, deliberately difficult to cancel, unsubscribe, or close account.",
    PatternType.CONFIRMSHAMING: "Guilt-tripping or shaming language used on decline/opt-out buttons to manipulate users.",
    PatternType.HIDDEN_COSTS: "Extra fees, taxes, or charges added late in checkout without earlier disclosure.",
    PatternType.TRICK_QUESTIONS: "Confusing double-negatives, pre-ticked boxes, or misleading opt-in/opt-out checkboxes.",
    PatternType.DISGUISED_ADS: "Paid content styled to look like organic results, editorial content, or user reviews.",
    PatternType.FORCED_CONTINUITY: "Free trial or introductory offer transitions to paid subscription without clear notice or easy cancellation.",
    PatternType.MISDIRECTION: "Visual design, copy, or UI layout draws attention away from important information to manipulate choices.",
}

PATTERN_LABELS = {
    PatternType.ROACH_MOTEL: "Roach Motel (difficult cancellation)",
    PatternType.CONFIRMSHAMING: "Confirmshaming",
    PatternType.HIDDEN_COSTS: "Hidden Costs / Drip Pricing",
    PatternType.TRICK_QUESTIONS: "Trick Questions / Deceptive Consent",
    PatternType.DISGUISED_ADS: "Disguised Advertising",
    PatternType.FORCED_CONTINUITY: "Forced Continuity / Negative Option Marketing",
    PatternType.MISDIRECTION: "Misdirection / Visual Manipulation",
}


# ──────────────────────────── Perplexity client ─────────────────────────── #

async def _call_perplexity(messages: list[dict], api_key: str) -> str:
    payload = {
        "model": "sonar-reasoning-pro",
        "messages": messages,
        "max_tokens": 2048,
        "temperature": 0.1,
        "web_search_options": {"search_context_size": "high"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    async with httpx.AsyncClient(timeout=90.0) as client:
        resp = await client.post(
            f"{PERPLEXITY_BASE}/chat/completions",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def _parse_cases(raw: str) -> list[EnforcementCase]:
    """Extract enforcement case JSON from the model response."""
    text = raw.strip()
    if "```" in text:
        parts = text.split("```")
        for part in parts:
            stripped = part.strip()
            if stripped.startswith("[") or stripped.startswith("json\n["):
                text = stripped.lstrip("json").strip()
                break

    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        logger.warning("No JSON array in precedents response: %s", text[:200])
        return []

    try:
        items = json.loads(text[start : end + 1])
    except json.JSONDecodeError as exc:
        logger.warning("JSON parse error in precedents: %s", exc)
        return []

    cases: list[EnforcementCase] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            case = EnforcementCase(
                case_name=item.get("case_name", "Unknown Case"),
                company=item.get("company", "Unknown Company"),
                year=int(item.get("year", 2020)),
                outcome=item.get("outcome", ""),
                source_url=item.get("source_url", ""),
            )
            cases.append(case)
        except Exception as exc:
            logger.warning("Could not parse enforcement case %s: %s", item, exc)
    return cases


# ──────────────────────────── public API ────────────────────────────────── #

async def fetch_precedents(
    findings: list[Finding],
    api_key: str,
    status_cb: Callable[[str], None] = lambda _: None,
) -> list[PatternPrecedents]:
    """
    For each unique pattern type in `findings`, fetch enforcement precedents.
    """
    unique_patterns = list({f.pattern_type for f in findings})
    results: list[PatternPrecedents] = []

    for pattern in unique_patterns:
        label = PATTERN_LABELS.get(pattern, pattern.value)
        description = PATTERN_DESCRIPTIONS.get(pattern, "")
        status_cb(f"Searching enforcement cases for: {label}…")

        prompt = USER_TEMPLATE.format(
            pattern_label=label,
            pattern_description=description,
        )
        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        try:
            raw = await _call_perplexity(messages, api_key)
            cases = _parse_cases(raw)
            status_cb(f"Found {len(cases)} precedent(s) for {label}.")
            results.append(PatternPrecedents(pattern_type=pattern, cases=cases))
        except Exception as exc:
            logger.exception("Precedent search failed for %s: %s", pattern, exc)
            status_cb(f"Precedent search failed for {label}: {exc}")
            results.append(PatternPrecedents(pattern_type=pattern, cases=[]))

    return results
