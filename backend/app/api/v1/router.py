from fastapi import APIRouter

from app.api.v1.endpoints import admin_pgs, analytics, audit_logs, auth, credits, featured_listings, owner_listings, pgs, reports, reviews
from app.api.v1.endpoints.dashboard import admin_router, owner_router, student_router

api_router = APIRouter(prefix="/api/v1")
api_router.include_router(auth.router)
api_router.include_router(student_router)
api_router.include_router(owner_router)
api_router.include_router(admin_router)
api_router.include_router(owner_listings.router)
api_router.include_router(admin_pgs.router)
api_router.include_router(pgs.router)
api_router.include_router(credits.router)
api_router.include_router(reviews.router)
api_router.include_router(reviews.student_router)
api_router.include_router(reviews.admin_router)
api_router.include_router(reports.router)
api_router.include_router(reports.student_router)
api_router.include_router(reports.admin_router)
api_router.include_router(featured_listings.router)
api_router.include_router(analytics.owner_router)
api_router.include_router(analytics.admin_router)
api_router.include_router(audit_logs.router)

# Reserved API namespaces for Part 2 expansion.
api_router.include_router(APIRouter(prefix="/users", tags=["users"]))
