"""
crawler.py — Playwright-based dark pattern crawler.

Navigates through a target site's:
  1. Homepage
  2. Signup / free-trial flow
  3. Cancellation flow
  4. Cookie consent banner

At each step, captures:
  - Screenshot (PNG, base64-encoded)
  - Full page text
  - Current URL

Returns a list of CrawlStep objects.
"""
from __future__ import annotations

import asyncio
import base64
import logging
import os
import re
import time
from pathlib import Path
from typing import AsyncIterator, Callable, Optional

from playwright.async_api import (
    Page,
    BrowserContext,
    async_playwright,
    TimeoutError as PwTimeout,
)

from models import CrawlStep

logger = logging.getLogger(__name__)

# Where screenshots are stored on disk (also kept as base64 in memory for API)
SCREENSHOT_DIR = Path(__file__).parent / "screenshots"
SCREENSHOT_DIR.mkdir(exist_ok=True)

# ─────────────────────────────── helpers ────────────────────────────────── #

async def _safe_screenshot(page: Page, name: str, task_id: str) -> tuple[Optional[str], Optional[str]]:
    """Take a screenshot, return (base64_string, file_path) or (None, None) on error."""
    try:
        path = SCREENSHOT_DIR / f"{task_id}_{name}_{int(time.time())}.png"
        await page.screenshot(path=str(path), full_page=False, timeout=10_000)
        data = path.read_bytes()
        b64 = base64.b64encode(data).decode()
        return b64, str(path)
    except Exception as exc:
        logger.warning("Screenshot failed for %s: %s", name, exc)
        return None, None


async def _get_text(page: Page) -> str:
    """Extract visible text from the page, truncated to 8 000 chars."""
    try:
        text = await page.evaluate(
            """() => {
                const walker = document.createTreeWalker(
                    document.body,
                    NodeFilter.SHOW_TEXT,
                    {
                        acceptNode(node) {
                            const parent = node.parentElement;
                            if (!parent) return NodeFilter.FILTER_REJECT;
                            const style = window.getComputedStyle(parent);
                            if (style.display === 'none' || style.visibility === 'hidden' || style.opacity === '0')
                                return NodeFilter.FILTER_REJECT;
                            return NodeFilter.FILTER_ACCEPT;
                        }
                    }
                );
                const chunks = [];
                let node;
                while ((node = walker.nextNode())) {
                    const t = node.textContent.trim();
                    if (t) chunks.push(t);
                }
                return chunks.join(' ');
            }"""
        )
        return (text or "")[:8000]
    except Exception as exc:
        logger.warning("Text extraction failed: %s", exc)
        return ""


# ───────────────────────── flow-specific navigators ─────────────────────── #

async def _navigate_homepage(
    page: Page,
    url: str,
    task_id: str,
    status_cb: Callable[[str], None],
) -> CrawlStep:
    status_cb("Navigating to homepage…")
    await page.goto(url, wait_until="domcontentloaded", timeout=30_000)
    await page.wait_for_timeout(2000)
    b64, path = await _safe_screenshot(page, "homepage", task_id)
    text = await _get_text(page)
    return CrawlStep(
        step_name="homepage",
        url=page.url,
        page_text=text,
        screenshot_b64=b64,
        screenshot_path=path,
    )


# Heuristic selectors for finding signup-related links/buttons
_SIGNUP_PATTERNS = [
    re.compile(r"\b(sign[\s-]?up|register|create.{0,10}account|get.{0,10}started|free.{0,10}trial|start.{0,10}free|join)\b", re.I),
]
_CANCEL_PATTERNS = [
    re.compile(r"\b(cancel|cancellation|unsubscribe|close.{0,6}account|delete.{0,6}account)\b", re.I),
]
_COOKIE_PATTERNS = [
    re.compile(r"\b(accept.{0,8}cookie|allow.{0,8}cookie|agree|i.accept|consent|got.it|ok)\b", re.I),
]


