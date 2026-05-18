from datetime import datetime, timedelta, timezone

from app.crypto_tokens import generate_scanner_token, hash_scanner_token
from app.db import SessionLocal
from app.models import Customer, License, ScannerApiToken


def _future(days=30):
    return datetime.now(timezone.utc) + timedelta(days=days)


def _seed_active_token(instance_id: str | None = None):
    db = SessionLocal()
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


def test_status_active_auto_bind_instance(client):
    plain, _ = _seed_active_token(instance_id=None)
    mid = "deadbeefdeadbeefdeadbeefdeadbeef"
    r = client.get(
        f"/v1/instances/{mid}/status",
        headers={"Authorization": f"Bearer {plain}"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "active"
    assert data["expires_at"] is not None


def test_status_forbidden_wrong_instance(client):
    plain, _ = _seed_active_token(instance_id="aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa")
    r = client.get(
        "/v1/instances/bbbbbbbbbbbbbbbbbbbbbbbbbbbbbbbb/status",
        headers={"Authorization": f"Bearer {plain}"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "forbidden"


def test_status_revoked(client):
    plain, lid = _seed_active_token(instance_id="abc")
    db = SessionLocal()
    lic = db.get(License, lid)
    lic.revoked_at = datetime.now(timezone.utc)
    db.add(lic)
    db.commit()
    db.close()
    r = client.get(
        "/v1/instances/abc/status",
        headers={"Authorization": f"Bearer {plain}"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "revoked"


def test_status_expired(client):
    plain, lid = _seed_active_token(instance_id="abc")
    db = SessionLocal()
    lic = db.get(License, lid)
    lic.expires_at = datetime.now(timezone.utc) - timedelta(days=1)
    db.add(lic)
    db.commit()
    db.close()
    r = client.get(
        "/v1/instances/abc/status",
        headers={"Authorization": f"Bearer {plain}"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "expired"


def test_status_bad_token(client):
    r = client.get(
        "/v1/instances/abc/status",
        headers={"Authorization": "Bearer invalid"},
    )
    assert r.status_code == 200
    assert r.json()["status"] == "not_found"


def test_status_missing_auth(client):
    r = client.get("/v1/instances/abc/status")
    assert r.status_code == 401
