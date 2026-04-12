from __future__ import annotations

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class TokensByProvider(BaseModel):
    groq: int = 0
    openai: int = 0
    google: int = 0


class UserAdminResponse(BaseModel):
    id: str
    email: EmailStr
    full_name: Optional[str] = None
    is_active: bool
    is_admin: bool
    created_at: datetime
    last_login: Optional[datetime] = None
    tokens_used: int
    tokens_by_provider: TokensByProvider
    is_online: bool


class UserCreateRequest(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    password: str
    is_admin: Optional[bool] = False
    is_active: Optional[bool] = True


class UserUpdateRequest(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None
    is_admin: Optional[bool] = None
    is_active: Optional[bool] = None


class AdminStatsResponse(BaseModel):
    total_users: int
    active_users: int
    total_tokens_used: int
    tokens_by_provider: TokensByProvider
