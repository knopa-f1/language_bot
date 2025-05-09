from datetime import datetime

from db.base import Base
from sqlalchemy import BigInteger, String, Integer, ForeignKey, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
import logging

logger = logging.getLogger(__name__)


class Chat(Base):
    __tablename__ = "chats"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    frequency: Mapped[int | None] = mapped_column(Integer)
    start_time: Mapped[int | None] = mapped_column(Integer)
    end_time: Mapped[int | None] = mapped_column(Integer)
    lang: Mapped[str | None] = mapped_column(String,  index=True)
    count_current: Mapped[int | None] = mapped_column(Integer)
    blocked_bot: Mapped[bool] = mapped_column(Boolean, nullable=True, server_default="False")

    words = relationship('ChatCurrentWord', back_populates='chat')

    @property
    def attributes_dict(self):
        return {str(k): v for k, v in vars(self).items() if not k.startswith('_')}


class ChatInfo(Base):
    __tablename__ = "chats_info"

    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chats.chat_id", ondelete="CASCADE"), primary_key=True)
    type: Mapped[str | None] = mapped_column(String)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    title: Mapped[str | None] = mapped_column(String, nullable=True)
    start_date: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), server_default='0001-01-01')

    @classmethod
    def props(cls):
        return [attr for attr in cls.__dict__ if
                not callable(getattr(cls, attr)) and not attr.startswith("_") and not attr.endswith("_id")]
