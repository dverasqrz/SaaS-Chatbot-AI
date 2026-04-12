
from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional

from fastapi import HTTPException, status
from sqlmodel import Session, select, func

from app.core.security import get_password_hash
from app.models.message import Message
from app.models.user import User
from app.schemas.admin import (
    UserAdminResponse,
    UserCreateRequest,
    UserUpdateRequest,
    AdminStatsResponse,
    TokensByProvider,
)


class AdminService:
    def __init__(self, session: Session, current_user: User):
        self.session = session
        self.current_user = current_user

    def _get_tokens_by_provider(self, user_id: Optional[str] = None) -> TokensByProvider:
        """Calculate tokens used by provider for a specific user or all users."""
        providers = ['groq', 'openai', 'google']
        result = {}

        for provider in providers:
            query = select(func.sum(Message.total_tokens)).where(
                Message.provider == provider,
                Message.total_tokens.is_not(None)
            )
            if user_id:
                query = query.where(Message.user_id == user_id)

            tokens = self.session.exec(query).one()
            result[provider] = int(tokens) if tokens else 0

        return TokensByProvider(**result)

    def get_admin_stats(self) -> AdminStatsResponse:
        """Estatísticas gerais para o dashboard admin com tokens reais por provedor."""
        total_users = self.session.exec(select(func.count(User.id))).one()
        active_users_count = self.session.exec(
            select(func.count(User.id)).where(User.is_active == True)
        ).one()

        try:
            total_tokens = self.session.exec(
                select(func.sum(Message.total_tokens)).where(Message.total_tokens.is_not(None))
            ).one()
            total_tokens = int(total_tokens) if total_tokens else 0
        except:
            total_tokens = 0

        tokens_by_provider = self._get_tokens_by_provider()

        return AdminStatsResponse(
            total_users=total_users,
            active_users=active_users_count,
            total_tokens_used=total_tokens,
            tokens_by_provider=tokens_by_provider,
        )

    def list_users(self) -> List[UserAdminResponse]:
        """Lista todos os usuários com informações administrativas e tokens por provedor."""
        users = self.session.exec(select(User).order_by(User.created_at.desc())).all()

        result = []
        for user in users:
            try:
                user_tokens = self.session.exec(
                    select(func.sum(Message.total_tokens))
                    .where(Message.user_id == user.id)
                    .where(Message.total_tokens.is_not(None))
                ).one()
                user_tokens = int(user_tokens) if user_tokens else 0
            except:
                user_tokens = 0

            tokens_by_provider = self._get_tokens_by_provider(user.id)

            recent_message = self.session.exec(
                select(Message)
                .where(Message.user_id == user.id)
                .order_by(Message.created_at.desc())
                .limit(1)
            ).first()

            is_online = False
            if recent_message:
                now_utc = datetime.now(timezone.utc)
                msg_time = recent_message.created_at
                if msg_time.tzinfo is None:
                    msg_time = msg_time.replace(tzinfo=timezone.utc)
                time_diff = now_utc - msg_time
                is_online = time_diff.total_seconds() <= 300

            result.append(UserAdminResponse(
                id=user.id,
                email=user.email,
                full_name=user.full_name,
                is_active=user.is_active,
                is_admin=user.is_admin,
                created_at=user.created_at,
                last_login=user.last_login,
                tokens_used=user_tokens,
                tokens_by_provider=tokens_by_provider,
                is_online=is_online,
            ))

        return result

    def create_user(self, data: UserCreateRequest) -> UserAdminResponse:
        """Cria um novo usuário (admin only)."""
        existing = self.session.exec(
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
            hashed_password=get_password_hash(data.password),
            is_admin=data.is_admin or False,
            is_active=data.is_active if data.is_active is not None else True,
        )

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        return UserAdminResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            last_login=user.last_login,
            tokens_used=0,
            tokens_by_provider=TokensByProvider(groq=0, openai=0, google=0),
            is_online=False,
        )

    def delete_user(self, user_id: str) -> None:
        """Deleta um usuário (admin only)."""
        user = self.session.exec(select(User).where(User.id == user_id)).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )

        if user.id == self.current_user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não pode deletar seu próprio usuário.",
            )

        messages = self.session.exec(
            select(Message).where(Message.user_id == user_id)
        ).all()
        for msg in messages:
            self.session.delete(msg)

        self.session.delete(user)
        self.session.commit()

    def toggle_registration(self) -> dict[str, str]:
        """Ativa/desativa o registro de novos usuários."""
        # Aqui você poderia implementar uma configuração global
        # Por enquanto, vamos retornar um placeholder
        return {"message": "Funcionalidade de toggle de registro implementada"}

    def update_user(self, user_id: str, data: UserUpdateRequest) -> UserAdminResponse:
        """Atualiza um usuário existente (admin only)."""
        user = self.session.exec(select(User).where(User.id == user_id)).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Usuário não encontrado.",
            )

        if user.id == self.current_user.id and data.is_active is False:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Não pode desativar seu próprio usuário.",
            )

        # Atualizar campos
        if data.email is not None:
            user.email = data.email
        if data.full_name is not None:
            user.full_name = data.full_name
        if data.is_active is not None:
            user.is_active = data.is_active
        if data.is_admin is not None:
            user.is_admin = data.is_admin
        if data.password is not None:
            user.hashed_password = get_password_hash(data.password)

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        # Recalcular tokens para o usuário atualizado
        user_tokens = 0
        try:
            user_tokens = self.session.exec(
                select(func.sum(Message.total_tokens))
                .where(Message.user_id == user.id)
                .where(Message.total_tokens.is_not(None))
            ).one()
            user_tokens = int(user_tokens) if user_tokens else 0
        except:
            pass

        tokens_by_provider = self._get_tokens_by_provider(user.id)

        return UserAdminResponse(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            is_active=user.is_active,
            is_admin=user.is_admin,
            created_at=user.created_at,
            last_login=user.last_login,
            tokens_used=user_tokens,
            tokens_by_provider=tokens_by_provider,
            is_online=False,
        )
