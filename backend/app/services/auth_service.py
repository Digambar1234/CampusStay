from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import CreditTransaction, CreditWallet, PGOwnerProfile, StudentProfile, User
from app.models.enums import ContactUnlockTransactionType, Role
from app.schemas.auth import AuthResponse, LoginRequest, RegisterRequest, UserResponse
from app.utils.phone import normalize_indian_phone

PUBLIC_REGISTRATION_ROLES = {Role.STUDENT, Role.PG_OWNER}
SIGNUP_BONUS_CREDITS = 10


def serialize_user(user: User) -> UserResponse:
    return UserResponse(
        id=str(user.id),
        full_name=user.full_name,
        email=user.email,
        phone=user.phone,
        role=user.role,
        is_active=user.is_active,
        is_verified=user.is_verified,
        created_at=user.created_at,
    )


def build_auth_response(user: User) -> AuthResponse:
    token = create_access_token(subject=str(user.id), extra_claims={"role": user.role.value})
    return AuthResponse(access_token=token, user=serialize_user(user))


def register_user(db: Session, payload: RegisterRequest) -> AuthResponse:
    if payload.role not in PUBLIC_REGISTRATION_ROLES:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Public registration is available only for students and PG owners.",
        )

    normalized_email = payload.email.lower()
    try:
        normalized_phone = normalize_indian_phone(payload.phone)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc))
    duplicate_query = select(User).where(
        or_(
            User.email == normalized_email,
            User.phone == normalized_phone if normalized_phone else False,
        )
    )
    if db.scalar(duplicate_query):
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email or phone is already registered.")

    user = User(
        full_name=payload.full_name.strip(),
        email=normalized_email,
        phone=normalized_phone,
        password_hash=get_password_hash(payload.password),
        role=payload.role,
    )
    db.add(user)
    db.flush()

    if payload.role == Role.STUDENT:
        db.add(StudentProfile(user_id=user.id))
        db.add(CreditWallet(student_id=user.id, balance=SIGNUP_BONUS_CREDITS))
        db.add(
            CreditTransaction(
                student_id=user.id,
                type=ContactUnlockTransactionType.FREE_SIGNUP_BONUS,
                amount=SIGNUP_BONUS_CREDITS,
                reason="Signup bonus credits",
            )
        )
    elif payload.role == Role.PG_OWNER:
        db.add(PGOwnerProfile(user_id=user.id))

    db.commit()
    db.refresh(user)
    return build_auth_response(user)


def authenticate_user(db: Session, payload: LoginRequest) -> AuthResponse:
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive.")
    return build_auth_response(user)