async def _click_matching(page: Page, patterns: list[re.Pattern], label: str) -> bool:
    """Try to find and click an element matching one of the regex patterns.  Returns True on success."""
    # Try buttons first, then anchors, then anything clickable
    for selector in ["button", "a", "[role='button']", "input[type='submit']"]:
        try:
            elements = await page.query_selector_all(selector)
            for el in elements:
                try:
                    text = (await el.inner_text()).strip()
                    for pat in patterns:
                        if pat.search(text):
                            await el.scroll_into_view_if_needed()
                            await el.click(timeout=5000)
                            logger.info("Clicked %s element: %r", label, text[:60])
                            return True
                except Exception:
                    continue
        except Exception:
            continue
    return False


async def _navigate_signup(
    page: Page,
    task_id: str,
    status_cb: Callable[[str], None],
) -> list[CrawlStep]:
    steps: list[CrawlStep] = []
    status_cb("Looking for signup / free-trial flow…")
    clicked = await _click_matching(page, _SIGNUP_PATTERNS, "signup")
    if clicked:
        await page.wait_for_timeout(2500)
        b64, path = await _safe_screenshot(page, "signup_flow", task_id)
        text = await _get_text(page)
        steps.append(CrawlStep(
            step_name="signup_flow",
            url=page.url,
            page_text=text,
            screenshot_b64=b64,
            screenshot_path=path,
        ))
        status_cb(f"Captured signup flow at {page.url}")

        # Look for pricing/plan selection pages (common dark pattern location)
        pricing_patterns = [re.compile(r"\b(pricing|plan|subscription|choose.{0,8}plan|pick.{0,8}plan)\b", re.I)]
        clicked2 = await _click_matching(page, pricing_patterns, "pricing")
        if clicked2:
            await page.wait_for_timeout(2000)
            b64, path = await _safe_screenshot(page, "pricing_flow", task_id)
            text = await _get_text(page)
            steps.append(CrawlStep(
                step_name="pricing_flow",
                url=page.url,
                page_text=text,
                screenshot_b64=b64,
                screenshot_path=path,
            ))
            status_cb(f"Captured pricing page at {page.url}")
    else:
        status_cb("Could not locate signup flow — skipping.")
    return steps


async def _navigate_cancellation(
    page: Page,
    task_id: str,
    status_cb: Callable[[str], None],
) -> list[CrawlStep]:
    steps: list[CrawlStep] = []
    status_cb("Looking for cancellation / account-close flow…")

    # Common paths for account settings / cancellation
    base = "/".join(page.url.split("/")[:3])
    candidate_paths = ["/account", "/settings", "/account/settings", "/profile", "/subscription", "/billing"]
    found = False
    for path in candidate_paths:
        try:
            resp = await page.goto(base + path, wait_until="domcontentloaded", timeout=10_000)
            if resp and resp.status < 400:
                await page.wait_for_timeout(1500)
                found = True
                b64, spath = await _safe_screenshot(page, "account_settings", task_id)
                text = await _get_text(page)
                steps.append(CrawlStep(
                    step_name="account_settings",
                    url=page.url,
                    page_text=text,
                    screenshot_b64=b64,
                    screenshot_path=spath,
                ))
                status_cb(f"Found account settings at {page.url}")
                break
        except PwTimeout:
            continue
        except Exception:
            continue

    # Now look for a cancel button/link on the current page
    clicked = await _click_matching(page, _CANCEL_PATTERNS, "cancel")
    if clicked:
        await page.wait_for_timeout(2500)
        b64, spath = await _safe_screenshot(page, "cancellation_flow", task_id)
        text = await _get_text(page)
        steps.append(CrawlStep(
            step_name="cancellation_flow",
            url=page.url,
            page_text=text,
            screenshot_b64=b64,
            screenshot_path=spath,
        ))
        status_cb(f"Captured cancellation flow at {page.url}")
    elif not found:
        status_cb("Could not locate cancellation flow — skipping.")

    return steps


