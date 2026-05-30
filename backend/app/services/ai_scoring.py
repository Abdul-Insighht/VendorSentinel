"""
VendorSentinel — AI Risk Scoring Engine
Uses an OpenAI-compatible AI/ML API to produce a holistic risk score
from all collected signals.  Falls back to a deterministic rule-based
scorer when the API is unavailable.
"""

import httpx
import json
import re
from typing import Any

from app.config import settings

# ── Constants ────────────────────────────────────────────────────
MODEL = "gpt-4o-mini"
TEMPERATURE = 0.3
MAX_TOKENS = 1500

SYSTEM_PROMPT = """You are VendorSentinel, an expert third-party cyber-risk analyst.
You will receive a set of OSINT signals collected about a vendor and must produce
a structured risk assessment.

Respond ONLY with valid JSON matching this schema — no markdown fences, no extra text:
{
  "risk_score": <float 1.0-10.0>,
  "risk_level": "<low|medium|high|critical>",
  "reasoning": "<2-4 sentence explanation>",
  "recommended_actions": ["<action1>", "<action2>", ...]
}

Scoring guidelines:
- 1-3: Low risk — no significant issues found
- 4-5: Medium risk — some concerns worth monitoring
- 6-7: High risk — actionable issues requiring attention
- 8-10: Critical risk — immediate action recommended
"""


# ── Helpers ──────────────────────────────────────────────────────

def _build_user_prompt(
    vendor_name: str,
    vendor_domain: str,
    signals: list[dict[str, Any]],
) -> str:
    """Construct the user message listing all collected signals."""
    signal_lines: list[str] = []
    for i, s in enumerate(signals, 1):
        signal_lines.append(
            f"{i}. [{s.get('severity', 'info').upper()}] "
            f"{s.get('title', 'Untitled')}\n"
            f"   {s.get('description', '')[:300]}"
        )

    body = "\n".join(signal_lines) if signal_lines else "No signals were detected."

    return (
        f"Vendor: {vendor_name} ({vendor_domain})\n"
        f"Total signals collected: {len(signals)}\n\n"
        f"--- Signals ---\n{body}\n\n"
        f"Produce the JSON risk assessment."
    )


def _parse_ai_response(raw_text: str) -> dict[str, Any]:
    """
    Parse the AI model's response into a structured dict.
    Handles cases where the model wraps JSON in markdown code fences.
    """
    # Strip markdown code fences if present
    cleaned = raw_text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*", "", cleaned)
    cleaned = re.sub(r"\s*```$", "", cleaned)

    data = json.loads(cleaned)

    # Validate / clamp
    score = float(data.get("risk_score", 5.0))
    score = max(1.0, min(10.0, score))

    level = data.get("risk_level", "medium").lower()
    if level not in ("low", "medium", "high", "critical"):
        level = "medium"

    reasoning = str(data.get("reasoning", ""))
    actions = data.get("recommended_actions", [])
    if isinstance(actions, str):
        actions = [actions]

    return {
        "score": round(score, 1),
        "risk_level": level,
        "reasoning": reasoning,
        "recommended_actions": actions,
    }


# ── Rule-based fallback scorer ───────────────────────────────────

