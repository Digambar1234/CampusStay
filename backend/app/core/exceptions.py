from fastapi import FastAPI, HTTPException, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded
from sqlalchemy.exc import IntegrityError


def error_response(code: str, message: str, status_code: int, details: dict | list | None = None) -> JSONResponse:
    return JSONResponse(status_code=status_code, content={"error": {"code": code, "message": message, "details": details or {}}})


def install_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(HTTPException)
    async def http_exception_handler(_: Request, exc: HTTPException):
        detail = exc.detail
        if isinstance(detail, dict):
            return error_response(str(detail.get("code", "HTTP_ERROR")), str(detail.get("message", "Request failed.")), exc.status_code, detail)
        return error_response("HTTP_ERROR", str(detail), exc.status_code)

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(_: Request, exc: RequestValidationError):
        return error_response("VALIDATION_ERROR", "Invalid request data.", status.HTTP_422_UNPROCESSABLE_ENTITY, exc.errors())

    @app.exception_handler(IntegrityError)
    async def integrity_exception_handler(_: Request, __: IntegrityError):
        return error_response("DATA_INTEGRITY_ERROR", "The request conflicts with existing data.", status.HTTP_409_CONFLICT)

    @app.exception_handler(RateLimitExceeded)
    async def rate_limit_exception_handler(_: Request, __: RateLimitExceeded):
        return error_response("RATE_LIMIT_EXCEEDED", "Too many requests. Please try again later.", status.HTTP_429_TOO_MANY_REQUESTS)

    @app.exception_handler(Exception)
    async def unhandled_exception_handler(_: Request, __: Exception):
        return error_response("INTERNAL_SERVER_ERROR", "Something went wrong.", status.HTTP_500_INTERNAL_SERVER_ERROR)