async def _capture_cookie_banner(
    page: Page,
    url: str,
    task_id: str,
    status_cb: Callable[[str], None],
) -> list[CrawlStep]:
    """Reload the homepage (fresh context needed for the cookie banner) and capture it."""
    steps: list[CrawlStep] = []
    status_cb("Checking for cookie consent banner…")
    try:
        await page.goto(url, wait_until="domcontentloaded", timeout=20_000)
        await page.wait_for_timeout(2000)

        # Common cookie banner selectors
        cookie_selectors = [
            "[id*='cookie']",
            "[class*='cookie']",
            "[id*='consent']",
            "[class*='consent']",
            "[id*='gdpr']",
            "[class*='gdpr']",
            "[id*='privacy']",
            "[class*='banner']",
            "[role='dialog']",
        ]
        banner_found = False
        for sel in cookie_selectors:
            try:
                el = await page.wait_for_selector(sel, timeout=3000)
                if el and await el.is_visible():
                    banner_found = True
                    break
            except Exception:
                continue

        if banner_found:
            b64, spath = await _safe_screenshot(page, "cookie_banner", task_id)
            text = await _get_text(page)
            steps.append(CrawlStep(
                step_name="cookie_consent",
                url=page.url,
                page_text=text,
                screenshot_b64=b64,
                screenshot_path=spath,
            ))
            status_cb("Captured cookie consent banner.")

            # Also capture post-accept state
            clicked = await _click_matching(page, _COOKIE_PATTERNS, "accept-cookie")
            if clicked:
                await page.wait_for_timeout(1500)
                b64, spath = await _safe_screenshot(page, "post_cookie", task_id)
                text = await _get_text(page)
                steps.append(CrawlStep(
                    step_name="post_cookie_accept",
                    url=page.url,
                    page_text=text,
                    screenshot_b64=b64,
                    screenshot_path=spath,
                ))
        else:
            status_cb("No cookie banner detected.")
    except Exception as exc:
        status_cb(f"Cookie banner check failed: {exc}")
    return steps


# ─────────────────────────────── public API ─────────────────────────────── #

async def crawl(
    url: str,
    task_id: str,
    status_cb: Callable[[str], None] = lambda _: None,
) -> list[CrawlStep]:
    """
    Run the full crawl pipeline for the given URL.
    `status_cb` is called with human-readable progress strings.
    Returns a list of CrawlStep objects.
    """
    # Normalise URL
    if not url.startswith(("http://", "https://")):
        url = "https://" + url

    steps: list[CrawlStep] = []

    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            headless=True,
            args=[
                "--no-sandbox",
                "--disable-setuid-sandbox",
                "--disable-dev-shm-usage",
                "--disable-gpu",
                "--disable-web-security",
            ],
        )
        ctx: BrowserContext = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0.0.0 Safari/537.36"
            ),
            locale="en-US",
            timezone_id="America/New_York",
            extra_http_headers={"Accept-Language": "en-US,en;q=0.9"},
        )

        page = await ctx.new_page()

        # Block heavy media to speed up crawl
        await page.route(
            "**/*.{mp4,webm,ogv,mp3,wav,flac}",
            lambda route: route.abort(),
        )

        try:
            # Step 1: Homepage
            homepage_step = await _navigate_homepage(page, url, task_id, status_cb)
            steps.append(homepage_step)

            # Step 2: Signup flow
            signup_steps = await _navigate_signup(page, task_id, status_cb)
            steps.extend(signup_steps)

            # Step 3: Cancellation flow (navigate back to home first)
            await page.goto(url, wait_until="domcontentloaded", timeout=20_000)
            await page.wait_for_timeout(1000)
            cancel_steps = await _navigate_cancellation(page, task_id, status_cb)
            steps.extend(cancel_steps)

            # Step 4: Cookie consent (fresh navigation)
            cookie_steps = await _capture_cookie_banner(page, url, task_id, status_cb)
            steps.extend(cookie_steps)

            status_cb(f"Crawl complete. Captured {len(steps)} step(s).")

        except Exception as exc:
            logger.exception("Crawler error for %s: %s", url, exc)
            status_cb(f"Crawler error: {exc}")
            # Still return whatever we captured
        finally:
            await ctx.close()
            await browser.close()

    return steps
