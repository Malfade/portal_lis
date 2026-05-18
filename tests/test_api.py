from datetime import datetime, timedelta, timezone

from licensing.crypto_tokens import generate_scanner_token, hash_scanner_token
from licensing.db import get_session_factory
from licensing.models import Customer, License, ScannerApiToken


def _future(days=30):
    return datetime.now(timezone.utc) + timedelta(days=days)


def _seed_active_token(instance_id: str | None = None):
    db = get_session_factory()()
    c = Customer(name="Acme")
    db.add(c)
    db.commit()
    lic = License(
        customer_id=c.id,
        expires_at=_future(60),
        instance_id=instance_id,
    )
    db.add(lic)
    db.commit()
    plain = generate_scanner_token()
    db.add(
        ScannerApiToken(
            license_id=lic.id,
            token_hash=hash_scanner_token(plain),
            label="test",
        )
    )
    db.commit()
    lid = lic.id
    db.close()
    return plain, lid


def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_status_active(client):
    plain, _ = _seed_active_token(instance_id="abc")
    r = client.get(
        "/v1/instances/abc/status",
        headers={"Authorization": f"Bearer {plain}"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "active"
