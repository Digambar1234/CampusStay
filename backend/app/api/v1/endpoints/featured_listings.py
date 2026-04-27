import uuid
from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies.auth import require_roles
from app.models import FeaturedListing, PGListing, User
from app.models.enums import FeaturedListingStatus, ListingStatus, Role
from app.schemas.trust import FeaturedListingCreate, FeaturedListingResponse
from app.services.pg_service import log_admin_action

router = APIRouter(prefix="/admin/featured-listings", tags=["admin-featured-listings"])


def _response(item: FeaturedListing) -> FeaturedListingResponse:
    return FeaturedListingResponse(
        id=item.id, pg_id=item.pg_id, pg_name=item.pg.pg_name, owner_id=item.owner_id, status=item.status,
        starts_at=item.starts_at, ends_at=item.ends_at, amount_rupees=item.amount_rupees, source=item.source,
        created_at=item.created_at, updated_at=item.updated_at,
    )


@router.post("", response_model=FeaturedListingResponse, status_code=201)
def create_featured(payload: FeaturedListingCreate, admin: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> FeaturedListingResponse:
    listing = db.get(PGListing, payload.pg_id)
    if not listing or listing.status != ListingStatus.APPROVED or not listing.admin_verified:
        raise HTTPException(status_code=404, detail="Approved PG listing not found.")
    now = datetime.now(UTC)
    featured = FeaturedListing(pg_id=listing.id, owner_id=listing.owner_id, starts_at=now, ends_at=now + timedelta(days=payload.days), amount_rupees=payload.amount_rupees, source=payload.source, status=FeaturedListingStatus.ACTIVE)
    db.add(featured)
    log_admin_action(db, admin, "create_featured_listing", listing, {"days": payload.days, "amount_rupees": payload.amount_rupees})
    db.commit()
    return _response(db.scalar(select(FeaturedListing).options(selectinload(FeaturedListing.pg)).where(FeaturedListing.id == featured.id)))


@router.get("", response_model=list[FeaturedListingResponse])
def list_featured(_: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> list[FeaturedListingResponse]:
    items = db.scalars(select(FeaturedListing).options(selectinload(FeaturedListing.pg)).order_by(FeaturedListing.created_at.desc())).all()
    return [_response(item) for item in items]


@router.post("/{featured_id}/cancel", response_model=FeaturedListingResponse)
def cancel_featured(featured_id: uuid.UUID, admin: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> FeaturedListingResponse:
    item = db.scalar(select(FeaturedListing).options(selectinload(FeaturedListing.pg)).where(FeaturedListing.id == featured_id))
    if not item:
        raise HTTPException(status_code=404, detail="Featured listing not found.")
    item.status = FeaturedListingStatus.CANCELLED
    log_admin_action(db, admin, "cancel_featured_listing", item.pg, {"featured_id": str(item.id)})
    db.commit()
    db.refresh(item)
    return _response(item)
