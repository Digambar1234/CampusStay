import uuid

from fastapi import HTTPException, status
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.models import AdminActionLog, PGListing, PGPhoto, PGRoom, User
from app.models.enums import ListingStatus


EDITABLE_OWNER_STATUSES = {ListingStatus.DRAFT, ListingStatus.PENDING_REVIEW, ListingStatus.REJECTED}
DELETABLE_OWNER_STATUSES = {ListingStatus.DRAFT, ListingStatus.REJECTED}


def get_owner_listing_or_404(db: Session, owner: User, pg_id: uuid.UUID) -> PGListing:
    listing = db.scalar(
        select(PGListing)
        .options(selectinload(PGListing.rooms), selectinload(PGListing.photos))
        .where(PGListing.id == pg_id, PGListing.owner_id == owner.id)
    )
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PG listing not found.")
    return listing


def get_listing_or_404(db: Session, pg_id: uuid.UUID) -> PGListing:
    listing = db.scalar(
        select(PGListing)
        .options(selectinload(PGListing.rooms), selectinload(PGListing.photos), selectinload(PGListing.owner))
        .where(PGListing.id == pg_id)
    )
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PG listing not found.")
    return listing


def ensure_owner_can_edit(listing: PGListing) -> None:
    if listing.status == ListingStatus.APPROVED:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Approved listings cannot be edited directly. Request admin change flow will be added later.",
        )
    if listing.status not in EDITABLE_OWNER_STATUSES:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=f"Listings with status {listing.status.value} cannot be edited.")


def ensure_owner_can_delete(listing: PGListing) -> None:
    if listing.status not in DELETABLE_OWNER_STATUSES:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Only draft or rejected listings can be deleted.")


def validate_listing_ready_for_review(listing: PGListing) -> None:
    errors: list[str] = []
    required_fields = {
        "PG name": listing.pg_name,
        "Address": listing.address,
        "Gender allowed": listing.gender_allowed,
        "Owner phone": listing.owner_phone,
    }
    for label, value in required_fields.items():
        if value is None or value == "":
            errors.append(f"{label} is required.")
    if not listing.rooms:
        errors.append("At least one room is required before submission.")
    if not listing.photos:
        errors.append("At least one photo is required before submission.")
    if errors:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=errors)


def set_primary_photo(db: Session, listing: PGListing, photo: PGPhoto) -> PGPhoto:
    for existing_photo in listing.photos:
        existing_photo.is_primary = existing_photo.id == photo.id
    db.flush()
    return photo


def log_admin_action(
    db: Session,
    admin: User,
    action: str,
    listing: PGListing,
    metadata: dict | None = None,
) -> None:
    db.add(
        AdminActionLog(
            admin_id=admin.id,
            action=action,
            target_type="pg_listing",
            target_id=str(listing.id),
            metadata_json=metadata,
        )
    )


def listing_counts(db: Session, owner_id: uuid.UUID | None = None) -> dict[ListingStatus, int]:
    query = select(PGListing.status, func.count(PGListing.id)).group_by(PGListing.status)
    if owner_id:
        query = query.where(PGListing.owner_id == owner_id)
    return {status_value: count for status_value, count in db.execute(query).all()}
