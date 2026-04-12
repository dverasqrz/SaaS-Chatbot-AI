
from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session, select, func

from app.core.security import (
    create_access_token,
    get_password_hash,
    verify_password,
)
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse


class AuthService:
    def __init__(self, session: Session):
        self.session = session

    def check_setup(self) -> dict[str, bool | int]:
        """Verifica se o sistema já tem usuários cadastrados."""
        user_count = self.session.exec(select(func.count(User.id))).one()
        return {
            "has_users": user_count > 0,
            "user_count": user_count
        }

    def register(self, data: RegisterRequest) -> TokenResponse:
        existing_user = self.session.exec(
            select(User).where(User.email == data.email.lower())
        ).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="E-mail já cadastrado.",
            )

        user_count = self.session.exec(select(func.count(User.id))).one()
        is_first_user = user_count == 0

        try:
            user = User(
                email=data.email.lower(),
                full_name=data.full_name.strip() if data.full_name else None,
                hashed_password=get_password_hash(data.password),
                is_admin=is_first_user,
                is_active=True,
            )
        except ValueError as exc:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(exc),
            ) from exc

        self.session.add(user)
        self.session.commit()
        self.session.refresh(user)

        workspace_name = f"Workspace de {user.full_name or user.email.split('@')[0]}"
        workspace = Workspace(
            name=workspace_name,
            owner_user_id=user.id,
        )
        self.session.add(workspace)
        self.session.commit()

        token = create_access_token(user.id)
        return TokenResponse(access_token=token)

    def login(self, data: LoginRequest) -> TokenResponse:
        user = self.session.exec(
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

    def get_current_user_info(self, current_user: User) -> User:
        """Retorna informações do usuário atual."""
        return current_user
