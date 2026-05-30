"""
VendorSentinel — Signal 4: Vendor Health & Reputation Monitoring
Uses Bright Data Scraping Browser (via Playwright CDP) to inspect
vendor websites and review sites for negative reputation signals.

Gracefully degrades to Web Unlocker when Playwright is not installed.
"""

import re
from typing import Any

from app.config import settings

# ── Constants ────────────────────────────────────────────────────
PROXY_HOST = "brd.superproxy.io"
PROXY_PORT = 33335

# Negative-signal keywords
NEGATIVE_KEYWORDS: list[str] = [
    "data breach", "security incident", "layoff", "restructuring",
    "leadership change", "ceo departure", "cto departure", "ciso departure",
    "regulatory action", "lawsuit", "settlement", "bankruptcy",
    "downsizing", "workforce reduction", "acquisition", "merger",
    "outage", "service disruption", "vulnerability",
]

POSITIVE_KEYWORDS: list[str] = [
    "soc 2", "iso 27001", "security certification", "bug bounty",
    "responsible disclosure", "security blog", "penetration test",
    "compliance", "zero trust",
]


# ── Helpers ──────────────────────────────────────────────────────

def _analyse_content(text: str, vendor_name: str, source: str) -> list[dict[str, Any]]:
    """
    Scan *text* for negative and positive reputation signals.
    Returns structured findings.
    """
    findings: list[dict[str, Any]] = []
    lower = text.lower()

    # Check for negative signals
    matched_negatives: list[str] = []
    for kw in NEGATIVE_KEYWORDS:
        if kw in lower:
            matched_negatives.append(kw)

    if matched_negatives:
        # Determine severity based on keyword type
        has_critical = any(
            k in matched_negatives
            for k in ["data breach", "security incident", "bankruptcy"]
        )
        severity = "high" if has_critical else "medium"

        findings.append({
            "title": f"Negative reputation signals found for {vendor_name}",
            "description": (
                f"Analysis of {source} detected the following concerning keywords: "
                f"{', '.join(matched_negatives)}. These may indicate operational, "
                f"financial, or security issues at {vendor_name}."
            ),
            "source_url": source,
            "severity": severity,
            "raw_data": {
                "source": source,
                "negative_keywords": matched_negatives,
                "analysis_method": "keyword_scan",
            },
        })

    # Check for positive signals (reduce risk perception)
    matched_positives: list[str] = []
    for kw in POSITIVE_KEYWORDS:
        if kw in lower:
            matched_positives.append(kw)

    if matched_positives:
        findings.append({
            "title": f"Positive security posture indicators at {vendor_name}",
            "description": (
                f"Analysis of {source} found positive security indicators: "
                f"{', '.join(matched_positives)}. These suggest proactive security "
                f"investment."
            ),
            "source_url": source,
            "severity": "info",
            "raw_data": {
                "source": source,
                "positive_keywords": matched_positives,
                "analysis_method": "keyword_scan",
            },
        })

    return findings


# ── Approach 1: Playwright / Scraping Browser ────────────────────

async def _check_via_scraping_browser(
    vendor_domain: str,
    vendor_name: str,
) -> list[dict[str, Any]]:
    """
    Connect to Bright Data's Scraping Browser via Playwright CDP.
    Visits the vendor website and extracts page content for analysis.
    """
    from playwright.async_api import async_playwright

    browser_ws = f"wss://{settings.bright_data_browser_auth}@{settings.bright_data_browser_host}"
    findings: list[dict[str, Any]] = []

    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(browser_ws)
        try:
            page = await browser.new_page()

            # ── Visit vendor website ──
            vendor_url = f"https://{vendor_domain}"
            print(f"  🌐 Scraping Browser → {vendor_url}")
            try:
                await page.goto(vendor_url, wait_until="domcontentloaded", timeout=30000)
                content = await page.content()
                # Strip HTML tags for text analysis
                text = re.sub(r"<[^>]+>", " ", content)
                text = re.sub(r"\s+", " ", text)
                findings.extend(_analyse_content(text, vendor_name, vendor_url))
            except Exception as exc:
                print(f"  ⚠️ Could not load vendor site: {exc}")

            # ── Try vendor's security/blog page ──
            for path in ["/security", "/blog", "/trust", "/compliance"]:
                sec_url = f"https://{vendor_domain}{path}"
                try:
                    await page.goto(sec_url, wait_until="domcontentloaded", timeout=15000)
                    content = await page.content()
                    text = re.sub(r"<[^>]+>", " ", content)
                    text = re.sub(r"\s+", " ", text)
                    findings.extend(_analyse_content(text, vendor_name, sec_url))
                except Exception:
                    pass  # Page may not exist — that's fine

        finally:
            await browser.close()

    return findings


