from datetime import datetime, timezone

from app.models import License


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def as_utc(dt: datetime | None) -> datetime | None:
    if dt is None:
        return None
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc)


def license_display_status(lic: License, now: datetime | None = None) -> str:
    if lic.revoked_at is not None:
        return "revoked"
    exp = as_utc(lic.expires_at)
    ref = now or utcnow()
    if exp is not None and exp <= ref:
        return "expired"
    return "active"
