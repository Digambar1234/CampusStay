from enum import StrEnum


class Role(StrEnum):
    STUDENT = "student"
    PG_OWNER = "pg_owner"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"


class GenderAllowed(StrEnum):
    BOYS = "boys"
    GIRLS = "girls"
    CO_LIVING = "co_living"


class ListingStatus(StrEnum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"


class RoomType(StrEnum):
    SINGLE = "single"
    DOUBLE_SHARING = "double_sharing"
    TRIPLE_SHARING = "triple_sharing"
    FOUR_SHARING = "four_sharing"
    DORMITORY = "dormitory"


class ImageType(StrEnum):
    ROOM = "room"
    WASHROOM = "washroom"
    BUILDING = "building"
    MESS = "mess"
    COMMON_AREA = "common_area"
    OTHER = "other"


class ContactUnlockTransactionType(StrEnum):
    FREE_SIGNUP_BONUS = "free_signup_bonus"
    PURCHASE = "purchase"
    CONTACT_UNLOCK = "contact_unlock"
    REFUND = "refund"
    ADMIN_ADJUSTMENT = "admin_adjustment"


class PaymentProvider(StrEnum):
    RAZORPAY = "razorpay"


class PaymentStatus(StrEnum):
    CREATED = "created"
    PAID = "paid"
    FAILED = "failed"
    REFUNDED = "refunded"


class ReportStatus(StrEnum):
    OPEN = "open"
    REVIEWED = "reviewed"
    RESOLVED = "resolved"
    REJECTED = "rejected"


class ReviewStatus(StrEnum):
    PENDING = "pending"
    APPROVED = "approved"
    HIDDEN = "hidden"
    REJECTED = "rejected"


class ReportType(StrEnum):
    FAKE_LISTING = "fake_listing"
    WRONG_PRICE = "wrong_price"
    WRONG_PHONE = "wrong_phone"
    ROOM_NOT_AVAILABLE = "room_not_available"
    MISLEADING_PHOTOS = "misleading_photos"
    ABUSIVE_OWNER = "abusive_owner"
    OTHER = "other"


class ReportPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class FeaturedListingStatus(StrEnum):
    ACTIVE = "active"
    EXPIRED = "expired"
    CANCELLED = "cancelled"
    PENDING = "pending"


class FeaturedListingSource(StrEnum):
    ADMIN_GRANT = "admin_grant"
    PAID = "paid"
