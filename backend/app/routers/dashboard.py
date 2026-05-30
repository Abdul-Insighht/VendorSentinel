"""
VendorSentinel — Dashboard Router
Aggregate statistics, alert feed, and alert-state mutations.
"""
from fastapi import APIRouter, HTTPException, status
from app.models import DashboardStats, AlertResponse
from app import database as db

router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get(
    "/summary",
    response_model=DashboardStats,
    summary="Dashboard summary statistics",
)
async def get_dashboard_summary() -> DashboardStats:
    """Return high-level KPIs for the dashboard.

    Includes total vendors, risk distribution, average score,
    critical-vendor count, signal count, and unread alert count.
    """
    try:
        stats = await db.get_dashboard_stats()
        return DashboardStats(**stats)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve dashboard stats: {exc}",
        ) from exc


@router.get(
    "/alerts",
    response_model=list[AlertResponse],
    summary="Recent alerts",
)
async def get_recent_alerts(limit: int = 50) -> list[AlertResponse]:
    """Return the most recent alerts across all vendors.

    Args:
        limit: Maximum number of alerts to return (default 50).
    """
    try:
        alerts = await db.get_recent_alerts(limit=limit)
        return [AlertResponse(**a) for a in alerts]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve alerts: {exc}",
        ) from exc


@router.put(
    "/alerts/{alert_id}/read",
    status_code=status.HTTP_200_OK,
    summary="Mark an alert as read",
)
async def mark_alert_as_read(alert_id: int) -> dict:
    """Mark a single alert as read.

    Args:
        alert_id: Unique identifier of the alert.

    Returns:
        Confirmation dict with the alert ID.
    """
    try:
        await db.mark_alert_read(alert_id)
        return {"status": "ok", "alert_id": alert_id}
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to mark alert as read: {exc}",
        ) from exc
