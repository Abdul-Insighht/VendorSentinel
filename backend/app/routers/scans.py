"""
VendorSentinel — Scan Management Router
Trigger, monitor, and retrieve scan results.
Scans are kicked off as background asyncio tasks so the API responds immediately.
"""
import asyncio
import logging
from fastapi import APIRouter, HTTPException, status
from app.models import ScanResultResponse, ScanHistoryResponse
from app import database as db

logger = logging.getLogger("vendorsentinel.scans")

# ── Lazy-import scanner so the app starts even without scanner deps ──
_scanner = None


def _get_scanner():
    """Lazily import the scanner module, caching the result."""
    global _scanner
    if _scanner is None:
        try:
            from app.services import scanner as _mod  # type: ignore[import-untyped]
            _scanner = _mod
        except ImportError as exc:
            logger.warning("Scanner module not available: %s", exc)
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Scanner service is not installed or configured yet.",
            ) from exc
    return _scanner


router = APIRouter(prefix="/api/scans", tags=["Scans"])


@router.post(
    "/trigger",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger a full scan of all vendors",
)
async def trigger_full_scan() -> dict:
    """Launch a background scan across **every** registered vendor.

    The scan runs asynchronously — this endpoint returns immediately with a
    confirmation message while the work continues in the background.

    Returns:
        A dict with a status message.

    Raises:
        HTTPException 503: If the scanner module is unavailable.
    """
    scanner = _get_scanner()
    asyncio.create_task(scanner.run_full_scan())
    logger.info("Full scan triggered in background")
    return {"status": "accepted", "message": "Full scan started in background"}


@router.post(
    "/trigger/{vendor_id}",
    status_code=status.HTTP_202_ACCEPTED,
    summary="Trigger a scan for a single vendor",
)
async def trigger_vendor_scan(vendor_id: int) -> dict:
    """Launch a background scan for one specific vendor.

    Args:
        vendor_id: Unique identifier of the vendor to scan.

    Returns:
        A dict with a status message.

    Raises:
        HTTPException 404: If the vendor does not exist.
        HTTPException 503: If the scanner module is unavailable.
    """
    vendor = await db.get_vendor(vendor_id)
    if vendor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor {vendor_id} not found",
        )

    scanner = _get_scanner()

    # Create a scan record and pass the full vendor dict + scan_id
    import uuid
    from datetime import datetime
    scan_id = str(uuid.uuid4())
    try:
        await db.create_scan_record(scan_id)
    except Exception as exc:
        logger.warning("Failed to create scan record: %s", exc)

    async def run_and_finalize_single_scan():
        try:
            signals = await scanner.scan_single_vendor(vendor, scan_id)
            await db.update_scan_record(
                scan_id,
                status="completed",
                vendors_scanned=1,
                total_signals_found=len(signals),
                completed_at=datetime.utcnow().isoformat(),
            )
        except Exception as exc:
            logger.error("Single vendor scan failed: %s", exc)
            try:
                await db.update_scan_record(
                    scan_id,
                    status="completed",
                    vendors_scanned=1,
                    total_signals_found=0,
                    completed_at=datetime.utcnow().isoformat(),
                    error_log=str(exc),
                )
            except Exception as db_exc:
                logger.error("Failed to update scan record after crash: %s", db_exc)

    asyncio.create_task(run_and_finalize_single_scan())
    logger.info("Scan triggered for vendor %s (scan_id=%s) in background", vendor_id, scan_id)
    return {
        "status": "accepted",
        "message": f"Scan for vendor {vendor_id} started in background",
        "scan_id": scan_id,
    }


@router.get(
    "/history",
    response_model=list[ScanHistoryResponse],
    summary="Get scan history",
)
async def get_scan_history(limit: int = 20) -> list[ScanHistoryResponse]:
    """Return the most recent scan execution records.

    Args:
        limit: Maximum number of records to return (default 20).
    """
    try:
        history = await db.get_scan_history(limit=limit)
        return [ScanHistoryResponse(**h) for h in history]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve scan history: {exc}",
        ) from exc


@router.get(
    "/latest",
    response_model=list[ScanResultResponse],
    summary="Get latest scan results",
)
async def get_latest_results() -> list[ScanResultResponse]:
    """Return the most recent scan results across all vendors."""
    try:
        results = await db.get_latest_scan_results_all()
        return [ScanResultResponse(**r) for r in results]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve latest scan results: {exc}",
        ) from exc
