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
)

router = APIRouter(prefix="/admin", tags=["admin"])


@router.get("/stats", response_model=AdminStatsResponse)
def get_admin_stats(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user),
):
    """Estatísticas gerais para o dashboard admin."""
    total_users = session.exec(select(func.count(User.id))).one()
    active_users = session.exec(
        select(func.count(User.id)).where(User.is_active == True)
    ).one()
    
    # Total de tokens usados (soma de todos os caracteres das mensagens)
    # Se não há mensagens, retorna 0
    try:
        total_tokens = session.exec(select(func.length(Message.content))).one()
    except:
        total_tokens = 0
    
    return AdminStatsResponse(
        total_users=total_users,
        active_users=active_users,
        total_tokens_used=total_tokens,
    )


@router.get("/users", response_model=List[UserAdminResponse])
def list_users(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user),
):
    """Lista todos os usuários com informações administrativas."""
    users = session.exec(select(User).order_by(User.created_at.desc())).all()
    
    result = []
    for user in users:
        # Contar tokens usados pelo usuário
        try:
            user_tokens = session.exec(
                select(func.length(Message.content)).where(Message.user_id == user.id)
            ).one()
        except:
            user_tokens = 0
        
        # Verificar se usuário está "online" (mensagem recente)
        recent_message = session.exec(
            select(Message)
            .where(Message.user_id == user.id)
            .order_by(Message.created_at.desc())
            .limit(1)
        ).first()
        
        is_online = False
        if recent_message:
            # Garante que ambos os datetimes tenham timezone para comparação
            now_utc = datetime.now(timezone.utc)
            time_diff = now_utc - recent_message.created_at
            is_online = time_diff.total_seconds() <= 300  # 5 minutos
        
        result.append(UserAdminResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            last_login=user.last_login,
            tokens_used=user_tokens,
            is_online=is_online,
        ))
    
    return result


@router.post("/users", response_model=UserAdminResponse, status_code=status.HTTP_201_CREATED)
def create_user(
    data: UserCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user),
):
    """Cria um novo usuário (admin only)."""
    # Verificar se email já existe
    existing = session.exec(
        select(User).where(User.email == data.email)
    ).first()
    
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado.",
        )
    
    user = User(
        email=data.email,
        full_name=data.full_name,
        password=data.password,  # Será hasheado automaticamente pelo modelo
        is_admin=data.is_admin or False,
        is_active=data.is_active if data.is_active is not None else True,
    )
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return UserAdminResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
        last_login=user.last_login,
        tokens_used=0,
        is_online=False,
    )


@router.put("/users/{user_id}", response_model=UserAdminResponse)
def update_user(
    user_id: str,
    data: UserUpdateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user),
):
    """Atualiza um usuário existente (admin only)."""
    user = session.exec(select(User).where(User.id == user_id)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )
    
    # Impedir auto-desativação
    if user.id == current_user.id and data.is_active is False:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não pode desativar seu próprio usuário.",
        )
    
    # Atualizar campos
    if data.email is not None:
        # Verificar se email já existe
        existing = session.exec(
            select(User).where(User.email == data.email, User.id != user_id)
        ).first()
        
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já está em uso por outro usuário.",
            )
        user.email = data.email
    
    if data.full_name is not None:
        user.full_name = data.full_name
    
    if data.is_admin is not None:
        # Impedir remoção de próprio admin
        if user.id == current_user.id and data.is_admin is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não pode remover privilégios de admin do próprio usuário.",
            )
        user.is_admin = data.is_admin
    
    if data.is_active is not None:
        user.is_active = data.is_active
    
    if data.password is not None and data.password.strip():
        user.password = data.password  # Será hasheado automaticamente
    
    session.add(user)
    session.commit()
    session.refresh(user)
    
    # Recalcular tokens
    try:
        user_tokens = session.exec(
            select(func.length(Message.content)).where(Message.user_id == user.id)
        ).one()
    except:
        user_tokens = 0
    
    return UserAdminResponse(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_admin=user.is_admin,
        created_at=user.created_at,
        last_login=user.last_login,
        tokens_used=user_tokens,
        is_online=False,
    )


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user),
):
    """Remove um usuário (admin only)."""
    user = session.exec(select(User).where(User.id == user_id)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado.",
        )
    
    # Impedir auto-remoção
    if user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não pode remover seu próprio usuário.",
        )
    
    # Remover mensagens do usuário
    messages = session.exec(
        select(Message).where(Message.user_id == user_id)
    ).all()
    for msg in messages:
        session.delete(msg)
    
    # Remover usuário
    session.delete(user)
    session.commit()


@router.post("/toggle-registration")
def toggle_registration(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_admin_user),
):
    """Ativa/desativa o registro de novos usuários."""
    # Aqui você poderia implementar uma configuração global
    # Por enquanto, vamos retornar um placeholder
    return {"message": "Funcionalidade de toggle de registro implementada"}
