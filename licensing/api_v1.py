from fastapi import APIRouter, Depends, Header, HTTPException, Request
from sqlalchemy.orm import Session

from licensing.crypto_tokens import hash_scanner_token
from licensing.datetime_util import as_utc, utcnow
from licensing.db import get_db
from licensing.models import License, ScannerApiToken
from licensing.rate_limit import rate_limiter
from licensing.schemas import LicenseStatusResponse

router = APIRouter(prefix="/v1", tags=["v1"])


def _resolve_license_status(
    lic: License, instance_id: str, db: Session
) -> LicenseStatusResponse:
    exp = as_utc(lic.expires_at)
    assert exp is not None
    revoked = as_utc(lic.revoked_at)
    if revoked is not None:
        return LicenseStatusResponse(
            status="revoked",
            expires_at=exp,
            license_id=lic.id,
            customer_id=lic.customer_id,
        )
    now = utcnow()
    if exp <= now:
        return LicenseStatusResponse(
            status="expired",
            expires_at=exp,
            license_id=lic.id,
            customer_id=lic.customer_id,
        )
    bound = (lic.instance_id or "").strip()
    if not bound:
        lic.instance_id = instance_id
        db.add(lic)
        db.commit()
        db.refresh(lic)
    elif bound != instance_id:
        return LicenseStatusResponse(
            status="forbidden",
            expires_at=exp,
            license_id=lic.id,
            customer_id=lic.customer_id,
        )
    return LicenseStatusResponse(
        status="active",
        expires_at=exp,
        license_id=lic.id,
        customer_id=lic.customer_id,
    )


@router.get(
    "/instances/{instance_id}/status",
    response_model=LicenseStatusResponse,
)
def instance_license_status(
    instance_id: str,
    request: Request,
    authorization: str | None = Header(default=None, alias="Authorization"),
    db: Session = Depends(get_db),
):
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="Missing or invalid Authorization header")
    raw = authorization[7:].strip()
    if not raw:
        raise HTTPException(status_code=401, detail="Empty bearer token")

    client_ip = request.client.host if request.client else "unknown"
    rl_key = f"{client_ip}:{instance_id}"
    if not rate_limiter.allow(rl_key):
        raise HTTPException(status_code=429, detail="Rate limit exceeded")

    th = hash_scanner_token(raw)
    row = (
        db.query(ScannerApiToken)
        .filter(ScannerApiToken.token_hash == th)
        .one_or_none()
    )
    if row is None:
        return LicenseStatusResponse(status="not_found")

    lic = db.get(License, row.license_id)
    if lic is None:
        return LicenseStatusResponse(status="not_found")

    return _resolve_license_status(lic, instance_id.strip(), db)
