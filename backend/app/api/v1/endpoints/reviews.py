import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies.auth import require_roles
from app.models import AdminActionLog, ContactUnlock, PGListing, Review, User
from app.models.enums import ListingStatus, ReviewStatus, Role
from app.schemas.trust import AdminReviewResponse, PublicReviewResponse, ReviewCreate, ReviewListResponse, ReviewUpdate, StudentReviewResponse
from app.services.pg_service import log_admin_action
from app.core.rate_limit import limiter

router = APIRouter(prefix="/reviews", tags=["reviews"])
student_router = APIRouter(prefix="/student/reviews", tags=["student-reviews"])
admin_router = APIRouter(prefix="/admin/reviews", tags=["admin-reviews"])


def _public_review(review: Review) -> PublicReviewResponse:
    first = review.student.full_name.split()[0] if review.student and review.student.full_name else "Student"
    return PublicReviewResponse(
        id=review.id, pg_id=review.pg_id, rating=review.rating, title=review.title, comment=review.comment,
        status=review.status, is_edited=review.is_edited, reviewer_name=first, created_at=review.created_at, updated_at=review.updated_at,
    )


@router.get("/pg/{pg_id}", response_model=ReviewListResponse)
def get_pg_reviews(pg_id: uuid.UUID, db: Session = Depends(get_db)) -> ReviewListResponse:
    listing = db.scalar(select(PGListing).where(PGListing.id == pg_id, PGListing.status == ListingStatus.APPROVED, PGListing.admin_verified.is_(True)))
    if not listing:
        raise HTTPException(status_code=404, detail="PG listing not found.")
    reviews = db.scalars(select(Review).options(selectinload(Review.student)).where(Review.pg_id == pg_id, Review.status == ReviewStatus.APPROVED).order_by(Review.created_at.desc())).all()
    avg = db.scalar(select(func.avg(Review.rating)).where(Review.pg_id == pg_id, Review.status == ReviewStatus.APPROVED))
    return ReviewListResponse(items=[_public_review(r) for r in reviews], total=len(reviews), average_rating=round(float(avg), 2) if avg else None)


@router.post("/pg/{pg_id}", response_model=StudentReviewResponse, status_code=201)
@limiter.limit("5/minute")
def create_review(request: Request, pg_id: uuid.UUID, payload: ReviewCreate, user: User = Depends(require_roles(Role.STUDENT)), db: Session = Depends(get_db)) -> StudentReviewResponse:
    listing = db.scalar(select(PGListing).where(PGListing.id == pg_id, PGListing.status == ListingStatus.APPROVED, PGListing.admin_verified.is_(True)))
    if not listing:
        raise HTTPException(status_code=404, detail="PG listing not found.")
    unlocked = db.scalar(select(ContactUnlock).where(ContactUnlock.student_id == user.id, ContactUnlock.pg_id == pg_id))
    if not unlocked:
        raise HTTPException(status_code=403, detail="Unlock this PG contact before leaving a review.")
    review = Review(student_id=user.id, pg_id=pg_id, **payload.model_dump())
    db.add(review)
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="You have already reviewed this PG.")
    db.refresh(review)
    return StudentReviewResponse(**_public_review(review).model_dump(), pg_name=listing.pg_name)


@router.patch("/{review_id}", response_model=StudentReviewResponse)
def update_review(review_id: uuid.UUID, payload: ReviewUpdate, user: User = Depends(require_roles(Role.STUDENT)), db: Session = Depends(get_db)) -> StudentReviewResponse:
    review = db.scalar(select(Review).options(selectinload(Review.pg), selectinload(Review.student)).where(Review.id == review_id, Review.student_id == user.id))
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(review, key, value)
    review.is_edited = True
    db.commit()
    db.refresh(review)
    return StudentReviewResponse(**_public_review(review).model_dump(), pg_name=review.pg.pg_name)


@router.delete("/{review_id}")
def delete_review(review_id: uuid.UUID, user: User = Depends(require_roles(Role.STUDENT)), db: Session = Depends(get_db)) -> dict:
    review = db.scalar(select(Review).where(Review.id == review_id, Review.student_id == user.id))
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    review.status = ReviewStatus.HIDDEN
    db.commit()
    return {"message": "Review hidden."}


@student_router.get("", response_model=list[StudentReviewResponse])
def my_reviews(user: User = Depends(require_roles(Role.STUDENT)), db: Session = Depends(get_db)) -> list[StudentReviewResponse]:
    reviews = db.scalars(select(Review).options(selectinload(Review.pg), selectinload(Review.student)).where(Review.student_id == user.id).order_by(Review.created_at.desc())).all()
    return [StudentReviewResponse(**_public_review(r).model_dump(), pg_name=r.pg.pg_name) for r in reviews]


@admin_router.get("", response_model=list[AdminReviewResponse])
def admin_reviews(status_filter: ReviewStatus | None = Query(default=None, alias="status"), rating: int | None = Query(default=None, ge=1, le=5), search: str | None = None, _: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> list[AdminReviewResponse]:
    query = select(Review).options(selectinload(Review.pg), selectinload(Review.student))
    if status_filter:
        query = query.where(Review.status == status_filter)
    if rating:
        query = query.where(Review.rating == rating)
    if search:
        term = f"%{search}%"
        query = query.join(PGListing).join(User, Review.student_id == User.id).where(or_(PGListing.pg_name.ilike(term), User.email.ilike(term), Review.comment.ilike(term)))
    reviews = db.scalars(query.order_by(Review.created_at.desc())).all()
    return [AdminReviewResponse(**_public_review(r).model_dump(), pg_name=r.pg.pg_name, student_name=r.student.full_name, student_email=r.student.email) for r in reviews]


def _moderate(review_id: uuid.UUID, new_status: ReviewStatus, admin: User, db: Session) -> dict:
    review = db.scalar(select(Review).options(selectinload(Review.pg)).where(Review.id == review_id))
    if not review:
        raise HTTPException(status_code=404, detail="Review not found.")
    review.status = new_status
    db.add(AdminActionLog(admin_id=admin.id, action=f"review_{new_status.value}", target_type="review", target_id=str(review.id), metadata_json={"pg_id": str(review.pg_id)}))
    db.commit()
    return {"message": f"Review {new_status.value}."}


@admin_router.post("/{review_id}/hide")
def hide_review(review_id: uuid.UUID, admin: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> dict:
    return _moderate(review_id, ReviewStatus.HIDDEN, admin, db)


@admin_router.post("/{review_id}/approve")
def approve_review(review_id: uuid.UUID, admin: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> dict:
    return _moderate(review_id, ReviewStatus.APPROVED, admin, db)


@admin_router.post("/{review_id}/reject")
def reject_review(review_id: uuid.UUID, admin: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> dict:
    return _moderate(review_id, ReviewStatus.REJECTED, admin, db)
