from datetime import datetime
from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, model_validator

from app.models.enums import GenderAllowed, ImageType, ListingStatus, RoomType


class PGRoomCreate(BaseModel):
    room_type: RoomType
    price_per_month: int = Field(gt=0)
    available_beds: int = Field(default=0, ge=0)
    ac_available: bool = False
    attached_washroom: bool = False


class PGRoomUpdate(BaseModel):
    room_type: RoomType | None = None
    price_per_month: int | None = Field(default=None, gt=0)
    available_beds: int | None = Field(default=None, ge=0)
    ac_available: bool | None = None
    attached_washroom: bool | None = None


class PGRoomResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pg_id: UUID
    room_type: RoomType
    price_per_month: int
    available_beds: int
    ac_available: bool
    attached_washroom: bool
    created_at: datetime
    updated_at: datetime


class PGPhotoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    pg_id: UUID
    image_url: str
    public_id: str | None
    image_type: ImageType
    is_primary: bool
    created_at: datetime


class PGListingBase(BaseModel):
    pg_name: str = Field(min_length=2, max_length=180)
    description: str | None = None
    address: str = Field(min_length=5, max_length=500)
    landmark: str | None = Field(default=None, max_length=180)
    distance_from_lpu_km: Decimal | None = Field(default=None, ge=0, max_digits=5, decimal_places=2)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    gender_allowed: GenderAllowed
    food_available: bool = False
    wifi_available: bool = False
    ac_available: bool = False
    laundry_available: bool = False
    parking_available: bool = False
    security_available: bool = False
    monthly_rent_min: int | None = Field(default=None, ge=0)
    monthly_rent_max: int | None = Field(default=None, ge=0)
    deposit_amount: int | None = Field(default=None, ge=0)
    owner_phone: str = Field(min_length=7, max_length=30)
    whatsapp_number: str | None = Field(default=None, max_length=30)

    @model_validator(mode="after")
    def validate_rent_range(self) -> "PGListingBase":
        if self.monthly_rent_min is not None and self.monthly_rent_max is not None:
            if self.monthly_rent_min > self.monthly_rent_max:
                raise ValueError("Minimum rent cannot be greater than maximum rent.")
        return self


class PGListingCreate(PGListingBase):
    pass


class PGListingUpdate(BaseModel):
    pg_name: str | None = Field(default=None, min_length=2, max_length=180)
    description: str | None = None
    address: str | None = Field(default=None, min_length=5, max_length=500)
    landmark: str | None = Field(default=None, max_length=180)
    distance_from_lpu_km: Decimal | None = Field(default=None, ge=0, max_digits=5, decimal_places=2)
    latitude: Decimal | None = Field(default=None, ge=-90, le=90)
    longitude: Decimal | None = Field(default=None, ge=-180, le=180)
    gender_allowed: GenderAllowed | None = None
    food_available: bool | None = None
    wifi_available: bool | None = None
    ac_available: bool | None = None
    laundry_available: bool | None = None
    parking_available: bool | None = None
    security_available: bool | None = None
    monthly_rent_min: int | None = Field(default=None, ge=0)
    monthly_rent_max: int | None = Field(default=None, ge=0)
    deposit_amount: int | None = Field(default=None, ge=0)
    owner_phone: str | None = Field(default=None, min_length=7, max_length=30)
    whatsapp_number: str | None = Field(default=None, max_length=30)


class PGListingPublicResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    owner_id: UUID
    pg_name: str
    description: str | None
    address: str
    landmark: str | None
    distance_from_lpu_km: Decimal | None
    latitude: Decimal | None
    longitude: Decimal | None
    gender_allowed: GenderAllowed
    food_available: bool
    wifi_available: bool
    ac_available: bool
    laundry_available: bool
    parking_available: bool
    security_available: bool
    monthly_rent_min: int | None
    monthly_rent_max: int | None
    deposit_amount: int | None
    status: ListingStatus
    admin_verified: bool
    created_at: datetime
    updated_at: datetime
    rooms: list[PGRoomResponse] = []
    photos: list[PGPhotoResponse] = []
    average_rating: float | None = None
    review_count: int = 0
    is_featured: bool = False


class PGListingOwnerResponse(PGListingPublicResponse):
    owner_phone: str
    whatsapp_number: str | None


class OwnerInfoResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    full_name: str
    email: str
    phone: str | None


class PGListingAdminResponse(PGListingOwnerResponse):
    owner: OwnerInfoResponse


class PGListingSummaryResponse(BaseModel):
    id: UUID
    pg_name: str
    address: str
    distance_from_lpu_km: Decimal | None
    gender_allowed: GenderAllowed
    monthly_rent_min: int | None
    monthly_rent_max: int | None
    status: ListingStatus
    admin_verified: bool
    rooms_count: int
    photos_count: int
    primary_photo_url: str | None = None
    average_rating: float | None = None
    review_count: int = 0
    is_featured: bool = False
    created_at: datetime


class PaginatedPGResponse(BaseModel):
    items: list[PGListingPublicResponse]
    total: int
    page: int
    page_size: int


class PaginatedOwnerPGResponse(BaseModel):
    items: list[PGListingSummaryResponse]
    total: int


class PaginatedAdminPGResponse(BaseModel):
    items: list[PGListingAdminResponse]
    total: int
    page: int
    page_size: int


class AdminPGActionRequest(BaseModel):
    reason: str | None = None
    note: str | None = None


class AdminRejectRequest(BaseModel):
    reason: str = Field(min_length=3)


class AdminRequestChangesRequest(BaseModel):
    message: str = Field(min_length=3)


class SuccessResponse(BaseModel):
    message: str
