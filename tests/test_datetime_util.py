from datetime import datetime, timedelta, timezone

from licensing.datetime_util import license_display_status
from licensing.models import License


def test_license_display_status_naive_expires_at():
    lic = License(
        customer_id="c",
        expires_at=datetime(2099, 1, 1, 0, 0, 0),  # naive from SQLite
        instance_id=None,
    )
    now = datetime(2026, 1, 1, tzinfo=timezone.utc)
    assert license_display_status(lic, now) == "active"

    lic.expires_at = datetime(2020, 1, 1, 0, 0, 0)
    assert license_display_status(lic, now) == "expired"
