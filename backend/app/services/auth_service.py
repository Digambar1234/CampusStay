import hashlib
import hmac
import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models import CreditTransaction, CreditWallet, LoginOtp, PGOwnerProfile, StudentProfile, User
from app.models.enums import ContactUnlockTransactionType, Role
from app.schemas.auth import AuthResponse, LoginOtpStartRequest, LoginOtpStartResponse, LoginOtpVerifyRequest, LoginRequest, RegisterRequest, UserResponse
from app.services.sms_service import send_login_otp
from app.utils.phone import normalize_indian_phone

PUBLIC_REGISTRATION_ROLES = {Role.STUDENT, Role.PG_OWNER}
SIGNUP_BONUS_CREDITS = 10
OTP_ATTEMPT_LIMIT = 5
logger = logging.getLogger(__name__)


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


def _hash_otp(phone: str, code: str) -> str:
    settings = get_settings()
    return hmac.new(settings.jwt_secret_key.encode(), f"{phone}:{code}".encode(), hashlib.sha256).hexdigest()


def _otp_phone_hint(phone: str) -> str:
    if len(phone) <= 4:
        return phone
    return f"{'*' * max(0, len(phone) - 4)}{phone[-4:]}"


def start_password_otp_login(db: Session, payload: LoginOtpStartRequest) -> LoginOtpStartResponse:
    settings = get_settings()
    user = db.scalar(select(User).where(User.email == payload.email.lower()))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password.")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="This account is inactive.")
    if not user.phone:
        settings = get_settings()
        logger.error(
            "login_otp_sms_failure reason=user_mobile_missing sms_provider=%s fast2sms_api_key_present=%s user_has_mobile=%s target_mobile=%s",
            settings.sms_provider or "",
            bool(settings.fast2sms_api_key),
            False,
            "missing",
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No mobile number is linked to this account.")

    code = f"{secrets.randbelow(900000) + 100000}"
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.login_otp_ttl_minutes)
    challenge = LoginOtp(
        user_id=user.id,
        phone=user.phone,
        code_hash=_hash_otp(user.phone, code),
        expires_at=expires_at,
    )
    db.add(challenge)
    db.commit()
    db.refresh(challenge)

    send_login_otp(user.phone, code)
    return LoginOtpStartResponse(
        challenge_id=str(challenge.id),
        phone_hint=_otp_phone_hint(user.phone),
        expires_in_seconds=settings.login_otp_ttl_minutes * 60,
        dev_otp=None if settings.is_production or settings.sms_provider else code,
    )


def verify_password_otp_login(db: Session, payload: LoginOtpVerifyRequest) -> AuthResponse:
    try:
        challenge_id = uuid.UUID(payload.challenge_id)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Invalid OTP challenge.") from exc

    challenge = db.scalar(select(LoginOtp).where(LoginOtp.id == challenge_id).with_for_update())
    if challenge is None or challenge.consumed_at is not None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP.")
    now = datetime.now(timezone.utc)
    expires_at = challenge.expires_at if challenge.expires_at.tzinfo else challenge.expires_at.replace(tzinfo=timezone.utc)
    if expires_at < now:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP.")
    if challenge.attempts >= OTP_ATTEMPT_LIMIT:
        raise HTTPException(status_code=status.HTTP_429_TOO_MANY_REQUESTS, detail="Too many OTP attempts.")

    challenge.attempts += 1
    if not hmac.compare_digest(challenge.code_hash, _hash_otp(challenge.phone, payload.otp)):
        db.commit()
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid OTP.")

    user = db.get(User, challenge.user_id)
    if user is None or not user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired OTP.")

    challenge.consumed_at = now
    user.is_verified = True
    db.commit()
    return build_auth_response(user)
