import uuid
import hashlib

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.security import decode_access_token
from app.db.session import get_db
from app.dependencies.auth import bearer_scheme
from app.models import ListingView, PGListing, User
from app.models.enums import GenderAllowed, ListingStatus
from app.schemas.pg import PaginatedPGResponse, PGListingPublicResponse
from app.services.analytics_service import is_pg_featured, review_stats

router = APIRouter(prefix="/pgs", tags=["pgs"])


def _public_base_query():
    return (
        select(PGListing)
        .options(selectinload(PGListing.rooms), selectinload(PGListing.photos))
        .where(PGListing.status == ListingStatus.APPROVED, PGListing.admin_verified.is_(True))
    )


def _public_response(db: Session, listing: PGListing) -> PGListingPublicResponse:
    avg, count = review_stats(db, listing.id)
    response = PGListingPublicResponse.model_validate(listing, from_attributes=True)
    response.average_rating = avg
    response.review_count = count
    response.is_featured = is_pg_featured(db, listing.id)
    return response


def _optional_viewer(credentials: HTTPAuthorizationCredentials | None, db: Session) -> uuid.UUID | None:
    if not credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user_id = uuid.UUID(str(payload.get("sub")))
        return user_id if db.get(User, user_id) else None
    except Exception:
        return None


@router.get("", response_model=PaginatedPGResponse)
def list_public_pgs(
    min_price: int | None = Query(default=None, ge=0),
    max_price: int | None = Query(default=None, ge=0),
    gender_allowed: GenderAllowed | None = None,
    food_available: bool | None = None,
    wifi_available: bool | None = None,
    ac_available: bool | None = None,
    max_distance_km: float | None = Query(default=None, ge=0),
    search: str | None = None,
    sort: str = Query(default="newest", pattern="^(newest|price_low_to_high|price_high_to_low|distance_low_to_high)$"),
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    db: Session = Depends(get_db),
) -> PaginatedPGResponse:
    query = _public_base_query()
    if min_price is not None:
        query = query.where(or_(PGListing.monthly_rent_max >= min_price, PGListing.monthly_rent_max.is_(None)))
    if max_price is not None:
        query = query.where(or_(PGListing.monthly_rent_min <= max_price, PGListing.monthly_rent_min.is_(None)))
    if gender_allowed is not None:
        query = query.where(PGListing.gender_allowed == gender_allowed)
    if food_available is not None:
        query = query.where(PGListing.food_available == food_available)
    if wifi_available is not None:
        query = query.where(PGListing.wifi_available == wifi_available)
    if ac_available is not None:
        query = query.where(PGListing.ac_available == ac_available)
    if max_distance_km is not None:
        query = query.where(PGListing.distance_from_lpu_km <= max_distance_km)
    if search:
        term = f"%{search.strip()}%"
        query = query.where(or_(PGListing.pg_name.ilike(term), PGListing.address.ilike(term), PGListing.landmark.ilike(term)))

    if sort == "price_low_to_high":
        query = query.order_by(PGListing.monthly_rent_min.asc().nullslast())
    elif sort == "price_high_to_low":
        query = query.order_by(PGListing.monthly_rent_min.desc().nullslast())
    elif sort == "distance_low_to_high":
        query = query.order_by(PGListing.distance_from_lpu_km.asc().nullslast())
    else:
        query = query.order_by(PGListing.created_at.desc())

    listings = db.scalars(query).all()
    total = len(listings)
    items = [_public_response(db, listing) for listing in listings]
    items.sort(key=lambda item: (item.is_featured, item.created_at), reverse=True)
    start = (page - 1) * page_size
    return PaginatedPGResponse(items=items[start:start + page_size], total=total, page=page, page_size=page_size)


@router.get("/{pg_id}", response_model=PGListingPublicResponse)
def get_public_pg(
    pg_id: uuid.UUID,
    request: Request,
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    db: Session = Depends(get_db),
) -> PGListingPublicResponse:
    listing = db.scalar(_public_base_query().where(PGListing.id == pg_id))
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PG listing not found.")
    try:
        ip = request.client.host if request.client else ""
        ua = request.headers.get("user-agent", "")
        db.add(
            ListingView(
                pg_id=listing.id,
                viewer_id=_optional_viewer(credentials, db),
                ip_hash=hashlib.sha256(ip.encode()).hexdigest() if ip else None,
                user_agent_hash=hashlib.sha256(ua.encode()).hexdigest() if ua else None,
            )
        )
        db.commit()
    except Exception:
        db.rollback()
    return _public_response(db, listing)
