
from __future__ import annotations

from fastapi import HTTPException, status
from sqlmodel import Session, select

from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceResponse


class WorkspaceService:
    def __init__(self, session: Session, current_user: User):
        self.session = session
        self.current_user = current_user

    def list_workspaces(self) -> list[WorkspaceResponse]:
        items = self.session.exec(
            select(Workspace).where(Workspace.owner_user_id == self.current_user.id)
        ).all()

        return [
            WorkspaceResponse(
                id=item.id,
                name=item.name,
                owner_user_id=item.owner_user_id,
                created_at=item.created_at,
            )
            for item in items
        ]
