import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.security import decode_access_token
from app.db.session import get_db
from app.dependencies.auth import bearer_scheme, require_roles
from app.models import AdminActionLog, PGListing, Report, User
from app.models.enums import ReportPriority, ReportStatus, ReportType, Role
from app.schemas.trust import ReportCreate, ReportResponse, ReportUpdate
from app.core.rate_limit import limiter

router = APIRouter(prefix="/reports", tags=["reports"])
student_router = APIRouter(prefix="/student/reports", tags=["student-reports"])
admin_router = APIRouter(prefix="/admin/reports", tags=["admin-reports"])


def _optional_student(credentials: HTTPAuthorizationCredentials | None, db: Session) -> User | None:
    if not credentials:
        return None
    try:
        payload = decode_access_token(credentials.credentials)
        user = db.get(User, uuid.UUID(str(payload.get("sub"))))
        return user if user and user.role == Role.STUDENT else None
    except Exception:
        return None


def _response(report: Report) -> ReportResponse:
    return ReportResponse(
        id=report.id, pg_id=report.pg_id, pg_name=report.pg.pg_name, student_id=report.student_id,
        reporter_email=report.reporter_email, reporter_phone=report.reporter_phone, report_type=report.report_type,
        priority=report.priority, reason=report.reason, description=report.description, status=report.status,
        admin_note=report.admin_note, resolved_by=report.resolved_by, resolved_at=report.resolved_at,
        created_at=report.created_at, updated_at=report.updated_at,
    )


@router.post("/pg/{pg_id}", response_model=ReportResponse, status_code=201)
@limiter.limit("5/minute")
def create_report(request: Request, pg_id: uuid.UUID, payload: ReportCreate, credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme), db: Session = Depends(get_db)) -> ReportResponse:
    listing = db.get(PGListing, pg_id)
    if not listing:
        raise HTTPException(status_code=404, detail="PG listing not found.")
    student = _optional_student(credentials, db)
    if not student and not payload.reporter_email:
        raise HTTPException(status_code=422, detail="Reporter email is required for public reports.")
    report = Report(pg_id=pg_id, student_id=student.id if student else None, **payload.model_dump())
    db.add(report)
    db.commit()
    db.refresh(report)
    return _response(db.scalar(select(Report).options(selectinload(Report.pg)).where(Report.id == report.id)))


@student_router.get("", response_model=list[ReportResponse])
def my_reports(user: User = Depends(require_roles(Role.STUDENT)), db: Session = Depends(get_db)) -> list[ReportResponse]:
    reports = db.scalars(select(Report).options(selectinload(Report.pg)).where(Report.student_id == user.id).order_by(Report.created_at.desc())).all()
    return [_response(r) for r in reports]


@admin_router.get("", response_model=list[ReportResponse])
def admin_reports(status_filter: ReportStatus | None = Query(default=None, alias="status"), priority: ReportPriority | None = None, report_type: ReportType | None = None, _: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> list[ReportResponse]:
    query = select(Report).options(selectinload(Report.pg))
    if status_filter:
        query = query.where(Report.status == status_filter)
    if priority:
        query = query.where(Report.priority == priority)
    if report_type:
        query = query.where(Report.report_type == report_type)
    return [_response(r) for r in db.scalars(query.order_by(Report.created_at.desc())).all()]


@admin_router.get("/{report_id}", response_model=ReportResponse)
def admin_report_detail(report_id: uuid.UUID, _: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> ReportResponse:
    report = db.scalar(select(Report).options(selectinload(Report.pg)).where(Report.id == report_id))
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return _response(report)


@admin_router.patch("/{report_id}", response_model=ReportResponse)
def update_report(report_id: uuid.UUID, payload: ReportUpdate, _: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> ReportResponse:
    report = db.scalar(select(Report).options(selectinload(Report.pg)).where(Report.id == report_id))
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    for key, value in payload.model_dump(exclude_unset=True).items():
        setattr(report, key, value)
    db.commit()
    db.refresh(report)
    return _response(report)


@admin_router.post("/{report_id}/resolve", response_model=ReportResponse)
def resolve_report(report_id: uuid.UUID, admin: User = Depends(require_roles(Role.ADMIN, Role.SUPER_ADMIN)), db: Session = Depends(get_db)) -> ReportResponse:
    report = db.scalar(select(Report).options(selectinload(Report.pg)).where(Report.id == report_id))
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    report.status = ReportStatus.RESOLVED
    report.resolved_by = admin.id
    report.resolved_at = datetime.now(UTC)
    db.add(AdminActionLog(admin_id=admin.id, action="resolve_report", target_type="report", target_id=str(report.id), metadata_json={"pg_id": str(report.pg_id)}))
    db.commit()
    db.refresh(report)
    return _response(report)
