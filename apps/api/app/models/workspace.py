from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import Field, SQLModel


class Workspace(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(nullable=False, max_length=120)
    owner_user_id: str = Field(nullable=False, index=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
