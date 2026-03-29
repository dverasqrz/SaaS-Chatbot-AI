from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class ConversationCreateRequest(BaseModel):
    workspace_id: str
    title: str = Field(default="Nova conversa", max_length=255)


class ConversationResponse(BaseModel):
    id: str
    workspace_id: str
    user_id: str
    title: str
    created_at: datetime
    updated_at: datetime


class MessageCreateRequest(BaseModel):
    role: str = Field(pattern="^(user|assistant|system)$")
    content: str = Field(min_length=1)
    model: str | None = None
    provider: str | None = None


class ConversationIdsRequest(BaseModel):
    conversation_ids: list[str] = Field(min_length=1, max_length=100)


class MessageResponse(BaseModel):
    id: str
    conversation_id: str
    role: str
    content: str
    model: str | None = None
    provider: str | None = None
    created_at: datetime
