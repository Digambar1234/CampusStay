from urllib.parse import urlencode
from urllib.request import Request, urlopen

from fastapi import HTTPException, status

from app.core.config import get_settings


def send_login_otp(phone: str, code: str) -> None:
    settings = get_settings()
    provider = (settings.sms_provider or "").lower()
    if provider == "fast2sms":
        if not settings.fast2sms_api_key:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SMS provider is not configured.")
        number = phone.removeprefix("+91")
        body = urlencode({"route": "otp", "variables_values": code, "numbers": number}).encode()
        request = Request(
            "https://www.fast2sms.com/dev/bulkV2",
            data=body,
            headers={"authorization": settings.fast2sms_api_key, "Content-Type": "application/x-www-form-urlencoded"},
            method="POST",
        )
        try:
            with urlopen(request, timeout=10) as response:
                if response.status >= 400:
                    raise RuntimeError("SMS provider rejected the OTP request.")
        except Exception as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not send OTP SMS.") from exc
        return

    if settings.is_production:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="SMS provider is not configured.")
