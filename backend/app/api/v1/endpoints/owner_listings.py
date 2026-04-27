import uuid

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, Request, UploadFile, status
from sqlalchemy import delete, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies.auth import require_roles
from app.models import PGListing, PGPhoto, PGRoom, User
from app.models.enums import ImageType, ListingStatus, Role
from app.schemas.pg import (
    PaginatedOwnerPGResponse,
    PGListingCreate,
    PGListingOwnerResponse,
    PGListingSummaryResponse,
    PGListingUpdate,
    PGPhotoResponse,
    PGRoomCreate,
    PGRoomResponse,
    PGRoomUpdate,
    SuccessResponse,
)
from app.services.cloudinary_service import delete_cloudinary_asset, upload_pg_photo
from app.services.pg_service import (
    ensure_owner_can_delete,
    ensure_owner_can_edit,
    get_owner_listing_or_404,
    set_primary_photo,
    validate_listing_ready_for_review,
)
from app.core.rate_limit import limiter

router = APIRouter(prefix="/owner/listings", tags=["owner-listings"])


def _summary(listing: PGListing) -> PGListingSummaryResponse:
    primary_photo = next((photo for photo in listing.photos if photo.is_primary), None)
    return PGListingSummaryResponse(
        id=listing.id,
        pg_name=listing.pg_name,
        address=listing.address,
        distance_from_lpu_km=listing.distance_from_lpu_km,
        gender_allowed=listing.gender_allowed,
        monthly_rent_min=listing.monthly_rent_min,
        monthly_rent_max=listing.monthly_rent_max,
        status=listing.status,
        admin_verified=listing.admin_verified,
        rooms_count=len(listing.rooms),
        photos_count=len(listing.photos),
        primary_photo_url=primary_photo.image_url if primary_photo else None,
        created_at=listing.created_at,
    )


@router.post("", response_model=PGListingOwnerResponse, status_code=status.HTTP_201_CREATED)
def create_listing(
    payload: PGListingCreate,
    submit: bool = Query(default=False),
    current_user: User = Depends(require_roles(Role.PG_OWNER)),
    db: Session = Depends(get_db),
) -> PGListing:
    listing = PGListing(
        owner_id=current_user.id,
        status=ListingStatus.PENDING_REVIEW if submit else ListingStatus.DRAFT,
        **payload.model_dump(),
    )
    db.add(listing)
    db.commit()
    db.refresh(listing)
    return listing


@router.get("", response_model=PaginatedOwnerPGResponse)
def list_owner_listings(
    current_user: User = Depends(require_roles(Role.PG_OWNER)),
    db: Session = Depends(get_db),
) -> PaginatedOwnerPGResponse:
    listings = db.scalars(
        select(PGListing)
        .options(selectinload(PGListing.rooms), selectinload(PGListing.photos))
        .where(PGListing.owner_id == current_user.id)
        .order_by(PGListing.created_at.desc())
    ).all()
    return PaginatedOwnerPGResponse(items=[_summary(listing) for listing in listings], total=len(listings))


@router.get("/{pg_id}", response_model=PGListingOwnerResponse)
def get_owner_listing(
    pg_id: uuid.UUID,
    current_user: User = Depends(require_roles(Role.PG_OWNER)),
    db: Session = Depends(get_db),
) -> PGListing:
    return get_owner_listing_or_404(db, current_user, pg_id)


@router.patch("/{pg_id}", response_model=PGListingOwnerResponse)
def update_owner_listing(
    pg_id: uuid.UUID,
    payload: PGListingUpdate,
    current_user: User = Depends(require_roles(Role.PG_OWNER)),
    db: Session = Depends(get_db),
) -> PGListing:
    listing = get_owner_listing_or_404(db, current_user, pg_id)
    ensure_owner_can_edit(listing)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(listing, field, value)
    db.commit()
    db.refresh(listing)
    return get_owner_listing_or_404(db, current_user, pg_id)


@router.post("/{pg_id}/submit", response_model=PGListingOwnerResponse)
def submit_owner_listing(
    pg_id: uuid.UUID,
    current_user: User = Depends(require_roles(Role.PG_OWNER)),
    db: Session = Depends(get_db),
) -> PGListing:
    listing = get_owner_listing_or_404(db, current_user, pg_id)
    if listing.status not in {ListingStatus.DRAFT, ListingStatus.REJECTED, ListingStatus.PENDING_REVIEW}:
        ensure_owner_can_edit(listing)
    validate_listing_ready_for_review(listing)
    listing.status = ListingStatus.PENDING_REVIEW
    listing.admin_verified = False
    db.commit()
    return get_owner_listing_or_404(db, current_user, pg_id)


