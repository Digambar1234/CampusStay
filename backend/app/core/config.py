from functools import lru_cache

from pydantic import AnyHttpUrl, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    database_url: str = Field(..., alias="DATABASE_URL")
    jwt_secret_key: str = Field(..., alias="JWT_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    access_token_expire_minutes: int = Field(default=60, alias="ACCESS_TOKEN_EXPIRE_MINUTES")
    frontend_origin: AnyHttpUrl | str = Field(default="http://localhost:3000", alias="FRONTEND_ORIGIN")
    frontend_origins: str | None = Field(default=None, alias="FRONTEND_ORIGINS")
    environment: str = Field(default="development", alias="ENVIRONMENT")

    admin_email: str | None = Field(default=None, alias="ADMIN_EMAIL")
    admin_password: str | None = Field(default=None, alias="ADMIN_PASSWORD")
    admin_full_name: str | None = Field(default=None, alias="ADMIN_FULL_NAME")

    cloudinary_cloud_name: str | None = Field(default=None, alias="CLOUDINARY_CLOUD_NAME")
    cloudinary_api_key: str | None = Field(default=None, alias="CLOUDINARY_API_KEY")
    cloudinary_api_secret: str | None = Field(default=None, alias="CLOUDINARY_API_SECRET")

    razorpay_key_id: str | None = Field(default=None, alias="RAZORPAY_KEY_ID")
    razorpay_key_secret: str | None = Field(default=None, alias="RAZORPAY_KEY_SECRET")
    allow_test_credit_purchase: bool = Field(default=False, alias="ALLOW_TEST_CREDIT_PURCHASE")
    credit_pack_price_rupees: int = Field(default=10, alias="CREDIT_PACK_PRICE_RUPEES")
    credit_pack_amount: int = Field(default=10, alias="CREDIT_PACK_AMOUNT")
    login_otp_ttl_minutes: int = Field(default=5, alias="LOGIN_OTP_TTL_MINUTES")
    sms_provider: str | None = Field(default=None, alias="SMS_PROVIDER")
    fast2sms_api_key: str | None = Field(default=None, alias="FAST2SMS_API_KEY")

    @property
    def allowed_origins(self) -> list[str]:
        if self.frontend_origins:
            return [origin.strip() for origin in self.frontend_origins.split(",") if origin.strip()]
        return [str(self.frontend_origin)]

    @property
    def is_production(self) -> bool:
        return self.environment.lower() == "production"


@lru_cache
def get_settings() -> Settings:
    return Settings()
