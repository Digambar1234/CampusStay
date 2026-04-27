import uuid

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, selectinload

from app.core.config import get_settings
from app.db.session import get_db
from app.dependencies.auth import require_roles
from app.models import ContactUnlock, CreditTransaction, CreditWallet, Payment, PGListing, PGPhoto, User
from app.models.enums import ContactUnlockTransactionType, ListingStatus, PaymentProvider, PaymentStatus, Role
from app.schemas.credit import (
    CreateCreditOrderRequest,
    CreateCreditOrderResponse,
    CreditTransactionListResponse,
    CreditTransactionResponse,
    CreditWalletResponse,
    UnlockContactResponse,
    UnlockedContactResponse,
    UnlockStatusResponse,
    VerifyPaymentRequest,
    VerifyPaymentResponse,
)
from app.services.razorpay_service import create_order, verify_payment_signature
from app.core.rate_limit import limiter

router = APIRouter(prefix="/credits", tags=["credits"])


def _get_wallet_or_404(db: Session, student: User) -> CreditWallet:
    wallet = db.scalar(select(CreditWallet).where(CreditWallet.student_id == student.id))
    if wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credit wallet not found.")
    return wallet


def _approved_pg_or_404(db: Session, pg_id: uuid.UUID) -> PGListing:
    listing = db.scalar(
        select(PGListing)
        .options(selectinload(PGListing.photos), selectinload(PGListing.rooms))
        .where(PGListing.id == pg_id, PGListing.status == ListingStatus.APPROVED, PGListing.admin_verified.is_(True))
    )
    if listing is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="PG listing not found.")
    return listing


def _wallet_response(db: Session, wallet: CreditWallet) -> CreditWalletResponse:
    totals = dict(
        db.execute(
            select(CreditTransaction.type, func.coalesce(func.sum(CreditTransaction.amount), 0))
            .where(CreditTransaction.student_id == wallet.student_id)
            .group_by(CreditTransaction.type)
        ).all()
    )
    return CreditWalletResponse(
        student_id=wallet.student_id,
        balance=wallet.balance,
        total_purchased_credits=max(0, totals.get(ContactUnlockTransactionType.PURCHASE, 0)),
        total_used_credits=abs(min(0, totals.get(ContactUnlockTransactionType.CONTACT_UNLOCK, 0))),
        signup_bonus_credits=max(0, totals.get(ContactUnlockTransactionType.FREE_SIGNUP_BONUS, 0)),
        created_at=wallet.created_at,
        updated_at=wallet.updated_at,
    )


@router.get("/wallet", response_model=CreditWalletResponse)
def get_wallet(
    current_user: User = Depends(require_roles(Role.STUDENT)),
    db: Session = Depends(get_db),
) -> CreditWalletResponse:
    return _wallet_response(db, _get_wallet_or_404(db, current_user))


