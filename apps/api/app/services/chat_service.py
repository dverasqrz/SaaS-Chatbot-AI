
from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException, status, Query
from sqlmodel import Session, select, func

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


class ChatService:
    def __init__(self, session: Session, current_user: User):
        self.session = session
        self.current_user = current_user

    def list_conversations(self, workspace_id: str) -> list[ConversationResponse]:
        workspace = self.session.exec(
            select(Workspace).where(
                Workspace.id == workspace_id,
                Workspace.owner_user_id == self.current_user.id,
            )
        ).first()

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace não encontrado.",
            )

        rows = self.session.exec(
            select(Conversation)
            .where(
                Conversation.workspace_id == workspace_id,
                Conversation.user_id == self.current_user.id,
            )
            .order_by(Conversation.updated_at.desc())
        ).all()

        return [ConversationResponse(**row.model_dump()) for row in rows]

    def _delete_conversation_cascade(self, conversation: Conversation) -> None:
        msgs = self.session.exec(
            select(Message).where(Message.conversation_id == conversation.id)
        ).all()
        for m in msgs:
            self.session.delete(m)
        self.session.delete(conversation)

    def delete_conversation(self, conversation_id: str) -> None:
        conversation = self.session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == self.current_user.id,
            )
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversa não encontrada.",
            )

        self._delete_conversation_cascade(conversation)
        self.session.commit()

    def delete_conversations_many(self, data: ConversationIdsRequest) -> None:
        for cid in data.conversation_ids:
            conversation = self.session.exec(
                select(Conversation).where(
                    Conversation.id == cid,
                    Conversation.user_id == self.current_user.id,
                )
            ).first()
            if conversation:
                self._delete_conversation_cascade(conversation)
        self.session.commit()

    def create_conversation(self, data: ConversationCreateRequest) -> ConversationResponse:
        workspace = self.session.exec(
            select(Workspace).where(
                Workspace.id == data.workspace_id,
                Workspace.owner_user_id == self.current_user.id,
            )
        ).first()

        if not workspace:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Workspace não encontrado.",
            )

        conversation = Conversation(
            workspace_id=workspace.id,
            user_id=self.current_user.id,
            title=data.title.strip() or "Nova conversa",
        )
        self.session.add(conversation)
        self.session.commit()
        self.session.refresh(conversation)

        return ConversationResponse(**conversation.model_dump())

    def list_messages(self, conversation_id: str) -> list[MessageResponse]:
        conversation = self.session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == self.current_user.id,
            )
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversa não encontrada.",
            )

        messages = self.session.exec(
            select(Message)
            .where(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
        ).all()

        return [MessageResponse(**item.model_dump()) for item in messages]

    def add_message(self, conversation_id: str, data: MessageCreateRequest) -> MessageResponse:
        conversation = self.session.exec(
            select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == self.current_user.id,
            )
        ).first()

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversa não encontrada.",
            )

        prior_user_count = len(
            self.session.exec(
                select(Message).where(
                    Message.conversation_id == conversation_id,
                    Message.role == "user",
                )
            ).all()
        )

        message = Message(
            conversation_id=conversation_id,
            user_id=self.current_user.id,
            role=data.role,
            content=data.content,
            timestamp=datetime.now(timezone.utc),
        )
        self.session.add(message)

        # Se for a primeira mensagem do usuário, sugere um título
        if prior_user_count == 0 and data.role == "user":
            suggested_title = suggest_conversation_title(data.content)
            if suggested_title:
                conversation.title = suggested_title
                self.session.add(conversation)

        self.session.commit()
        self.session.refresh(message)
        self.session.refresh(conversation) # Refresh conversation to get updated title

        return MessageResponse(**message.model_dump())
