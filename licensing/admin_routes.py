from datetime import datetime, timezone
from pathlib import Path

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from licensing.config import get_settings
from licensing.crypto_tokens import generate_scanner_token, hash_scanner_token
from licensing.datetime_util import license_display_status, utcnow
from licensing.db import get_db
from licensing.models import Customer, License, ScannerApiToken

templates = Jinja2Templates(
    directory=str(Path(__file__).resolve().parent.parent / "templates")
)

router = APIRouter(tags=["admin"])


def require_admin_session(request: Request) -> RedirectResponse | None:
    if request.session.get("admin") != "1":
        return RedirectResponse("/admin/login", status_code=303)
    return None


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request, "error": None},
    )


@router.post("/login", response_class=HTMLResponse)
def login_submit(
    request: Request,
    password: str = Form(...),
):
    expected = get_settings().admin_password
    if not expected:
        return templates.TemplateResponse(
            "login.html",
            {
                "request": request,
                "error": "Server misconfigured: LICENSING_ADMIN_PASSWORD is not set.",
            },
            status_code=503,
        )
    if password != expected:
        return templates.TemplateResponse(
            "login.html",
            {"request": request, "error": "Invalid password"},
            status_code=401,
        )
    request.session["admin"] = "1"
    return RedirectResponse("/admin/", status_code=303)


@router.get("/logout")
def logout(request: Request):
    request.session.clear()
    return RedirectResponse("/admin/login", status_code=303)


@router.get("/", response_class=HTMLResponse)
def admin_home(request: Request, db: Session = Depends(get_db)):
    if (redir := require_admin_session(request)):
        return redir
    customers = db.query(Customer).order_by(Customer.name).all()
    return templates.TemplateResponse(
        "dashboard.html",
        {"request": request, "customers": customers},
    )


@router.post("/customers")
def create_customer(
    request: Request,
    name: str = Form(...),
    db: Session = Depends(get_db),
):
    if (redir := require_admin_session(request)):
        return redir
    c = Customer(name=name.strip())
    db.add(c)
    db.commit()
    return RedirectResponse(f"/admin/customers/{c.id}", status_code=303)


@router.get("/customers/{customer_id}", response_class=HTMLResponse)
def customer_detail(
    request: Request,
    customer_id: str,
    db: Session = Depends(get_db),
):
    if (redir := require_admin_session(request)):
        return redir
    c = db.get(Customer, customer_id)
    if not c:
        raise HTTPException(status_code=404)
    flash = request.session.pop("flash_scanner_token", None)
    now = utcnow()
    license_statuses = {lic.id: license_display_status(lic, now) for lic in c.licenses}
    return templates.TemplateResponse(
        "customer_detail.html",
        {
            "request": request,
            "customer": c,
            "new_token": flash,
            "license_statuses": license_statuses,
        },
    )


@router.post("/licenses")
def create_license(
    request: Request,
    customer_id: str = Form(...),
    expires_at: str = Form(...),
    instance_id: str = Form(""),
    notes: str = Form(""),
    db: Session = Depends(get_db),
):
    if (redir := require_admin_session(request)):
        return redir
    c = db.get(Customer, customer_id)
    if not c:
        raise HTTPException(status_code=404)
    raw = expires_at.strip().replace("Z", "+00:00")
    try:
        exp = datetime.fromisoformat(raw)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid expires_at")
    if exp.tzinfo is None:
        exp = exp.replace(tzinfo=timezone.utc)
    inst = instance_id.strip() or None
    lic = License(
        customer_id=customer_id,
        expires_at=exp,
        instance_id=inst,
        notes=notes.strip() or None,
    )
    db.add(lic)
    db.commit()
    return RedirectResponse(f"/admin/customers/{customer_id}", status_code=303)


@router.post("/licenses/{license_id}/revoke")
def revoke_license(
    request: Request,
    license_id: str,
    db: Session = Depends(get_db),
):
    if (redir := require_admin_session(request)):
        return redir
    lic = db.get(License, license_id)
    if not lic:
        raise HTTPException(status_code=404)
    lic.revoked_at = datetime.now(timezone.utc)
    db.add(lic)
    db.commit()
    return RedirectResponse(f"/admin/customers/{lic.customer_id}", status_code=303)


@router.post("/licenses/{license_id}/instance")
def set_instance(
    request: Request,
    license_id: str,
    instance_id: str = Form(""),
    db: Session = Depends(get_db),
):
    if (redir := require_admin_session(request)):
        return redir
    lic = db.get(License, license_id)
    if not lic:
        raise HTTPException(status_code=404)
    lic.instance_id = instance_id.strip() or None
    db.add(lic)
    db.commit()
    return RedirectResponse(f"/admin/customers/{lic.customer_id}", status_code=303)


@router.post("/tokens")
def create_token(
    request: Request,
    license_id: str = Form(...),
    label: str = Form(""),
    db: Session = Depends(get_db),
):
    if (redir := require_admin_session(request)):
        return redir
    lic = db.get(License, license_id)
    if not lic:
        raise HTTPException(status_code=404)
    plain = generate_scanner_token()
    tok = ScannerApiToken(
        license_id=license_id,
        token_hash=hash_scanner_token(plain),
        label=label.strip() or None,
    )
    db.add(tok)
    db.commit()
    request.session["flash_scanner_token"] = plain
    return RedirectResponse(
        f"/admin/customers/{lic.customer_id}",
        status_code=303,
    )
