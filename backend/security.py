import base64
import hashlib
import hmac
import os
import secrets
from datetime import datetime, timedelta, timezone
from typing import TYPE_CHECKING, Union
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from .config import get_settings
from .db import get_db

if TYPE_CHECKING:
    from .models import Role, User




bearer = HTTPBearer(auto_error=False)
settings = get_settings()


def hash_password(password: str) -> str:
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 600_000)
    return f"pbkdf2_sha256$600000${base64.b64encode(salt).decode()}${base64.b64encode(key).decode()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        _, iterations, salt, expected = stored.split("$")
        actual = hashlib.pbkdf2_hmac("sha256", password.encode(), base64.b64decode(salt), int(iterations))
        return hmac.compare_digest(actual, base64.b64decode(expected))
    except (ValueError, TypeError):
        return False


def create_access_token(user: Union["User", dict]) -> str:
    now = datetime.now(timezone.utc)
    if isinstance(user, dict):
        sub = user.get("sub") or user.get("id")
        role = user.get("role")
        if hasattr(role, "value"):
            role = role.value
        full_name = user.get("full_name", "")
        payload = {
            "sub": str(sub),
            "role": str(role),
            "full_name": full_name,
            "iss": settings.jwt_issuer,
            "iat": now,
            "exp": now + timedelta(minutes=settings.access_token_minutes),
            "jti": secrets.token_hex(12),
        }
        return jwt.encode(payload, settings.jwt_secret, algorithm="HS256")

    role_val = user.role.value if hasattr(user.role, "value") else str(user.role)
    return jwt.encode(
        {
            "sub": str(user.id),
            "role": role_val,
            "full_name": user.full_name,
            "iss": settings.jwt_issuer,
            "iat": now,
            "exp": now + timedelta(minutes=settings.access_token_minutes),
            "jti": secrets.token_hex(12),
        },
        settings.jwt_secret,
        algorithm="HS256",
    )



_REVOKED_JTIS: set[str] = set()

def revoke_jti(jti: str, exp_timestamp: float | None = None) -> None:
    """Revoke a JWT by adding its jti to the revocation blocklist."""
    if not jti:
        return
    _REVOKED_JTIS.add(jti)
    try:
        from .rate_limiter import rate_limiter
        if rate_limiter.redis:
            ttl = int(exp_timestamp - datetime.now(timezone.utc).timestamp()) if exp_timestamp else 3600
            if ttl > 0:
                rate_limiter.redis.setex(f"revoked_jti:{jti}", ttl, "1")
    except Exception:
        pass


def decode_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.jwt_secret, algorithms=["HS256"], issuer=settings.jwt_issuer)
        jti = payload.get("jti")
        if jti:
            if jti in _REVOKED_JTIS:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token has been revoked")
            try:
                from .rate_limiter import rate_limiter
                if rate_limiter.redis and rate_limiter.redis.get(f"revoked_jti:{jti}"):
                    _REVOKED_JTIS.add(jti)
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token has been revoked")
            except HTTPException:
                raise
            except Exception:
                pass
        return payload
    except jwt.PyJWTError as exc:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="invalid or expired token") from exc


def current_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> "User":
    from .models import User
    if not credentials:
        raise HTTPException(status_code=401, detail="authentication required")
    payload = decode_token(credentials.credentials)
    user = db.get(User, payload["sub"])
    if not user or not user.active:
        raise HTTPException(status_code=401, detail="account unavailable")
    return user


def optional_user(credentials: HTTPAuthorizationCredentials = Depends(bearer), db: Session = Depends(get_db)) -> "User | None":
    from .models import User
    if not credentials:
        return None
    try:
        payload = decode_token(credentials.credentials)
        user = db.get(User, payload["sub"])
        if user and user.active:
            return user
    except Exception:
        pass
    return None



def require_roles(*roles: "Role"):
    def dependency(user: "User" = Depends(current_user)) -> "User":
        if user.role not in roles:
            raise HTTPException(status_code=403, detail="insufficient permissions")
        return user
    return dependency


from cryptography.fernet import Fernet

def _get_fernet_cipher() -> Fernet:
    key = settings.data_encryption_key
    if not key:
        key = "development-only-data-encryption-key-must-be-changed"
    # Derive a 32-byte key suitable for Fernet
    key_bytes = hashlib.sha256(key.encode()).digest()
    fernet_key = base64.urlsafe_b64encode(key_bytes)
    return Fernet(fernet_key)


def encrypt_field(val: str | None) -> str | None:
    if val is None:
        return None
    try:
        cipher = _get_fernet_cipher()
        return cipher.encrypt(val.encode("utf-8")).decode("utf-8")
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Field encryption failure. Operation aborted for data safety."
        ) from exc


def decrypt_field(val: str | None) -> str | None:
    if val is None:
        return None
    try:
        cipher = _get_fernet_cipher()
        return cipher.decrypt(val.encode("utf-8")).decode("utf-8")
    except Exception as exc:
        # Fail closed: Do NOT fallback to raw text if decryption fails
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Secure storage decryption error. Access denied."
        ) from exc


def validate_participant_access(resource_client_id: str, resource_lawyer_id: str | None, current_user: "User") -> None:
    """Enforce strict participant boundary isolation (BOLA/IDOR defense)."""
    from .models import Role
    if current_user.role == Role.ADMIN:
        return
    user_id_str = str(current_user.id)
    if user_id_str != str(resource_client_id) and (not resource_lawyer_id or user_id_str != str(resource_lawyer_id)):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="record unavailable"
        )


