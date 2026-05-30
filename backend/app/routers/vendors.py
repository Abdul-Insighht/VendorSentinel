"""
VendorSentinel — Vendor CRUD Router
Handles creation, retrieval, update, and deletion of vendor records.
"""
from fastapi import APIRouter, HTTPException, status
from app.models import VendorCreate, VendorUpdate, VendorResponse
from app import database as db

router = APIRouter(prefix="/api/vendors", tags=["Vendors"])


@router.post(
    "",
    response_model=VendorResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new vendor",
)
async def create_vendor(vendor: VendorCreate) -> VendorResponse:
    """Create a new third-party vendor to monitor.

    Args:
        vendor: Vendor details including name, domain, and sensitivity level.

    Returns:
        The newly created vendor record.

    Raises:
        HTTPException 500: If the vendor could not be persisted.
    """
    try:
        result = await db.create_vendor(
            name=vendor.name,
            domain=vendor.domain,
            website_url=vendor.website_url,
            category=vendor.category,
            data_sensitivity=vendor.data_sensitivity,
            description=vendor.description,
        )
        return VendorResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create vendor: {exc}",
        ) from exc


@router.get(
    "",
    response_model=list[VendorResponse],
    summary="List all vendors",
)
async def list_vendors() -> list[VendorResponse]:
    """Return every registered vendor, ordered by risk score descending."""
    try:
        vendors = await db.get_all_vendors()
        return [VendorResponse(**v) for v in vendors]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve vendors: {exc}",
        ) from exc


@router.get(
    "/{vendor_id}",
    response_model=VendorResponse,
    summary="Get vendor details",
)
async def get_vendor(vendor_id: int) -> VendorResponse:
    """Fetch a single vendor by its ID.

    Args:
        vendor_id: Unique identifier of the vendor.

    Raises:
        HTTPException 404: If the vendor does not exist.
    """
    vendor = await db.get_vendor(vendor_id)
    if vendor is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor {vendor_id} not found",
        )
    return VendorResponse(**vendor)


@router.put(
    "/{vendor_id}",
    response_model=VendorResponse,
    summary="Update a vendor",
)
async def update_vendor(vendor_id: int, updates: VendorUpdate) -> VendorResponse:
    """Partially update a vendor's mutable fields.

    Only the fields present in the request body will be changed.

    Args:
        vendor_id: Unique identifier of the vendor.
        updates: Fields to update.

    Raises:
        HTTPException 404: If the vendor does not exist.
    """
    existing = await db.get_vendor(vendor_id)
    if existing is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor {vendor_id} not found",
        )
    try:
        # Only send non-None fields to the database layer
        update_data = updates.model_dump(exclude_unset=True)
        result = await db.update_vendor(vendor_id, **update_data)
        return VendorResponse(**result)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update vendor: {exc}",
        ) from exc


@router.delete(
    "/{vendor_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a vendor",
)
async def delete_vendor(vendor_id: int) -> None:
    """Remove a vendor and all associated scan data.

    Args:
        vendor_id: Unique identifier of the vendor to delete.

    Raises:
        HTTPException 404: If the vendor does not exist.
    """
    deleted = await db.delete_vendor(vendor_id)
    if not deleted:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vendor {vendor_id} not found",
        )
