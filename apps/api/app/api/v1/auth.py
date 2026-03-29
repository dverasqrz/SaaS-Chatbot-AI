from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func

from app.api.deps import get_current_user
from app.core.db import get_session
from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.get("/check-setup")
def check_setup(session: Session = Depends(get_session)):
    """Verifica se o sistema já tem usuários cadastrados."""
    user_count = session.exec(select(func.count(User.id))).one()
    return {
        "has_users": user_count > 0,
        "user_count": user_count
    }


@router.get("/me", response_model=User)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
):
    """Retorna informações do usuário atual."""
    return current_user


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, session: Session = Depends(get_session)):
    existing_user = session.exec(
        select(User).where(User.email == data.email.lower())
    ).first()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado.",
        )

    # Verificar se é o primeiro usuário do sistema
    user_count = session.exec(select(func.count(User.id))).one()
    is_first_user = user_count == 0

    try:
        user = User(
            email=data.email.lower(),
            full_name=data.full_name.strip() if data.full_name else None,
            hashed_password=get_password_hash(data.password),
            is_admin=is_first_user,  # Primeiro usuário é automaticamente admin
            is_active=True,
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    session.add(user)
    session.commit()
    session.refresh(user)

    # Criar workspace para o usuário
    workspace_name = f"Workspace de {user.full_name or user.email.split('@')[0]}"
    workspace = Workspace(
        name=workspace_name,
        owner_user_id=user.id,
    )
    session.add(workspace)
    session.commit()

    token = create_access_token(user.id)
    return TokenResponse(access_token=token)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, session: Session = Depends(get_session)):
    user = session.exec(
        select(User).where(User.email == data.email.lower())
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
        )

    try:
        valid_password = verify_password(data.password, user.hashed_password)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
        ) from exc

    if not valid_password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciais inválidas.",
        )

    return TokenResponse(access_token=create_access_token(user.id))
