from datetime import datetime
from uuid import UUID

from pydantic import BaseModel


class AuditLogResponse(BaseModel):
    id: UUID
    admin_id: UUID
    admin_name: str
    admin_email: str
    action: str
    target_type: str
    target_id: str | None
    metadata: dict | None
    created_at: datetime


class PaginatedAuditLogResponse(BaseModel):
    items: list[AuditLogResponse]
    total: int
    page: int
    page_size: int
