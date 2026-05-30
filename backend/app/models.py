"""
VendorSentinel Pydantic Models
Request/Response models for API endpoints.
"""
from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


# ═══════════════════════════════════════════════════════════════
# Vendor Models
# ═══════════════════════════════════════════════════════════════

class VendorCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=200, description="Vendor company name")
    domain: str = Field(..., min_length=1, max_length=200, description="Vendor primary domain (e.g. solarwinds.com)")
    website_url: str = Field(default="", description="Vendor website URL")
    category: str = Field(default="general", description="Vendor category (cloud, identity, payment, etc.)")
    data_sensitivity: str = Field(default="medium", description="Data sensitivity level: low, medium, high, critical")
    description: str = Field(default="", description="Description of vendor relationship")


class VendorUpdate(BaseModel):
    name: Optional[str] = None
    domain: Optional[str] = None
    website_url: Optional[str] = None
    category: Optional[str] = None
    data_sensitivity: Optional[str] = None
    description: Optional[str] = None


class VendorResponse(BaseModel):
    id: int
    name: str
    domain: str
    website_url: str
    category: str
    data_sensitivity: str
    description: str
    logo_url: str
    risk_score: float
    risk_level: str
    last_scanned: Optional[str]
    created_at: str
    updated_at: str


# ═══════════════════════════════════════════════════════════════
# Scan Models
# ═══════════════════════════════════════════════════════════════

class ScanTriggerRequest(BaseModel):
    vendor_ids: Optional[list[int]] = Field(default=None, description="Specific vendor IDs to scan, or null for all")


class ScanResultResponse(BaseModel):
    id: int
    vendor_id: int
    scan_id: str
    signal_type: str
    severity: str
    title: str
    description: str
    source_url: str
    raw_data: str
    found_at: str


class ScanHistoryResponse(BaseModel):
    id: int
    scan_id: str
    status: str
    vendors_scanned: int
    total_signals_found: int
    started_at: str
    completed_at: Optional[str]
    error_log: str


# ═══════════════════════════════════════════════════════════════
# Risk Score Models
# ═══════════════════════════════════════════════════════════════

class RiskScoreResponse(BaseModel):
    id: int
    vendor_id: int
    scan_id: str
    score: float
    risk_level: str
    ai_reasoning: str
    recommended_actions: str
    signal_summary: str
    scored_at: str


# ═══════════════════════════════════════════════════════════════
# Alert Models
# ═══════════════════════════════════════════════════════════════

class AlertResponse(BaseModel):
    id: int
    vendor_id: int
    vendor_name: Optional[str] = ""
    scan_id: str
    alert_type: str
    severity: str
    title: str
    message: str
    is_read: int
    created_at: str


# ═══════════════════════════════════════════════════════════════
# Dashboard Models
# ═══════════════════════════════════════════════════════════════

class DashboardStats(BaseModel):
    total_vendors: int
    risk_distribution: dict
    average_risk_score: float
    critical_vendors: int
    total_signals: int
    unread_alerts: int


# ═══════════════════════════════════════════════════════════════
# Report Models
# ═══════════════════════════════════════════════════════════════

class VendorReportResponse(BaseModel):
    vendor: dict
    risk_history: list[dict]
    latest_signals: list[dict]
    latest_score: Optional[dict]
    alerts: list[dict]
