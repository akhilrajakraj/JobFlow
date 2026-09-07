"""Password hashing and signed bearer-token helpers."""

import base64
import hashlib
import hmac
import json
import secrets
import time

from app.core.config import settings

_ITERATIONS = 310_000
_TOKEN_TTL = 3600


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, _ITERATIONS)
    return f"pbkdf2_sha256${_ITERATIONS}${base64.urlsafe_b64encode(salt).decode()}${base64.urlsafe_b64encode(digest).decode()}"


def verify_password(password: str, encoded: str) -> bool:
    try:
        algorithm, iterations, salt, expected = encoded.split("$", 3)
        if algorithm != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.urlsafe_b64decode(salt), int(iterations))
        return hmac.compare_digest(base64.urlsafe_b64encode(digest).decode(), expected)
    except (ValueError, TypeError):
        return False


def _b64(value: bytes) -> str:
    return base64.urlsafe_b64encode(value).rstrip(b"=").decode()


def create_access_token(subject: str, role: str, expires_in: int = _TOKEN_TTL) -> str:
    header = _b64(json.dumps({"alg": "HS256", "typ": "JWT"}, separators=(",", ":")).encode())
    payload = _b64(json.dumps({"sub": subject, "role": role, "exp": int(time.time()) + expires_in}, separators=(",", ":")).encode())
    signing = f"{header}.{payload}".encode()
    secret = settings.jwt_secret.encode()
    signature = _b64(hmac.new(secret, signing, hashlib.sha256).digest())
    return f"{header}.{payload}.{signature}"


def decode_access_token(token: str) -> dict:
    parts = token.split(".")
    if len(parts) != 3:
        raise ValueError("Invalid token")
    signing = f"{parts[0]}.{parts[1]}".encode()
    expected = _b64(hmac.new(settings.jwt_secret.encode(), signing, hashlib.sha256).digest())
    if not hmac.compare_digest(parts[2], expected):
        raise ValueError("Invalid token signature")
    payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * (-len(parts[1]) % 4)))
    if int(payload.get("exp", 0)) < int(time.time()):
        raise ValueError("Token expired")
    return payload
