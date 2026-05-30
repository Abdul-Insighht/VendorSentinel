"""
VendorSentinel — Signal 3: Hiring Distress Detection
Uses Bright Data Web Scraper API to monitor LinkedIn job postings
for spikes in security-related hiring that may indicate an active
incident or significant internal security concerns.
"""

import httpx
import json
import re
from typing import Any

from app.config import settings

# ── Constants ────────────────────────────────────────────────────
SCRAPER_TRIGGER_URL = "https://api.brightdata.com/datasets/v3/trigger"
SCRAPER_SCRAPE_URL = "https://api.brightdata.com/datasets/v3/scrape"
PROXY_HOST = "brd.superproxy.io"
PROXY_PORT = 33335

# Security-specific role keywords (case-insensitive matching)
SECURITY_ROLES: list[str] = [
    "security engineer",
    "ciso",
    "chief information security officer",
    "incident response",
    "threat intelligence",
    "penetration tester",
    "soc analyst",
    "security architect",
    "security analyst",
    "application security",
    "devsecops",
    "cybersecurity",
    "information security",
    "security operations",
    "vulnerability management",
]

# Thresholds for spike detection
NORMAL_SECURITY_POSTINGS = 3  # typical baseline
ELEVATED_THRESHOLD = 5        # elevated concern
SPIKE_THRESHOLD = 10          # clear spike — likely incident response


# ── Helper ───────────────────────────────────────────────────────

def _is_security_role(title: str) -> bool:
    """Check if a job title matches a security-related role."""
    lower = title.lower()
    return any(role in lower for role in SECURITY_ROLES)


def _analyse_postings(
    postings: list[dict[str, Any]],
    vendor_name: str,
) -> list[dict[str, Any]]:
    """
    Analyse a list of job postings for security-hiring distress signals.
    Returns a list of structured findings.
    """
    findings: list[dict[str, Any]] = []

    # Filter to security roles
    security_postings = [p for p in postings if _is_security_role(p.get("title", ""))]
    total_security = len(security_postings)
    total_all = len(postings)

    print(f"  📊 {total_security}/{total_all} postings are security-related")

    # ---- Spike analysis ----
    if total_security >= SPIKE_THRESHOLD:
        severity = "high"
        title = f"Security hiring spike detected at {vendor_name}"
        description = (
            f"{vendor_name} has {total_security} active security job postings, "
            f"significantly above the normal baseline of ~{NORMAL_SECURITY_POSTINGS}. "
            f"This may indicate an ongoing security incident, breach remediation, "
            f"or major security programme overhaul."
        )
    elif total_security >= ELEVATED_THRESHOLD:
        severity = "medium"
        title = f"Elevated security hiring at {vendor_name}"
        description = (
            f"{vendor_name} has {total_security} active security job postings, "
            f"above the typical baseline. This may reflect proactive investment "
            f"or a response to a recent incident."
        )
    elif total_security > 0:
        severity = "low"
        title = f"Normal security hiring at {vendor_name}"
        description = (
            f"{vendor_name} has {total_security} active security job postings, "
            f"within a normal range."
        )
    else:
        severity = "info"
        title = f"No security hiring detected at {vendor_name}"
        description = (
            f"No security-specific job postings were found for {vendor_name}."
        )

    role_titles = [p.get("title", "Unknown") for p in security_postings[:20]]

    findings.append({
        "title": title,
        "description": description,
        "source_url": f"https://www.linkedin.com/company/{vendor_name.lower().replace(' ', '-')}/jobs/",
        "severity": severity,
        "raw_data": {
            "total_postings": total_all,
            "security_postings": total_security,
            "security_role_titles": role_titles,
            "spike_threshold": SPIKE_THRESHOLD,
            "elevated_threshold": ELEVATED_THRESHOLD,
        },
    })

    # Flag individual critical roles (incident response = extra signal)
    ir_postings = [
        p for p in security_postings
        if "incident response" in p.get("title", "").lower()
    ]
    if ir_postings:
        findings.append({
            "title": f"Incident Response hiring at {vendor_name}",
            "description": (
                f"{vendor_name} is actively hiring {len(ir_postings)} Incident "
                f"Response role(s). This may signal an active or recent security "
                f"incident requiring remediation."
            ),
            "source_url": f"https://www.linkedin.com/company/{vendor_name.lower().replace(' ', '-')}/jobs/",
            "severity": "high",
            "raw_data": {
                "incident_response_roles": [p.get("title") for p in ir_postings],
            },
        })

    return findings


