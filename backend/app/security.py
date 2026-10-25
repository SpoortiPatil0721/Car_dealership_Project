import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt

from app.config import Settings


class InvalidTokenError(Exception):
    pass


def _b64(raw: bytes) -> str:
    return base64.b64encode(raw).decode()


def hash_password(password: str, settings: Settings) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, settings.password_iterations)
    # store iterations alongside so old hashes keep working if we bump the count
    return f"pbkdf2_sha256${settings.password_iterations}${_b64(salt)}${_b64(digest)}"


def verify_password(password: str, stored: str) -> bool:
    try:
        algo, iterations, salt, expected = stored.split("$")
        if algo != "pbkdf2_sha256":
            return False
        digest = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(salt), int(iterations))
    except ValueError:
        return False
    return hmac.compare_digest(_b64(digest), expected)


def create_access_token(user_id: int, is_admin: bool, settings: Settings, expires_in: timedelta | None = None) -> str:
    now = datetime.now(timezone.utc)
    lifetime = expires_in if expires_in is not None else timedelta(minutes=settings.token_minutes)
    claims = {"sub": str(user_id), "admin": is_admin, "iat": now, "exp": now + lifetime}
    return jwt.encode(claims, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str, settings: Settings) -> dict:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError as exc:
        raise InvalidTokenError(str(exc)) from exc
