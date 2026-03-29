from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class WorkspaceCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=120)


class WorkspaceResponse(BaseModel):
    id: str
    name: str
    owner_user_id: str
    created_at: datetime
