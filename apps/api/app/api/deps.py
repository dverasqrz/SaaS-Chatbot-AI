from __future__ import annotations

from fastapi import Depends, Header, HTTPException, status
from sqlmodel import Session, select

from app.core.db import get_session
from app.core.security import decode_access_token
from app.models.user import User


def get_current_user(
    authorization: str | None = Header(default=None),
    session: Session = Depends(get_session),
) -> User:
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token Bearer ausente.",
        )

    token = authorization.replace("Bearer ", "", 1).strip()

    try:
        payload = decode_access_token(token)
        user_id = payload["sub"]
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido.",
        ) from exc

    user = session.exec(select(User).where(User.id == user_id)).first()
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inválido ou inativo.",
        )

    return user
