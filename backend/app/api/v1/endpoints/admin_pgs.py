import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies.auth import require_roles
from app.models import PGListing, User
from app.models.enums import ListingStatus, Role
from app.schemas.pg import AdminRejectRequest, AdminRequestChangesRequest, PaginatedAdminPGResponse, PGListingAdminResponse
from app.services.pg_service import get_listing_or_404, log_admin_action

router = APIRouter(prefix="/admin/pgs", tags=["admin-pgs"])


def _admin_query(status_value: ListingStatus, page: int, page_size: int, db: Session) -> PaginatedAdminPGResponse:
    base_query = (
        select(PGListing)
        .options(selectinload(PGListing.rooms), selectinload(PGListing.photos), selectinload(PGListing.owner))
        .where(PGListing.status == status_value)
    )
    total = db.scalar(select(func.count()).select_from(base_query.subquery())) or 0
    listings = db.scalars(
        base_query.order_by(PGListing.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return PaginatedAdminPGResponse(items=list(listings), total=total, page=page, page_size=page_size)


@router.get("/pending", response_model=PaginatedAdminPGResponse)
def list_pending_pgs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)),
    db: Session = Depends(get_db),
) -> PaginatedAdminPGResponse:
    return _admin_query(ListingStatus.PENDING_REVIEW, page, page_size, db)


@router.get("/approved", response_model=PaginatedAdminPGResponse)
def list_approved_pgs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)),
    db: Session = Depends(get_db),
) -> PaginatedAdminPGResponse:
    return _admin_query(ListingStatus.APPROVED, page, page_size, db)


@router.get("/rejected", response_model=PaginatedAdminPGResponse)
def list_rejected_pgs(
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    _: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)),
    db: Session = Depends(get_db),
) -> PaginatedAdminPGResponse:
    return _admin_query(ListingStatus.REJECTED, page, page_size, db)


@router.get("/{pg_id}", response_model=PGListingAdminResponse)
def get_admin_pg(
    pg_id: uuid.UUID,
    _: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)),
    db: Session = Depends(get_db),
) -> PGListing:
    return get_listing_or_404(db, pg_id)


@router.post("/{pg_id}/approve", response_model=PGListingAdminResponse)
def approve_pg(
    pg_id: uuid.UUID,
    admin: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)),
    db: Session = Depends(get_db),
) -> PGListing:
    listing = get_listing_or_404(db, pg_id)
    listing.status = ListingStatus.APPROVED
    listing.admin_verified = True
    log_admin_action(db, admin, "approve", listing)
    db.commit()
    return get_listing_or_404(db, pg_id)


@router.post("/{pg_id}/reject", response_model=PGListingAdminResponse)
def reject_pg(
    pg_id: uuid.UUID,
    payload: AdminRejectRequest,
    admin: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)),
    db: Session = Depends(get_db),
) -> PGListing:
    listing = get_listing_or_404(db, pg_id)
    listing.status = ListingStatus.REJECTED
    listing.admin_verified = False
    log_admin_action(db, admin, "reject", listing, {"reason": payload.reason})
    db.commit()
    return get_listing_or_404(db, pg_id)


@router.post("/{pg_id}/suspend", response_model=PGListingAdminResponse)
def suspend_pg(
    pg_id: uuid.UUID,
    payload: AdminRejectRequest,
    admin: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)),
    db: Session = Depends(get_db),
) -> PGListing:
    listing = get_listing_or_404(db, pg_id)
    listing.status = ListingStatus.SUSPENDED
    listing.admin_verified = False
    log_admin_action(db, admin, "suspend", listing, {"reason": payload.reason})
    db.commit()
    return get_listing_or_404(db, pg_id)


@router.post("/{pg_id}/request-changes", response_model=PGListingAdminResponse)
def request_changes_pg(
    pg_id: uuid.UUID,
    payload: AdminRequestChangesRequest,
    admin: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)),
    db: Session = Depends(get_db),
) -> PGListing:
    listing = get_listing_or_404(db, pg_id)
    listing.status = ListingStatus.REJECTED
    listing.admin_verified = False
    log_admin_action(db, admin, "request_changes", listing, {"message": payload.message})
    db.commit()
    return get_listing_or_404(db, pg_id)
