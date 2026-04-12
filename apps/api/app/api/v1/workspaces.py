from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.db import get_session
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.workspace import WorkspaceResponse
from app.services.workspace_service import WorkspaceService

router = APIRouter(prefix="/workspaces", tags=["workspaces"])

def get_workspace_service(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> WorkspaceService:
    return WorkspaceService(session, current_user)


@router.get("", response_model=list[WorkspaceResponse])
def list_workspaces(
    workspace_service: WorkspaceService = Depends(get_workspace_service),
):
    return workspace_service.list_workspaces()
