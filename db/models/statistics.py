from datetime import datetime

from db.base import Base
from sqlalchemy import BigInteger, String, Integer, DateTime, ForeignKey, Enum, Date
from sqlalchemy.orm import Mapped, mapped_column

import logging

logger = logging.getLogger(__name__)


class Status(Enum):
    new = "new"
    in_progress = "in_progress"
    never_learn = "never_learn"
    already_know = "already_know"
    learned = "learned"


class ChatStatistic(Base):
    __tablename__ = "chats_statistics"

    chat_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("chats.chat_id", ondelete="CASCADE"), primary_key=True)
    word_id: Mapped[int] = mapped_column(Integer,
                                         ForeignKey("words.word_id", ondelete="CASCADE"),
                                         primary_key=True)
    correct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wrong: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[Enum[Status] | None] = mapped_column(String, nullable=True, index=True)
    status_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)


class ChatActivityStatistic(Base):
    __tablename__ = "chats_event_statistics"

    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    date: Mapped[datetime] = mapped_column(Date, primary_key=True, index=True)
    event_count: Mapped[int] = mapped_column(Integer, index=True)
