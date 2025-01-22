from datetime import datetime
from uuid import UUID, uuid4

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Text,
    func,
    Enum,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base


class Thread(Base):
    __tablename__ = 'thread'

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, default=uuid4, index=True)
    title: Mapped[str] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=func.now(),
        onupdate=func.now(),
        index=True
    )

    user_id: Mapped[UUID] = mapped_column(ForeignKey('user.id'))

    messages: Mapped[list['Message']] = relationship(back_populates='thread', order_by='asc(Message.created_at)')
    user: Mapped['User'] = relationship(back_populates='threads')


class Message(Base):
    __tablename__ = 'message'

    id: Mapped[UUID] = mapped_column(primary_key=True, unique=True, default=uuid4, index=True)
    role: Mapped[str] = mapped_column(
        Enum("user", "assistant", "tool", name="chat_role_enum", create_type=False),
        default='user'
    )
    content: Mapped[str] = mapped_column(Text)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), default=func.now(), index=True)

    thread_id: Mapped[UUID] = mapped_column(ForeignKey('thread.id'))

    thread: Mapped['Thread'] = relationship('Thread', back_populates='messages')


