"""
VendorSentinel — Signal 2: Credential Leak Detection
Uses Bright Data Web Unlocker to search for exposed credentials,
API keys, and secrets related to a vendor domain on public code
repositories and paste sites.
"""

import httpx
import re
from typing import Any

from app.config import settings

# ── Constants ────────────────────────────────────────────────────
PROXY_HOST = "brd.superproxy.io"
PROXY_PORT = 33335

# Patterns that indicate credential exposure
CREDENTIAL_PATTERNS: list[re.Pattern] = [
    re.compile(r"password\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"api[_-]?key\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"secret\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"token\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"authorization\s*:\s*bearer\s+\S+", re.IGNORECASE),
    re.compile(r"-----BEGIN\s+(RSA\s+)?PRIVATE\s+KEY-----", re.IGNORECASE),
    re.compile(r"aws_access_key_id\s*[:=]\s*\S+", re.IGNORECASE),
    re.compile(r"aws_secret_access_key\s*[:=]\s*\S+", re.IGNORECASE),
]


# ── Helper ───────────────────────────────────────────────────────

def _build_proxy_url() -> str:
    """Build the Web Unlocker proxy URL from settings."""
    return (
        f"http://{settings.bright_data_unlocker_username}"
        f":{settings.bright_data_unlocker_password}"
        f"@{PROXY_HOST}:{PROXY_PORT}"
    )


def _detect_credential_patterns(text: str) -> list[str]:
    """Return a list of matched credential-type strings found in *text*."""
    matches: list[str] = []
    for pattern in CREDENTIAL_PATTERNS:
        found = pattern.findall(text)
        matches.extend(found[:3])  # cap per-pattern to avoid noise
    return matches


def _classify_finding(matched_patterns: list[str]) -> str:
    """
    Any credential leak is inherently critical because it represents
    direct exposure of authentication material.
    """
    if matched_patterns:
        return "critical"
    return "medium"


# ── Fetcher (through Web Unlocker) ───────────────────────────────

async def _fetch_via_unlocker(url: str) -> str:
    """Fetch *url* through the Bright Data Web Unlocker proxy."""
    proxy = _build_proxy_url()

    async with httpx.AsyncClient(
        proxies={"http://": proxy, "https://": proxy},
        timeout=60.0,
        verify=False,
        follow_redirects=True,
    ) as client:
        print(f"  📡 Web Unlocker GET → {url}")
        resp = await client.get(url)
        resp.raise_for_status()
        return resp.text


# ── Search: GitHub Code Search ───────────────────────────────────

async def _search_github(vendor_domain: str) -> list[dict[str, Any]]:
    """
    Search GitHub code search for leaked credentials mentioning the
    vendor's domain.  We route through the Web Unlocker to avoid
    rate-limit blocks.
    """
    findings: list[dict[str, Any]] = []
    import urllib.parse

    query = f'"{vendor_domain}" password OR api_key OR secret OR token'
    encoded = urllib.parse.quote_plus(query)
    github_url = f"https://github.com/search?q={encoded}&type=code"

    try:
        html = await _fetch_via_unlocker(github_url)

        # Quick heuristic: count code-result snippets
        # GitHub wraps each result in a <div data-testid="results-list"> or
        # class="code-list-item" container.
        result_count = html.lower().count("code-list-item") or html.lower().count("search-result")

        if result_count > 0 or "password" in html.lower() or "api_key" in html.lower():
            # Look for credential patterns in the returned HTML
            matched = _detect_credential_patterns(html)
            severity = _classify_finding(matched)

            findings.append({
                "title": f"Potential credential exposure on GitHub for {vendor_domain}",
                "description": (
                    f"GitHub code search returned results matching credential keywords "
                    f"for domain '{vendor_domain}'. "
                    f"Matched patterns: {matched[:5] if matched else 'keyword presence detected'}."
                ),
                "source_url": github_url,
                "severity": severity,
                "raw_data": {
                    "source": "github_code_search",
                    "matched_patterns": matched[:10],
                    "result_count_estimate": max(result_count, 1),
                },
            })
        else:
            print(f"  ℹ️ No credential-related results on GitHub for {vendor_domain}")
    except Exception as exc:
        print(f"  ⚠️ GitHub search failed: {exc}")

    return findings


