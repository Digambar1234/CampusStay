from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.enums import ContactUnlockTransactionType, PaymentStatus


class CreditWalletResponse(BaseModel):
    student_id: UUID
    balance: int
    total_purchased_credits: int
    total_used_credits: int
    signup_bonus_credits: int
    created_at: datetime
    updated_at: datetime


class CreditTransactionResponse(BaseModel):
    id: UUID
    type: ContactUnlockTransactionType
    amount: int
    reason: str | None
    created_at: datetime


class CreditTransactionListResponse(BaseModel):
    items: list[CreditTransactionResponse]
    total: int
    page: int
    page_size: int


class UnlockContactResponse(BaseModel):
    pg_id: UUID
    pg_name: str
    owner_phone: str
    whatsapp_number: str | None
    already_unlocked: bool
    credits_used: int
    remaining_balance: int


class UnlockStatusResponse(BaseModel):
    pg_id: UUID
    is_unlocked: bool
    wallet_balance: int
    can_unlock: bool
    reason: str | None = None


class UnlockedContactResponse(BaseModel):
    pg_id: UUID
    pg_name: str
    address: str
    distance_from_lpu_km: Decimal | None
    monthly_rent_min: int | None
    monthly_rent_max: int | None
    owner_phone: str
    whatsapp_number: str | None
    primary_photo_url: str | None
    unlocked_at: datetime


class CreateCreditOrderRequest(BaseModel):
    pack: str = Field(default="credits_10")


class CreateCreditOrderResponse(BaseModel):
    order_id: str
    amount_rupees: int
    amount_paise: int
    credits: int
    currency: str = "INR"
    razorpay_key_id: str


class VerifyPaymentRequest(BaseModel):
    razorpay_order_id: str
    razorpay_payment_id: str
    razorpay_signature: str


class VerifyPaymentResponse(BaseModel):
    payment_status: PaymentStatus
    wallet_balance: int
    credits_added: int
    already_verified: bool = False
