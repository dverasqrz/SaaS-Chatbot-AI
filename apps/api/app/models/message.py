from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
from uuid import uuid4

from sqlmodel import Field, SQLModel


class Message(SQLModel, table=True):
    id: str = Field(default_factory=lambda: str(uuid4()), primary_key=True)
    conversation_id: str = Field(nullable=False, index=True)
    user_id: str = Field(nullable=False, index=True)
    role: str = Field(nullable=False, max_length=20)
    content: str = Field(nullable=False)
    model: Optional[str] = Field(default=None, max_length=120)
    provider: Optional[str] = Field(default=None, max_length=40)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