# ── Search: Pastebin via Google ──────────────────────────────────

async def _search_pastebin(vendor_domain: str) -> list[dict[str, Any]]:
    """
    Search Google for pastebin entries containing the vendor domain
    and credential-related keywords, routed through Web Unlocker.
    """
    findings: list[dict[str, Any]] = []
    import urllib.parse

    query = f'site:pastebin.com "{vendor_domain}" password OR credentials'
    encoded = urllib.parse.quote_plus(query)
    google_url = f"https://www.google.com/search?q={encoded}&num=10"

    try:
        html = await _fetch_via_unlocker(google_url)

        # Extract result titles (quick regex)
        title_re = re.compile(r"<h3[^>]*>(.*?)</h3>", re.DOTALL)
        strip_tags = re.compile(r"<[^>]+>")
        titles = [strip_tags.sub("", t).strip() for t in title_re.findall(html)]

        for title in titles[:5]:
            if not title:
                continue
            matched = _detect_credential_patterns(title)
            findings.append({
                "title": f"Pastebin credential leak: {title[:120]}",
                "description": (
                    f"A pastebin entry referencing '{vendor_domain}' was found "
                    f"via Google search, potentially containing exposed credentials."
                ),
                "source_url": "https://pastebin.com",
                "severity": "critical",
                "raw_data": {
                    "source": "pastebin_google_search",
                    "original_title": title,
                    "matched_patterns": matched[:10],
                },
            })

        if not titles:
            print(f"  ℹ️ No pastebin results for {vendor_domain}")
    except Exception as exc:
        print(f"  ⚠️ Pastebin search failed: {exc}")

    return findings


# ── Search: General Web Leak Search ──────────────────────────────

async def _search_general_leaks(vendor_domain: str) -> list[dict[str, Any]]:
    """
    Broad Google search for credential leaks referencing the vendor domain.
    """
    findings: list[dict[str, Any]] = []
    import urllib.parse

    query = f'"{vendor_domain}" "leaked credentials" OR "exposed api key" OR "data dump"'
    encoded = urllib.parse.quote_plus(query)
    google_url = f"https://www.google.com/search?q={encoded}&num=10"

    try:
        html = await _fetch_via_unlocker(google_url)

        title_re = re.compile(r"<h3[^>]*>(.*?)</h3>", re.DOTALL)
        strip_tags = re.compile(r"<[^>]+>")
        titles = [strip_tags.sub("", t).strip() for t in title_re.findall(html)]

        for title in titles[:5]:
            if not title:
                continue
            findings.append({
                "title": f"Credential leak reference: {title[:120]}",
                "description": (
                    f"Google search found a result referencing leaked credentials "
                    f"for '{vendor_domain}'."
                ),
                "source_url": google_url,
                "severity": "high",
                "raw_data": {
                    "source": "google_leak_search",
                    "original_title": title,
                },
            })

        if not titles:
            print(f"  ℹ️ No general leak results for {vendor_domain}")
    except Exception as exc:
        print(f"  ⚠️ General leak search failed: {exc}")

    return findings


# ── Public entry point ───────────────────────────────────────────

async def search_credential_leaks(
    vendor_name: str,
    vendor_domain: str,
) -> list[dict[str, Any]]:
    """
    Scan multiple public sources for leaked credentials tied to a vendor.

    Args:
        vendor_name: Human-readable company name.
        vendor_domain: Primary domain (e.g. "acme.com").

    Returns:
        List of finding dicts with keys:
            title, description, source_url, severity, raw_data
    """
    print(f"🔍 [Web Unlocker] Searching credential leaks for '{vendor_name}' ({vendor_domain})")

    all_findings: list[dict[str, Any]] = []

    # Run all three searches (sequentially to respect proxy limits)
    github_findings = await _search_github(vendor_domain)
    all_findings.extend(github_findings)

    pastebin_findings = await _search_pastebin(vendor_domain)
    all_findings.extend(pastebin_findings)

    general_findings = await _search_general_leaks(vendor_domain)
    all_findings.extend(general_findings)

    print(f"  ✅ Credential scan complete — {len(all_findings)} findings")
    return all_findings
