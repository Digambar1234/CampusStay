from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.dependencies.auth import get_current_user
from app.models import User
from app.schemas.auth import AuthResponse, LoginOtpStartRequest, LoginOtpStartResponse, LoginOtpVerifyRequest, LoginRequest, RegisterRequest, UserResponse
from app.services.auth_service import authenticate_user, register_user, serialize_user, start_password_otp_login, verify_password_otp_login
from app.core.rate_limit import limiter

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=AuthResponse, status_code=201)
@limiter.limit("3/minute")
def register(request: Request, payload: RegisterRequest, db: Session = Depends(get_db)) -> AuthResponse:
    return register_user(db, payload)


@router.post("/login", response_model=AuthResponse)
@limiter.limit("5/minute")
def login(request: Request, payload: LoginRequest, db: Session = Depends(get_db)) -> AuthResponse:
    return authenticate_user(db, payload)


@router.post("/login/start", response_model=LoginOtpStartResponse)
@limiter.limit("5/minute")
def login_start(request: Request, payload: LoginOtpStartRequest, db: Session = Depends(get_db)) -> LoginOtpStartResponse:
    return start_password_otp_login(db, payload)


@router.post("/login/verify-otp", response_model=AuthResponse)
@limiter.limit("10/minute")
def login_verify_otp(request: Request, payload: LoginOtpVerifyRequest, db: Session = Depends(get_db)) -> AuthResponse:
    return verify_password_otp_login(db, payload)


@router.get("/me", response_model=UserResponse)
def me(current_user: User = Depends(get_current_user)) -> UserResponse:
    return serialize_user(current_user)
