from pydantic import BaseModel, EmailStr, Field
from datetime import datetime

from app.models.enums import Role


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    phone: str | None = Field(default=None, max_length=30)
    password: str = Field(min_length=8, max_length=128)
    role: Role


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: str
    full_name: str
    email: EmailStr
    phone: str | None
    role: Role
    is_active: bool
    is_verified: bool
    created_at: datetime | None = None


class AuthResponse(TokenResponse):
    user: UserResponse
