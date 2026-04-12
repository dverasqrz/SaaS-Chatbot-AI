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
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])

def get_auth_service(session: Session = Depends(get_session)) -> AuthService:
    return AuthService(session)


@router.get("/check-setup")
def check_setup(auth_service: AuthService = Depends(get_auth_service)):
    """Verifica se o sistema já tem usuários cadastrados."""
    return auth_service.check_setup()


@router.get("/me", response_model=User)
def get_current_user_info(
    current_user: User = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service),
):
    """Retorna informações do usuário atual."""
    return auth_service.get_current_user_info(current_user)


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(data: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.register(data)


@router.post("/login", response_model=TokenResponse)
def login(data: LoginRequest, auth_service: AuthService = Depends(get_auth_service)):
    return auth_service.login(data)
