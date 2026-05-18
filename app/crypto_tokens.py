import hashlib
import secrets


def hash_scanner_token(plain: str) -> str:
    return hashlib.sha256(plain.encode("utf-8")).hexdigest()


def generate_scanner_token() -> str:
    return "aksec_" + secrets.token_urlsafe(32)
