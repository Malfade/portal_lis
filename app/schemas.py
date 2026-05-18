from datetime import datetime

from pydantic import BaseModel, Field


class LicenseStatusResponse(BaseModel):
    status: str = Field(
        ...,
        description="active | expired | revoked | forbidden | not_found",
    )
    expires_at: datetime | None = None
    license_id: str | None = None
    customer_id: str | None = None