@router.get("/transactions", response_model=CreditTransactionListResponse)
def get_transactions(
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
    current_user: User = Depends(require_roles(Role.STUDENT)),
    db: Session = Depends(get_db),
) -> CreditTransactionListResponse:
    query = select(CreditTransaction).where(CreditTransaction.student_id == current_user.id)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    transactions = db.scalars(
        query.order_by(CreditTransaction.created_at.desc()).offset((page - 1) * page_size).limit(page_size)
    ).all()
    return CreditTransactionListResponse(
        items=[
            CreditTransactionResponse(
                id=tx.id,
                type=tx.type,
                amount=tx.amount,
                reason=tx.reason,
                created_at=tx.created_at,
            )
            for tx in transactions
        ],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/unlock-status/{pg_id}", response_model=UnlockStatusResponse)
def get_unlock_status(
    pg_id: uuid.UUID,
    current_user: User = Depends(require_roles(Role.STUDENT)),
    db: Session = Depends(get_db),
) -> UnlockStatusResponse:
    _approved_pg_or_404(db, pg_id)
    wallet = _get_wallet_or_404(db, current_user)
    unlocked = db.scalar(select(ContactUnlock).where(ContactUnlock.student_id == current_user.id, ContactUnlock.pg_id == pg_id))
    can_unlock = bool(unlocked) or wallet.balance > 0
    return UnlockStatusResponse(
        pg_id=pg_id,
        is_unlocked=unlocked is not None,
        wallet_balance=wallet.balance,
        can_unlock=can_unlock,
        reason=None if can_unlock else "INSUFFICIENT_CREDITS",
    )


@router.post("/unlock-contact/{pg_id}", response_model=UnlockContactResponse)
@limiter.limit("10/minute")
def unlock_contact(
    request: Request,
    pg_id: uuid.UUID,
    current_user: User = Depends(require_roles(Role.STUDENT)),
    db: Session = Depends(get_db),
) -> UnlockContactResponse:
    listing = _approved_pg_or_404(db, pg_id)
    existing_unlock = db.scalar(
        select(ContactUnlock).where(ContactUnlock.student_id == current_user.id, ContactUnlock.pg_id == listing.id)
    )
    wallet = _get_wallet_or_404(db, current_user)
    if existing_unlock:
        return UnlockContactResponse(
            pg_id=listing.id,
            pg_name=listing.pg_name,
            owner_phone=listing.owner_phone,
            whatsapp_number=listing.whatsapp_number,
            already_unlocked=True,
            credits_used=0,
            remaining_balance=wallet.balance,
        )

    locked_wallet = db.scalar(select(CreditWallet).where(CreditWallet.student_id == current_user.id).with_for_update())
    if locked_wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credit wallet not found.")
    if locked_wallet.balance <= 0:
        raise HTTPException(
            status_code=status.HTTP_402_PAYMENT_REQUIRED,
            detail={"code": "INSUFFICIENT_CREDITS", "message": "You do not have enough credits."},
        )

    locked_wallet.balance -= 1
    db.add(ContactUnlock(student_id=current_user.id, pg_id=listing.id, credits_used=1))
    db.add(
        CreditTransaction(
            student_id=current_user.id,
            type=ContactUnlockTransactionType.CONTACT_UNLOCK,
            amount=-1,
            reason=f"Unlocked contact for PG: {listing.pg_name}",
        )
    )
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        wallet_after_race = _get_wallet_or_404(db, current_user)
        return UnlockContactResponse(
            pg_id=listing.id,
            pg_name=listing.pg_name,
            owner_phone=listing.owner_phone,
            whatsapp_number=listing.whatsapp_number,
            already_unlocked=True,
            credits_used=0,
            remaining_balance=wallet_after_race.balance,
        )
    db.refresh(locked_wallet)
    return UnlockContactResponse(
        pg_id=listing.id,
        pg_name=listing.pg_name,
        owner_phone=listing.owner_phone,
        whatsapp_number=listing.whatsapp_number,
        already_unlocked=False,
        credits_used=1,
        remaining_balance=locked_wallet.balance,
    )


@router.get("/unlocked-contacts", response_model=list[UnlockedContactResponse])
def get_unlocked_contacts(
    current_user: User = Depends(require_roles(Role.STUDENT)),
    db: Session = Depends(get_db),
) -> list[UnlockedContactResponse]:
    unlocks = db.scalars(
        select(ContactUnlock)
        .options(selectinload(ContactUnlock.pg).selectinload(PGListing.photos))
        .join(PGListing, PGListing.id == ContactUnlock.pg_id)
        .where(
            ContactUnlock.student_id == current_user.id,
            PGListing.status == ListingStatus.APPROVED,
            PGListing.admin_verified.is_(True),
        )
        .order_by(ContactUnlock.created_at.desc())
    ).all()
    response: list[UnlockedContactResponse] = []
    for unlock in unlocks:
        listing = unlock.pg
        primary = next((photo for photo in listing.photos if photo.is_primary), None) or (listing.photos[0] if listing.photos else None)
        response.append(
            UnlockedContactResponse(
                pg_id=listing.id,
                pg_name=listing.pg_name,
                address=listing.address,
                distance_from_lpu_km=listing.distance_from_lpu_km,
                monthly_rent_min=listing.monthly_rent_min,
                monthly_rent_max=listing.monthly_rent_max,
                owner_phone=listing.owner_phone,
                whatsapp_number=listing.whatsapp_number,
                primary_photo_url=primary.image_url if primary else None,
                unlocked_at=unlock.created_at,
            )
        )
    return response


@router.post("/create-order", response_model=CreateCreditOrderResponse)
@limiter.limit("5/minute")
def create_credit_order(
    request: Request,
    payload: CreateCreditOrderRequest,
    current_user: User = Depends(require_roles(Role.STUDENT)),
    db: Session = Depends(get_db),
) -> CreateCreditOrderResponse:
    settings = get_settings()
    if payload.pack != "credits_10":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported credit pack.")
    amount_rupees = settings.credit_pack_price_rupees
    credits = settings.credit_pack_amount
    amount_paise = amount_rupees * 100
    order = create_order(amount_paise=amount_paise, receipt=f"cr-{current_user.id.hex[:24]}")
    payment = Payment(
        student_id=current_user.id,
        provider=PaymentProvider.RAZORPAY,
        provider_order_id=order["id"],
        amount_rupees=amount_rupees,
        credits_purchased=credits,
        status=PaymentStatus.CREATED,
    )
    db.add(payment)
    db.commit()
    return CreateCreditOrderResponse(
        order_id=order["id"],
        amount_rupees=amount_rupees,
        amount_paise=amount_paise,
        credits=credits,
        razorpay_key_id=settings.razorpay_key_id or "",
    )


@router.post("/verify-payment", response_model=VerifyPaymentResponse)
@limiter.limit("10/minute")
def verify_credit_payment(
    request: Request,
    payload: VerifyPaymentRequest,
    current_user: User = Depends(require_roles(Role.STUDENT)),
    db: Session = Depends(get_db),
) -> VerifyPaymentResponse:
    payment = db.scalar(
        select(Payment)
        .where(Payment.provider_order_id == payload.razorpay_order_id, Payment.student_id == current_user.id)
        .with_for_update()
    )
    if payment is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Payment order not found.")

    wallet = db.scalar(select(CreditWallet).where(CreditWallet.student_id == current_user.id).with_for_update())
    if wallet is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Credit wallet not found.")

    if payment.status == PaymentStatus.PAID:
        return VerifyPaymentResponse(
            payment_status=payment.status,
            wallet_balance=wallet.balance,
            credits_added=0,
            already_verified=True,
        )

    is_valid = verify_payment_signature(
        order_id=payload.razorpay_order_id,
        payment_id=payload.razorpay_payment_id,
        signature=payload.razorpay_signature,
    )
    if not is_valid:
        payment.status = PaymentStatus.FAILED
        payment.provider_payment_id = payload.razorpay_payment_id
        db.commit()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid Razorpay payment signature.")

    payment.status = PaymentStatus.PAID
    payment.provider_payment_id = payload.razorpay_payment_id
    wallet.balance += payment.credits_purchased
    db.add(
        CreditTransaction(
            student_id=current_user.id,
            type=ContactUnlockTransactionType.PURCHASE,
            amount=payment.credits_purchased,
            reason=f"Purchased {payment.credits_purchased} credits for ₹{payment.amount_rupees}",
        )
    )
    db.commit()
    db.refresh(wallet)
    return VerifyPaymentResponse(
        payment_status=payment.status,
        wallet_balance=wallet.balance,
        credits_added=payment.credits_purchased,
        already_verified=False,
    )
