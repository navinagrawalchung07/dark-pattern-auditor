"""
classify.py — Perplexity-powered dark pattern classifier.

For each crawl step, uses sonar-reasoning-pro with a fetch_url tool to pull
live statute text from ftc.gov and ec.europa.eu before classifying.

Returns a list of Finding objects.
"""
from __future__ import annotations

import json
import logging
import os
from typing import Callable

import httpx

from models import CrawlStep, Finding, PatternType, Severity

logger = logging.getLogger(__name__)

PERPLEXITY_BASE = "https://api.perplexity.ai"

# ─────────────────────────── live statute sources ───────────────────────── #

STATUTE_SOURCES = [
    # FTC Act § 5 — Unfair or Deceptive Acts or Practices
    "https://www.ftc.gov/legal-library/browse/statutes/federal-trade-commission-act",
    # FTC Enforcement Policy Statement on Deceptively Formatted Advertising
    "https://www.ftc.gov/system/files/documents/public_statements/896923/151222deceptiveenforcement.pdf",
    # FTC Dark Patterns Report 2022
    "https://www.ftc.gov/reports/dark-patterns-report",
    # EU UCPD (Unfair Commercial Practices Directive) — EUR-Lex
    "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32005L0029",
    # EU Digital Services Act consumer protection provisions
    "https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32022R2065",
]

# ─────────────────────────────── prompt ─────────────────────────────────── #

SYSTEM_PROMPT = """You are a senior consumer-protection attorney specialising in digital dark patterns. 
You identify deceptive UI patterns on websites and classify them against real, current law.

Dark pattern types you detect:
- roach_motel: Easy to sign up, deliberately hard to cancel or unsubscribe
- confirmshaming: Decline button uses guilt-tripping language ("No thanks, I hate saving money")
- hidden_costs: Fees, taxes, or charges added late in checkout without earlier disclosure
- trick_questions: Pre-ticked boxes, confusing double-negatives to obtain consent
- disguised_ads: Paid content or ads styled to look like organic results or editorial
- forced_continuity: Free trial transitions to paid without clear warning or easy cancellation
- misdirection: Visual design or copy draws attention away from important information

Severity:
- low: Minor annoyance, unlikely regulatory action
- medium: Meaningful deception, potential enforcement interest
- high: Clear statutory violation, strong enforcement precedent exists

You MUST use the fetch_url tool to retrieve live statute text before classifying — do not rely on training data for legal citations."""

USER_TEMPLATE = """I need you to analyse the following web page content captured during an audit of {url}.

Step name: {step_name}
URL captured: {step_url}

Page text (truncated to 8 000 chars):
---
{page_text}
---

Instructions:
1. Use fetch_url to retrieve the current text from at least TWO of these URLs before classifying:
   - https://www.ftc.gov/reports/dark-patterns-report
   - https://www.ftc.gov/legal-library/browse/statutes/federal-trade-commission-act
   - https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32005L0029
   - https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32022R2065

2. Identify ALL dark patterns present in the page text above.

3. For each pattern found, return a JSON object with EXACTLY these fields:
{{
  "pattern_type": "<one of: roach_motel|confirmshaming|hidden_costs|trick_questions|disguised_ads|forced_continuity|misdirection>",
  "severity": "<low|medium|high>",
  "description": "<2-3 sentence explanation of why this is a dark pattern>",
  "quoted_ui_text": "<exact text from the page that constitutes the dark pattern, verbatim>",
  "statute_name": "<full name of the statute violated, e.g. FTC Act § 5(a), EU UCPD Annex I item 11>",
  "statute_excerpt": "<exact quoted passage from the statute (fetched via fetch_url)>",
  "statutory_url": "<URL you fetched the statute from>"
}}

Return your findings as a JSON array. If no dark patterns are found, return an empty array [].
Do not include any text outside the JSON array in your final answer."""


# ────────────────────────── Perplexity client ───────────────────────────── #

async def _call_perplexity(messages: list[dict], api_key: str) -> str:
    """Call the Perplexity chat completions endpoint with sonar-reasoning-pro."""
    payload = {
        "model": "sonar-reasoning-pro",
        "messages": messages,
        "max_tokens": 4096,
        "temperature": 0.1,
        "web_search_options": {"search_context_size": "high"},
    }
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "Accept": "application/json",
    }
    async with httpx.AsyncClient(timeout=120.0) as client:
        resp = await client.post(
            f"{PERPLEXITY_BASE}/chat/completions",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()
        return data["choices"][0]["message"]["content"]


def _parse_findings(raw: str, step: CrawlStep) -> list[Finding]:
    """Extract the JSON array from the model response and parse into Finding objects."""
    # Strip markdown code fences if present
    text = raw.strip()
    if "```" in text:
        # Extract content between first ``` and last ```
        parts = text.split("```")
        # Find the part that looks like JSON
        for part in parts:
            stripped = part.strip()
            if stripped.startswith("[") or stripped.startswith("json\n["):
                text = stripped.lstrip("json").strip()
                break

    # Find the JSON array boundaries
    start = text.find("[")
    end = text.rfind("]")
    if start == -1 or end == -1:
        logger.warning("No JSON array found in response: %s", text[:200])
        return []

    json_str = text[start : end + 1]
    try:
        items = json.loads(json_str)
    except json.JSONDecodeError as exc:
        logger.warning("JSON parse error: %s — raw: %s", exc, json_str[:500])
        return []

    findings: list[Finding] = []
    for item in items:
        if not isinstance(item, dict):
            continue
        try:
            pattern_type = PatternType(item.get("pattern_type", ""))
            severity = Severity(item.get("severity", "low"))
            finding = Finding(
                pattern_type=pattern_type,
                severity=severity,
                description=item.get("description", ""),
                quoted_ui_text=item.get("quoted_ui_text", ""),
                statute_name=item.get("statute_name", ""),
                statute_excerpt=item.get("statute_excerpt", ""),
                statutory_url=item.get("statutory_url", ""),
                step_name=step.step_name,
                screenshot_b64=step.screenshot_b64,
            )
            findings.append(finding)
        except Exception as exc:
            logger.warning("Could not parse finding %s: %s", item, exc)
            continue

    return findings


# ──────────────────────────── public API ────────────────────────────────── #

async def classify_steps(
    steps: list[CrawlStep],
    target_url: str,
    api_key: str,
    status_cb: Callable[[str], None] = lambda _: None,
) -> list[Finding]:
    """
    Classify all crawl steps and return deduplicated findings.
    """
    all_findings: list[Finding] = []
    seen: set[str] = set()  # dedup key: pattern_type + quoted_ui_text[:60]

    for step in steps:
        if not step.page_text.strip():
            continue

        status_cb(f"Classifying step: {step.step_name}…")
        prompt = USER_TEMPLATE.format(
            url=target_url,
            step_name=step.step_name,
            step_url=step.url,
            page_text=step.page_text,
        )

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt},
        ]

        try:
            raw = await _call_perplexity(messages, api_key)
            step_findings = _parse_findings(raw, step)
            status_cb(f"Found {len(step_findings)} pattern(s) in {step.step_name}.")

            for f in step_findings:
                dedup_key = f"{f.pattern_type}|{f.quoted_ui_text[:60]}"
                if dedup_key not in seen:
                    seen.add(dedup_key)
                    all_findings.append(f)

        except Exception as exc:
            logger.exception("Classification error for step %s: %s", step.step_name, exc)
            status_cb(f"Classification failed for {step.step_name}: {exc}")

    return all_findings
