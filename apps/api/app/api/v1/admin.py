from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select, func

from app.api.deps import get_current_user, get_admin_user
from app.core.db import get_session
from app.models.message import Message
from app.models.user import User
from app.schemas.admin import (
    UserAdminResponse,
    UserCreateRequest,
    UserUpdateRequest,
    AdminStatsResponse,
    TokensByProvider,
)
from app.services.admin_service import AdminService

router = APIRouter(prefix="/admin", tags=["admin"])

def get_admin_service(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user),
) -> AdminService:
    return AdminService(session, current_user)





@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    admin_service: AdminService = Depends(get_admin_service),
):
    """Estatísticas gerais para o dashboard admin com tokens reais por provedor."""
    return admin_service.get_admin_stats()


@router.get("/users", response_model=List[UserAdminResponse])
def list_users(
    admin_service: AdminService = Depends(get_admin_service),
):
    """Lista todos os usuários com informações administrativas e tokens por provedor."""
    return admin_service.list_users()


@router.post("/users", response_model=UserAdminResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreateRequest,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Cria um novo usuário (admin only)."""
    return admin_service.create_user(data)


@router.put("/users/{user_id}", response_model=UserAdminResponse)
def update_user(
    user_id: str,
    data: UserUpdateRequest,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Atualiza um usuário existente (admin only)."""
    return admin_service.update_user(user_id, data)



@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    admin_service: AdminService = Depends(get_admin_service),
):
    """Remove um usuário (admin only)."""
    admin_service.delete_user(user_id)
    return None


@router.post("/toggle-registration")
def toggle_registration(
    admin_service: AdminService = Depends(get_admin_service),
):
    """Ativa/desativa o registro de novos usuários."""
    return admin_service.toggle_registration()