# ── Approach 1: Bright Data Web Scraper API ─────────────────────

async def _scrape_via_api(vendor_name: str) -> list[dict[str, Any]]:
    """
    Use Bright Data's Web Scraper /scrape endpoint to fetch LinkedIn
    job postings for *vendor_name*.
    """
    headers = {
        "Authorization": f"Bearer {settings.bright_data_api_token}",
        "Content-Type": "application/json",
    }

    company_slug = vendor_name.lower().replace(" ", "-")
    target_url = f"https://www.linkedin.com/company/{company_slug}/jobs/"

    payload = [{"url": target_url}]

    async with httpx.AsyncClient(timeout=90.0) as client:
        print(f"  📡 Web Scraper POST → {SCRAPER_SCRAPE_URL}")
        resp = await client.post(
            SCRAPER_SCRAPE_URL,
            headers=headers,
            json=payload,
            params={"format": "json"},
        )
        resp.raise_for_status()

        data = resp.json()
        # Normalise — response may be a list of job objects or a wrapper
        if isinstance(data, list):
            return data
        if isinstance(data, dict):
            return data.get("results", data.get("jobs", [data]))
        return []


# ── Approach 2: Google search fallback ───────────────────────────

async def _scrape_via_google_fallback(vendor_name: str) -> list[dict[str, Any]]:
    """
    Fallback: search Google for LinkedIn job postings via the Bright
    Data Web Unlocker proxy and parse titles from the SERP HTML.
    """
    import urllib.parse

    username = settings.bright_data_unlocker_username
    password = settings.bright_data_unlocker_password
    proxy_url = f"http://{username}:{password}@{PROXY_HOST}:{PROXY_PORT}"

    query = f'site:linkedin.com/jobs "{vendor_name}" security engineer OR CISO OR incident response OR SOC analyst'
    encoded = urllib.parse.quote_plus(query)
    google_url = f"https://www.google.com/search?q={encoded}&num=20"

    async with httpx.AsyncClient(
        proxies={"http://": proxy_url, "https://": proxy_url},
        timeout=60.0,
        verify=False,
    ) as client:
        print(f"  📡 Google fallback GET → {google_url}")
        resp = await client.get(google_url)
        resp.raise_for_status()

        # Extract titles from HTML
        title_re = re.compile(r"<h3[^>]*>(.*?)</h3>", re.DOTALL)
        strip_tags = re.compile(r"<[^>]+>")
        raw_titles = title_re.findall(resp.text)

        postings: list[dict[str, Any]] = []
        for raw in raw_titles[:20]:
            clean = strip_tags.sub("", raw).strip()
            if clean:
                postings.append({"title": clean, "source": "google_fallback"})

        return postings


# ── Public entry point ───────────────────────────────────────────

async def search_hiring_signals(
    vendor_name: str,
    vendor_domain: str,
) -> list[dict[str, Any]]:
    """
    Detect security-hiring distress signals for a vendor.

    Args:
        vendor_name: Human-readable company name.
        vendor_domain: Primary domain (used for context only).

    Returns:
        List of finding dicts with keys:
            title, description, source_url, severity, raw_data
    """
    print(f"🔍 [Web Scraper] Checking hiring signals for '{vendor_name}' ({vendor_domain})")

    postings: list[dict[str, Any]] = []

    # Attempt 1 — Web Scraper API
    try:
        postings = await _scrape_via_api(vendor_name)
        if postings:
            print(f"  ✅ Web Scraper API returned {len(postings)} postings")
    except Exception as exc:
        print(f"  ⚠️ Web Scraper API failed ({exc}), falling back to Google search")

    # Attempt 2 — Google fallback
    if not postings:
        try:
            postings = await _scrape_via_google_fallback(vendor_name)
            print(f"  ✅ Google fallback returned {len(postings)} postings")
        except Exception as exc:
            print(f"  ❌ Google fallback also failed ({exc})")

    # Analyse whatever we got (even an empty list produces an info finding)
    findings = _analyse_postings(postings, vendor_name)
    print(f"  ✅ Hiring analysis complete — {len(findings)} findings")
    return findings
