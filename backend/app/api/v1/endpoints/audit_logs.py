import uuid
from datetime import datetime

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from app.db.session import get_db
from app.dependencies.auth import require_roles
from app.models import AdminActionLog, User
from app.models.enums import Role
from app.schemas.audit import AuditLogResponse, PaginatedAuditLogResponse

router = APIRouter(prefix="/admin/audit-logs", tags=["admin-audit-logs"])


@router.get("", response_model=PaginatedAuditLogResponse)
def list_audit_logs(
    action: str | None = None,
    target_type: str | None = None,
    admin_id: uuid.UUID | None = None,
    date_from: datetime | None = None,
    date_to: datetime | None = None,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=50, ge=1, le=100),
    _: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)),
    db: Session = Depends(get_db),
) -> PaginatedAuditLogResponse:
    query = select(AdminActionLog).options(selectinload(AdminActionLog.admin))
    if action:
        query = query.where(AdminActionLog.action == action)
    if target_type:
        query = query.where(AdminActionLog.target_type == target_type)
    if admin_id:
        query = query.where(AdminActionLog.admin_id == admin_id)
    if date_from:
        query = query.where(AdminActionLog.created_at >= date_from)
    if date_to:
        query = query.where(AdminActionLog.created_at <= date_to)
    total = db.scalar(select(func.count()).select_from(query.subquery())) or 0
    logs = db.scalars(query.order_by(AdminActionLog.created_at.desc()).offset((page - 1) * page_size).limit(page_size)).all()
    return PaginatedAuditLogResponse(
        items=[
            AuditLogResponse(
                id=log.id,
                admin_id=log.admin_id,
                admin_name=log.admin.full_name,
                admin_email=log.admin.email,
                action=log.action,
                target_type=log.target_type,
                target_id=log.target_id,
                metadata=log.metadata_json,
                created_at=log.created_at,
            )
            for log in logs
        ],
        total=total,
        page=page,
        page_size=page_size,
    )
