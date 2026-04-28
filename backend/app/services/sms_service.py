import json
import logging
from urllib.parse import urlencode
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from fastapi import HTTPException, status

from app.core.config import get_settings

logger = logging.getLogger(__name__)


def _mask_phone(phone: str | None) -> str:
    if not phone:
        return "missing"
    digits = "".join(char for char in phone if char.isdigit())
    if digits.startswith("91") and len(digits) > 10:
        digits = digits[-10:]
    if len(digits) <= 4:
        return "*" * len(digits)
    return f"{digits[:2]}{'*' * max(0, len(digits) - 4)}{digits[-2:]}"


def _log_sms_failure(reason: str, phone: str | None, **extra: object) -> None:
    settings = get_settings()
    logger.error(
        "login_otp_sms_failure reason=%s sms_provider=%s fast2sms_api_key_present=%s user_has_mobile=%s target_mobile=%s %s",
        reason,
        settings.sms_provider or "",
        bool(settings.fast2sms_api_key),
        bool(phone),
        _mask_phone(phone),
        " ".join(f"{key}={value!r}" for key, value in extra.items()),
    )


def send_login_otp(phone: str, code: str) -> None:
    settings = get_settings()
    provider = (settings.sms_provider or "").lower()
    if provider == "fast2sms":
        if not settings.fast2sms_api_key:
            _log_sms_failure("missing_fast2sms_api_key", phone)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not send OTP SMS.")
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
                response_body = response.read().decode("utf-8", errors="replace")
                if response.status >= 400:
                    _log_sms_failure("fast2sms_http_error", phone, http_status=response.status, response_body=response_body)
                    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not send OTP SMS.")
                try:
                    payload = json.loads(response_body)
                except json.JSONDecodeError:
                    payload = {}
                if payload.get("return") is False or payload.get("status") is False:
                    _log_sms_failure("fast2sms_provider_rejected", phone, http_status=response.status, response_body=response_body)
                    raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not send OTP SMS.")
        except HTTPException:
            raise
        except HTTPError as exc:
            response_body = exc.read().decode("utf-8", errors="replace")
            _log_sms_failure("fast2sms_http_error", phone, http_status=exc.code, response_body=response_body)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not send OTP SMS.") from exc
        except URLError as exc:
            _log_sms_failure("fast2sms_network_error", phone, error=str(exc.reason))
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not send OTP SMS.") from exc
        except Exception as exc:
            _log_sms_failure("fast2sms_unexpected_error", phone, error=type(exc).__name__)
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not send OTP SMS.") from exc
        return

    if settings.is_production:
        _log_sms_failure("sms_provider_not_configured", phone)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="Could not send OTP SMS.")
