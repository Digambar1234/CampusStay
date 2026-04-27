from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi.middleware import SlowAPIMiddleware
from sqlalchemy import text

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.exceptions import install_exception_handlers
from app.core.middleware import RequestContextMiddleware, SecurityHeadersMiddleware
from app.core.rate_limit import limiter
from app.db.session import engine

settings = get_settings()

app = FastAPI(
    title="CampusStay API",
    version="0.1.0",
    description="Verified PG discovery platform API for students near LPU.",
)
app.state.limiter = limiter

app.add_middleware(SecurityHeadersMiddleware)
app.add_middleware(RequestContextMiddleware)
app.add_middleware(SlowAPIMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

install_exception_handlers(app)


@app.get("/health", tags=["health"])
def health() -> dict[str, str]:
    return {"status": "ok", "environment": settings.environment}


@app.get("/ready", tags=["health"])
def ready() -> dict:
    checks: dict[str, dict[str, bool | str]] = {}
    status_value = "ready"
    try:
        with engine.connect() as connection:
            connection.execute(text("select 1"))
        checks["database"] = {"ok": True}
    except Exception:
        checks["database"] = {"ok": False}
        status_value = "not_ready"

    checks["environment"] = {"ok": bool(settings.database_url and settings.jwt_secret_key)}
    checks["cloudinary"] = {"ok": bool(settings.cloudinary_cloud_name and settings.cloudinary_api_key and settings.cloudinary_api_secret)}
    checks["razorpay"] = {"ok": bool(settings.razorpay_key_id and settings.razorpay_key_secret)}
    if status_value == "ready" and (not checks["cloudinary"]["ok"] or not checks["razorpay"]["ok"]):
        status_value = "degraded"
    return {"status": status_value, "checks": checks}


app.include_router(api_router)
