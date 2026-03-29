from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.db import get_session
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceResponse

router = APIRouter(prefix="/workspaces", tags=["workspaces"])


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    items = session.exec(
        select(Workspace).where(Workspace.owner_user_id == current_user.id)
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