@router.delete("/{pg_id}", response_model=SuccessResponse)
def delete_owner_listing(
    pg_id: uuid.UUID,
    current_user: User = Depends(require_roles(Role.PG_OWNER)),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    listing = get_owner_listing_or_404(db, current_user, pg_id)
    ensure_owner_can_delete(listing)
    db.delete(listing)
    db.commit()
    return SuccessResponse(message="PG listing deleted.")


@router.post("/{pg_id}/rooms", response_model=PGRoomResponse, status_code=status.HTTP_201_CREATED)
def add_room(
    pg_id: uuid.UUID,
    payload: PGRoomCreate,
    current_user: User = Depends(require_roles(Role.PG_OWNER)),
    db: Session = Depends(get_db),
) -> PGRoom:
    listing = get_owner_listing_or_404(db, current_user, pg_id)
    ensure_owner_can_edit(listing)
    room = PGRoom(pg_id=listing.id, **payload.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@router.patch("/{pg_id}/rooms/{room_id}", response_model=PGRoomResponse)
def update_room(
    pg_id: uuid.UUID,
    room_id: uuid.UUID,
    payload: PGRoomUpdate,
    current_user: User = Depends(require_roles(Role.PG_OWNER)),
    db: Session = Depends(get_db),
) -> PGRoom:
    listing = get_owner_listing_or_404(db, current_user, pg_id)
    ensure_owner_can_edit(listing)
    room = db.scalar(select(PGRoom).where(PGRoom.id == room_id, PGRoom.pg_id == listing.id))
    if room is None:
        raise HTTPException(status_code=404, detail="Room not found.")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(room, field, value)
    db.commit()
    db.refresh(room)
    return room


@router.delete("/{pg_id}/rooms/{room_id}", response_model=SuccessResponse)
def delete_room(
    pg_id: uuid.UUID,
    room_id: uuid.UUID,
    current_user: User = Depends(require_roles(Role.PG_OWNER)),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    listing = get_owner_listing_or_404(db, current_user, pg_id)
    ensure_owner_can_edit(listing)
    result = db.execute(delete(PGRoom).where(PGRoom.id == room_id, PGRoom.pg_id == listing.id))
    if result.rowcount == 0:
        raise HTTPException(status_code=404, detail="Room not found.")
    db.commit()
    return SuccessResponse(message="Room deleted.")


@router.post("/{pg_id}/photos", response_model=PGPhotoResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("10/minute")
async def upload_photo(
    request: Request,
    pg_id: uuid.UUID,
    file: UploadFile = File(...),
    image_type: ImageType = Form(...),
    is_primary: bool = Form(False),
    current_user: User = Depends(require_roles(Role.PG_OWNER)),
    db: Session = Depends(get_db),
) -> PGPhoto:
    listing = get_owner_listing_or_404(db, current_user, pg_id)
    ensure_owner_can_edit(listing)
    upload_result = await upload_pg_photo(file, str(pg_id))
    if is_primary:
        for existing_photo in listing.photos:
            existing_photo.is_primary = False
    photo = PGPhoto(
        pg_id=listing.id,
        image_url=upload_result["secure_url"],
        public_id=upload_result["public_id"],
        image_type=image_type,
        is_primary=is_primary or len(listing.photos) == 0,
    )
    db.add(photo)
    db.commit()
    db.refresh(photo)
    return photo


@router.delete("/{pg_id}/photos/{photo_id}", response_model=SuccessResponse)
def delete_photo(
    pg_id: uuid.UUID,
    photo_id: uuid.UUID,
    current_user: User = Depends(require_roles(Role.PG_OWNER)),
    db: Session = Depends(get_db),
) -> SuccessResponse:
    listing = get_owner_listing_or_404(db, current_user, pg_id)
    ensure_owner_can_edit(listing)
    photo = db.scalar(select(PGPhoto).where(PGPhoto.id == photo_id, PGPhoto.pg_id == listing.id))
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found.")
    public_id = photo.public_id
    db.delete(photo)
    db.commit()
    delete_cloudinary_asset(public_id)
    return SuccessResponse(message="Photo deleted.")


@router.patch("/{pg_id}/photos/{photo_id}/primary", response_model=PGPhotoResponse)
def mark_primary_photo(
    pg_id: uuid.UUID,
    photo_id: uuid.UUID,
    current_user: User = Depends(require_roles(Role.PG_OWNER)),
    db: Session = Depends(get_db),
) -> PGPhoto:
    listing = get_owner_listing_or_404(db, current_user, pg_id)
    ensure_owner_can_edit(listing)
    photo = db.scalar(select(PGPhoto).where(PGPhoto.id == photo_id, PGPhoto.pg_id == listing.id))
    if photo is None:
        raise HTTPException(status_code=404, detail="Photo not found.")
    set_primary_photo(db, listing, photo)
    db.commit()
    db.refresh(photo)
    return photo
