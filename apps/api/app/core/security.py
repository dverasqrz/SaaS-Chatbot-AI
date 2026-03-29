from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from jwt.exceptions import InvalidTokenError

from app.core.config import settings

# bcrypt só considera os primeiros 72 bytes da senha (comportamento padrão da lib).
BCRYPT_MAX_PASSWORD_BYTES = 72


def _password_bytes(password: str) -> bytes:
    return password.encode("utf-8")[:BCRYPT_MAX_PASSWORD_BYTES]


def get_password_hash(password: str) -> str:
    if len(password) < 8:
        raise ValueError("A senha deve ter no mínimo 8 caracteres.")
    pw = _password_bytes(password)
    if not pw:
        raise ValueError("Senha inválida.")
    digest = bcrypt.hashpw(pw, bcrypt.gensalt())
    return digest.decode("ascii")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        pw = _password_bytes(plain_password)
        hashed = hashed_password.encode("ascii")
        return bcrypt.checkpw(pw, hashed)
    except Exception as exc:
        raise ValueError("Falha ao verificar senha.") from exc


def create_access_token(subject: str) -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=settings.access_token_expire_minutes)
    payload: dict[str, Any] = {
        "sub": subject,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(
        payload,
        settings.jwt_secret_key.get_secret_value(),
        algorithm=settings.jwt_algorithm,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret_key.get_secret_value(),
            algorithms=[settings.jwt_algorithm],
        )
    except InvalidTokenError as exc:
        raise ValueError("Token inválido ou expirado.") from exc