# ── Approach 2: Web Unlocker fallback ────────────────────────────

async def _check_via_web_unlocker(
    vendor_domain: str,
    vendor_name: str,
) -> list[dict[str, Any]]:
    """
    Fallback when Playwright is unavailable: fetch the vendor website
    through the Bright Data Web Unlocker proxy using httpx.
    """
    import httpx

    proxy_url = (
        f"http://{settings.bright_data_unlocker_username}"
        f":{settings.bright_data_unlocker_password}"
        f"@{PROXY_HOST}:{PROXY_PORT}"
    )
    findings: list[dict[str, Any]] = []

    urls_to_check = [
        f"https://{vendor_domain}",
        f"https://{vendor_domain}/security",
        f"https://{vendor_domain}/blog",
        f"https://{vendor_domain}/trust",
    ]

    async with httpx.AsyncClient(
        proxies={"http://": proxy_url, "https://": proxy_url},
        timeout=45.0,
        verify=False,
        follow_redirects=True,
    ) as client:
        for url in urls_to_check:
            try:
                print(f"  📡 Web Unlocker GET → {url}")
                resp = await client.get(url)

                if resp.status_code >= 400:
                    continue

                # Strip HTML for analysis
                text = re.sub(r"<[^>]+>", " ", resp.text)
                text = re.sub(r"\s+", " ", text)
                findings.extend(_analyse_content(text, vendor_name, url))
            except Exception as exc:
                print(f"  ⚠️ Could not fetch {url}: {exc}")

    return findings


# ── Public entry point ───────────────────────────────────────────

async def check_vendor_health(
    vendor_name: str,
    vendor_domain: str,
) -> list[dict[str, Any]]:
    """
    Analyse a vendor's online presence for health and reputation signals.

    Attempts Playwright-based Scraping Browser first, then falls back to
    Web Unlocker HTTP requests if Playwright is not installed.

    Args:
        vendor_name: Human-readable company name.
        vendor_domain: Primary domain (e.g. "acme.com").

    Returns:
        List of finding dicts with keys:
            title, description, source_url, severity, raw_data
    """
    print(f"🔍 [Scraping Browser] Checking health for '{vendor_name}' ({vendor_domain})")

    # Attempt 1 — Playwright / Scraping Browser
    try:
        findings = await _check_via_scraping_browser(vendor_domain, vendor_name)
        if findings is not None:
            print(f"  ✅ Scraping Browser analysis complete — {len(findings)} findings")
            return findings
    except ImportError:
        print("  ⚠️ Playwright not installed, falling back to Web Unlocker")
    except Exception as exc:
        print(f"  ⚠️ Scraping Browser failed ({exc}), falling back to Web Unlocker")

    # Attempt 2 — Web Unlocker fallback
    try:
        findings = await _check_via_web_unlocker(vendor_domain, vendor_name)
        print(f"  ✅ Web Unlocker fallback complete — {len(findings)} findings")
        return findings
    except Exception as exc:
        print(f"  ❌ Web Unlocker fallback also failed ({exc})")

    return []
