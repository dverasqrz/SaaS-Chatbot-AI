from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    name: str = Field(nullable=False, max_length=120)
    email: str = Field(nullable=False, unique=True, index=True, max_length=255)
    hashed_password: str = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    is_active: bool = Field(default=True)
