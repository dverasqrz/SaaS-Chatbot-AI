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
from app.utils.conversation_title import suggest_conversation_title

router = APIRouter(prefix="/chats", tags=["chats"])


@router.get("/conversations", response_model=list[ConversationResponse])
def list_conversations(
    workspace_id: str = Query(..., description="ID do workspace"),
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    workspace = session.exec(
        select(Workspace).where(
            Workspace.id == workspace_id,
            Workspace.owner_user_id == current_user.id,
        )
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace não encontrado.",
        )

    rows = session.exec(
        select(Conversation)
        .where(
            Conversation.workspace_id == workspace_id,
            Conversation.user_id == current_user.id,
        )
        .order_by(Conversation.updated_at.desc())
    ).all()

    return [ConversationResponse(**row.model_dump()) for row in rows]


def _delete_conversation_cascade(session: Session, conversation: Conversation) -> None:
    msgs = session.exec(
        select(Message).where(Message.conversation_id == conversation.id)
    ).all()
    for m in msgs:
        session.delete(m)
    session.delete(conversation)


@router.delete("/conversations/{conversation_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversation(
    conversation_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada.",
        )

    _delete_conversation_cascade(session, conversation)
    session.commit()
    return None


@router.post("/conversations/delete-many", status_code=status.HTTP_204_NO_CONTENT)
def delete_conversations_many(
    data: ConversationIdsRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    for cid in data.conversation_ids:
        conversation = session.exec(
            select(Conversation).where(
                Conversation.id == cid,
                Conversation.user_id == current_user.id,
            )
        ).first()
        if conversation:
            _delete_conversation_cascade(session, conversation)
    session.commit()
    return None


@router.post("/conversations", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    data: ConversationCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    workspace = session.exec(
        select(Workspace).where(
            Workspace.id == data.workspace_id,
            Workspace.owner_user_id == current_user.id,
        )
    ).first()

    if not workspace:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Workspace não encontrado.",
        )

    conversation = Conversation(
        workspace_id=workspace.id,
        user_id=current_user.id,
        title=data.title.strip() or "Nova conversa",
    )
    session.add(conversation)
    session.commit()
    session.refresh(conversation)

    return ConversationResponse(**conversation.model_dump())


@router.get("/conversations/{conversation_id}/messages", response_model=list[MessageResponse])
def list_messages(
    conversation_id: str,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada.",
        )

    messages = session.exec(
        select(Message)
        .where(Message.conversation_id == conversation_id)
        .order_by(Message.created_at.asc())
    ).all()

    return [MessageResponse(**item.model_dump()) for item in messages]


@router.post("/conversations/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def add_message(
    conversation_id: str,
    data: MessageCreateRequest,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    conversation = session.exec(
        select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == current_user.id,
        )
    ).first()

    if not conversation:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Conversa não encontrada.",
        )

    prior_user_count = len(
        session.exec(
            select(Message).where(
                Message.conversation_id == conversation_id,
                Message.role == "user",
            )
        ).all()
    )

    message = Message(
        conversation_id=conversation_id,
        role=data.role,
        content=data.content.strip(),
        model=data.model,
        provider=data.provider,
    )
    session.add(message)

    if data.role == "user" and prior_user_count == 0:
        conversation.title = suggest_conversation_title(data.content)
    conversation.updated_at = datetime.now(timezone.utc)
    session.add(conversation)

    session.commit()
    session.refresh(message)

    return MessageResponse(**message.model_dump())
