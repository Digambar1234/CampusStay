from sqlalchemy import select

from app.core.config import get_settings
from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models import User
from app.models.enums import Role


def main() -> None:
    settings = get_settings()
    if not settings.admin_email or not settings.admin_password:
        raise RuntimeError("ADMIN_EMAIL and ADMIN_PASSWORD must be set to seed the admin user.")

    with SessionLocal() as db:
        existing_admin = db.scalar(select(User).where(User.email == settings.admin_email.lower()))
        if existing_admin:
            print(f"Admin already exists: {existing_admin.email}")
            return

        admin = User(
            full_name=settings.admin_full_name or "CampusStay Admin",
            email=settings.admin_email.lower(),
            phone=None,
            password_hash=get_password_hash(settings.admin_password),
            role=Role.ADMIN,
            is_active=True,
            is_verified=True,
        )
        db.add(admin)
        db.commit()
        print(f"Created admin user: {admin.email}")


if __name__ == "__main__":
    main()
