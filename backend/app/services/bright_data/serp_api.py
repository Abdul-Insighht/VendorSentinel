"""
VendorSentinel — Signal 1: News & Public Media Monitoring
Uses Bright Data SERP API to search for vendor-related security incidents,
data breaches, regulatory fines, and negative press coverage.
"""

import httpx
import json
import urllib.parse
from typing import Any

from app.config import settings

# ── Constants ────────────────────────────────────────────────────
SERP_API_URL = "https://api.brightdata.com/request"
PROXY_HOST = "brd.superproxy.io"
PROXY_PORT = 33335

SEARCH_TEMPLATE = (
    '"{vendor_name}" data breach OR cyberattack OR security incident '
    "OR data leak OR ransomware OR regulatory fine OR GDPR violation"
)

# Keywords that bump severity
CRITICAL_KEYWORDS = ["data breach", "ransomware", "cyberattack", "credentials leaked"]
HIGH_KEYWORDS = ["security incident", "data leak", "GDPR violation", "regulatory fine", "class action"]
MEDIUM_KEYWORDS = ["security vulnerability", "patch", "CVE", "exploit"]


# ── Helpers ──────────────────────────────────────────────────────

def _classify_severity(text: str) -> str:
    """Classify a finding's severity based on keyword presence in title/snippet."""
    lower = text.lower()
    for kw in CRITICAL_KEYWORDS:
        if kw in lower:
            return "critical"
    for kw in HIGH_KEYWORDS:
        if kw in lower:
            return "high"
    for kw in MEDIUM_KEYWORDS:
        if kw in lower:
            return "medium"
    return "low"


def _parse_organic_results(raw: dict | list | str) -> list[dict[str, Any]]:
    """
    Parse Google SERP JSON (Bright Data format) into normalised findings.
    Bright Data may return results under 'organic' or 'results' keys,
    or as a raw list.
    """
    findings: list[dict[str, Any]] = []

    # Normalise to list of result dicts
    items: list[dict] = []
    if isinstance(raw, dict):
        items = raw.get("organic", raw.get("results", []))
    elif isinstance(raw, list):
        items = raw

    for item in items:
        title = item.get("title", item.get("name", ""))
        snippet = item.get("description", item.get("snippet", ""))
        link = item.get("link", item.get("url", ""))

        if not title:
            continue

        combined_text = f"{title} {snippet}"
        severity = _classify_severity(combined_text)

        findings.append({
            "title": title,
            "description": snippet,
            "source_url": link,
            "severity": severity,
            "raw_data": item,
        })

    return findings


# ── Primary: Bright Data SERP API (POST /request) ───────────────

async def _search_via_api(query: str) -> list[dict[str, Any]]:
    """
    Send a search request through the Bright Data SERP API endpoint.
    Returns parsed findings or raises on failure.
    """
    encoded_query = urllib.parse.quote_plus(query)
    google_url = f"https://www.google.com/search?q={encoded_query}&num=10"

    headers = {
        "Authorization": f"Bearer {settings.bright_data_api_token}",
        "Content-Type": "application/json",
    }
    payload = {
        "zone": "serp",
        "url": google_url,
        "format": "json",
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"  📡 SERP API POST → {SERP_API_URL}")
        resp = await client.post(SERP_API_URL, headers=headers, json=payload)
        resp.raise_for_status()

        data = resp.json()
        return _parse_organic_results(data)


# ── Fallback: SERP Proxy ────────────────────────────────────────

async def _search_via_proxy(query: str) -> list[dict[str, Any]]:
    """
    Fallback: route a regular Google search through the Bright Data
    SERP proxy zone and scrape results from the HTML response.
    """
    username = settings.bright_data_serp_username
    password = settings.bright_data_serp_password
    proxy_url = f"http://{username}:{password}@{PROXY_HOST}:{PROXY_PORT}"

    encoded_query = urllib.parse.quote_plus(query)
    google_url = f"https://www.google.com/search?q={encoded_query}&num=10"

    async with httpx.AsyncClient(
        proxies={"http://": proxy_url, "https://": proxy_url},
        timeout=60.0,
        verify=False,
    ) as client:
        print(f"  📡 SERP Proxy GET → {google_url}")
        resp = await client.get(google_url)
        resp.raise_for_status()

        # Bright Data SERP zone may return JSON directly or raw HTML
        content_type = resp.headers.get("content-type", "")
        if "json" in content_type:
            return _parse_organic_results(resp.json())

        # Attempt basic HTML parsing as a last resort
        return _parse_html_results(resp.text)


def _parse_html_results(html: str) -> list[dict[str, Any]]:
    """
    Minimal HTML parser for Google results when JSON is unavailable.
    Extracts <h3> titles and surrounding links.
    """
    findings: list[dict[str, Any]] = []
    # Very lightweight: look for result blocks
    import re

    # Google wraps titles in <h3> tags
    title_pattern = re.compile(r"<h3[^>]*>(.*?)</h3>", re.DOTALL)
    link_pattern = re.compile(r'href="(/url\?q=|)(https?://[^"&]+)', re.DOTALL)

    titles = title_pattern.findall(html)
    links = link_pattern.findall(html)

    # Pair up titles with links (best effort)
    urls = [match[1] for match in links if "google.com" not in match[1]]

    for i, raw_title in enumerate(titles[:10]):
        # Strip HTML tags from title
        clean_title = re.sub(r"<[^>]+>", "", raw_title).strip()
        if not clean_title:
            continue

        url = urls[i] if i < len(urls) else ""
        severity = _classify_severity(clean_title)

        findings.append({
            "title": clean_title,
            "description": "Found via Google SERP proxy search",
            "source_url": url,
            "severity": severity,
            "raw_data": {"html_extracted": True},
        })

    return findings


# ── Public entry point ───────────────────────────────────────────

async def search_vendor_news(
    vendor_name: str,
    vendor_domain: str,
) -> list[dict[str, Any]]:
    """
    Search for public security-related news about a vendor.

    Args:
        vendor_name: Human-readable company name (e.g. "Acme Corp").
        vendor_domain: Primary domain (e.g. "acme.com").

    Returns:
        List of finding dicts, each with keys:
            title, description, source_url, severity, raw_data
    """
    query = SEARCH_TEMPLATE.format(vendor_name=vendor_name)
    print(f"🔍 [SERP] Searching news for '{vendor_name}' ({vendor_domain})")

    # Attempt 1 — SERP API (POST)
    try:
        findings = await _search_via_api(query)
        if findings:
            print(f"  ✅ SERP API returned {len(findings)} results")
            return findings
        print("  ⚠️ SERP API returned 0 results, falling back to proxy")
    except Exception as exc:
        print(f"  ⚠️ SERP API failed ({exc}), falling back to proxy")

    # Attempt 2 — SERP Proxy
    try:
        findings = await _search_via_proxy(query)
        print(f"  ✅ SERP Proxy returned {len(findings)} results")
        return findings
    except Exception as exc:
        print(f"  ❌ SERP Proxy also failed ({exc})")

    # Both failed — return empty
    return []