def _rule_based_score(signals: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Deterministic fallback when the AI API is unavailable.
    Builds a score by summing severity weights.
    """
    SEVERITY_WEIGHTS = {
        "critical": 3.0,
        "high": 2.0,
        "medium": 1.0,
        "low": 0.5,
        "info": 0.0,
    }

    score = 2.0  # baseline — no signals = low risk

    severity_counts: dict[str, int] = {
        "critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0,
    }

    for s in signals:
        sev = s.get("severity", "info").lower()
        severity_counts[sev] = severity_counts.get(sev, 0) + 1
        score += SEVERITY_WEIGHTS.get(sev, 0.0)

    score = min(10.0, round(score, 1))

    # Determine level
    if score >= 8.0:
        level = "critical"
    elif score >= 6.0:
        level = "high"
    elif score >= 4.0:
        level = "medium"
    else:
        level = "low"

    # Generate basic reasoning
    parts: list[str] = []
    if severity_counts["critical"]:
        parts.append(f"{severity_counts['critical']} critical signal(s)")
    if severity_counts["high"]:
        parts.append(f"{severity_counts['high']} high-severity signal(s)")
    if severity_counts["medium"]:
        parts.append(f"{severity_counts['medium']} medium-severity signal(s)")
    if severity_counts["low"]:
        parts.append(f"{severity_counts['low']} low-severity signal(s)")

    if parts:
        reasoning = (
            f"Rule-based analysis detected {', '.join(parts)}. "
            f"Combined risk score: {score}/10."
        )
    else:
        reasoning = "No significant signals were detected. Vendor appears low risk."

    # Basic recommended actions
    actions: list[str] = []
    if severity_counts["critical"]:
        actions.append("Immediately investigate critical findings and assess direct impact.")
    if severity_counts["high"]:
        actions.append("Review high-severity findings and request vendor clarification.")
    if severity_counts["medium"]:
        actions.append("Monitor medium-severity issues and schedule periodic review.")
    if not actions:
        actions.append("Continue routine monitoring — no immediate action required.")

    return {
        "score": score,
        "risk_level": level,
        "reasoning": reasoning,
        "recommended_actions": actions,
    }


# ── Public entry point ───────────────────────────────────────────

async def score_vendor_risk(
    vendor_name: str,
    vendor_domain: str,
    signals: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Produce an AI-powered (or rule-based fallback) risk score for a vendor.

    Args:
        vendor_name: Human-readable company name.
        vendor_domain: Primary domain.
        signals: List of findings from all signal collectors.

    Returns:
        Dict with keys: score, risk_level, reasoning, recommended_actions
    """
    print(f"🤖 [AI Scoring] Scoring risk for '{vendor_name}' with {len(signals)} signals")

    # Build the signal summary for DB storage
    signal_summary = {
        "total": len(signals),
        "by_severity": {},
    }
    for s in signals:
        sev = s.get("severity", "info")
        signal_summary["by_severity"][sev] = signal_summary["by_severity"].get(sev, 0) + 1

    # ── Attempt AI scoring ──
    if settings.aiml_api_key:
        try:
            result = await _call_ai_api(vendor_name, vendor_domain, signals)
            result["signal_summary"] = signal_summary
            print(f"  ✅ AI score: {result['score']}/10 ({result['risk_level']})")
            return result
        except Exception as exc:
            print(f"  ⚠️ AI scoring failed ({exc}), using rule-based fallback")

    # ── Fallback ──
    result = _rule_based_score(signals)
    result["signal_summary"] = signal_summary
    print(f"  ✅ Rule-based score: {result['score']}/10 ({result['risk_level']})")
    return result


async def _call_ai_api(
    vendor_name: str,
    vendor_domain: str,
    signals: list[dict[str, Any]],
) -> dict[str, Any]:
    """
    Call the AI/ML API (OpenAI-compatible) to score vendor risk.
    Raises on any API or parsing failure so the caller can fall back.
    """
    url = f"{settings.aiml_api_base_url.rstrip('/')}/chat/completions"

    headers = {
        "Authorization": f"Bearer {settings.aiml_api_key}",
        "Content-Type": "application/json",
    }

    user_prompt = _build_user_prompt(vendor_name, vendor_domain, signals)

    payload = {
        "model": MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "temperature": TEMPERATURE,
        "max_tokens": MAX_TOKENS,
    }

    async with httpx.AsyncClient(timeout=60.0) as client:
        print(f"  📡 AI API POST → {url}")
        resp = await client.post(url, headers=headers, json=payload)
        resp.raise_for_status()

        data = resp.json()
        raw_content = data["choices"][0]["message"]["content"]
        return _parse_ai_response(raw_content)
