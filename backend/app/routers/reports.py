"""
VendorSentinel — Report Router
Full vendor report combining profile, risk history, signals, and alerts.
"""
from fastapi import APIRouter, HTTPException, status
from app.models import VendorReportResponse
from app import database as db

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get(
    "/{vendor_id}",
    response_model=VendorReportResponse,
    summary="Full vendor risk report",
)
async def get_vendor_report(vendor_id: int) -> VendorReportResponse:
    """Assemble a comprehensive report for a single vendor.

    The report includes the vendor profile, historical risk scores,
    the latest scan signals, the most recent AI risk assessment,
    and all alerts associated with this vendor.

    Args:
        vendor_id: Unique identifier of the vendor.

    Raises:
        HTTPException 404: If the vendor does not exist.
        HTTPException 500: If report assembly fails.
    """
    vendor = await db.get_vendor(vendor_id)
    if vendor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor {vendor_id} not found",
        )

    try:
        risk_history = await db.get_risk_history(vendor_id, limit=30)
        signals = await db.get_scan_results(vendor_id)
        alerts_raw = await db.get_recent_alerts(limit=50)

        # Filter alerts to this vendor only
        vendor_alerts = [a for a in alerts_raw if a.get("vendor_id") == vendor_id]

        # Latest risk score (first entry since history is ordered DESC)
        latest_score = risk_history[0] if risk_history else None

        return VendorReportResponse(
            vendor=vendor,
            risk_history=risk_history,
            latest_signals=signals,
            latest_score=latest_score,
            alerts=vendor_alerts,
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate report for vendor {vendor_id}: {exc}",
        ) from exc
