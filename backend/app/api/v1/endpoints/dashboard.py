from fastapi import APIRouter, Depends

from app.dependencies.auth import require_roles
from app.models import User
from app.models.enums import Role
from app.schemas.dashboard import DashboardResponse

student_router = APIRouter(prefix="/student", tags=["student"])
owner_router = APIRouter(prefix="/owner", tags=["owner"])
admin_router = APIRouter(prefix="/admin", tags=["admin"])


@student_router.get("/dashboard", response_model=DashboardResponse)
def student_dashboard(current_user: User = Depends(require_roles(Role.STUDENT))) -> DashboardResponse:
    return DashboardResponse(message=f"Welcome, {current_user.full_name}.", role=current_user.role.value)


@owner_router.get("/dashboard", response_model=DashboardResponse)
def owner_dashboard(current_user: User = Depends(require_roles(Role.PG_OWNER))) -> DashboardResponse:
    return DashboardResponse(message=f"Welcome, {current_user.full_name}.", role=current_user.role.value)


@admin_router.get("/dashboard", response_model=DashboardResponse)
def admin_dashboard(current_user: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN))) -> DashboardResponse:
    return DashboardResponse(message=f"Welcome, {current_user.full_name}.", role=current_user.role.value)
