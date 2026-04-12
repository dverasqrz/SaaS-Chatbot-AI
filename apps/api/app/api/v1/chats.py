from __future__ import annotations

from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlmodel import Session, select

from app.api.deps import get_current_user
from app.core.db import get_session
from app.models.conversation import Conversation
from app.models.message import Message
from app.models.user import User
from app.models.workspace import Workspace
from app.schemas.chat import (
    ConversationCreateRequest,
    ConversationIdsRequest,
    ConversationResponse,
    MessageCreateRequest,
    MessageResponse,
)
from app.services.chat_service import ChatService
from app.utils.conversation_title import suggest_conversation_title

router = APIRouter(prefix="/chats", tags=["chats"])

def get_chat_service(
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
) -> ChatService:
    return ChatService(session, current_user)


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    workspace_id: str = Query(..., description="ID do workspace"),
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.list_conversations(workspace_id)





@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service),
):
    chat_service.delete_conversation(conversation_id)
    return None


@router.post("/conversations/delete-many", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversations_many(
    data: ConversationIdsRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    chat_service.delete_conversations_many(data)
    return None


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    data: ConversationCreateRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.create_conversation(data)


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
def list_messages(
    conversation_id: str,
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.list_messages(conversation_id)


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def add_message(
    conversation_id: str,
    data: MessageCreateRequest,
    chat_service: ChatService = Depends(get_chat_service),
):
    return chat_service.add_message(conversation_id, data)
