from __future__ import annotations

from fastapi import APIRouter

from app.api.v1 import admin, auth, chats, workspaces

api_router = APIRouter(prefix="/api/v1")

api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(chats.router, tags=["chats"])
api_router.include_router(workspaces.router, tags=["workspaces"])
api_router.include_router(admin.router, tags=["admin"])
