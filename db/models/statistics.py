from datetime import datetime

from db.base import Base
from sqlalchemy import BigInteger, String, Integer, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column

import logging

logger = logging.getLogger(__name__)


class Status(Enum):
    new = "new"
    in_progress = "in_progress"
    never_learn = "never_learn"
    learned = "learned"


class UsersStatistic(Base):
    __tablename__ = "users_statistics"

    user_id: Mapped[int] = mapped_column(BigInteger, ForeignKey("users.user_id"), primary_key=True)
    word_id: Mapped[int] = mapped_column(Integer,
                                         ForeignKey("words.word_id", ondelete="CASCADE"),
                                         primary_key=True)
    correct: Mapped[int | None] = mapped_column(Integer, nullable=True)
    wrong: Mapped[int | None] = mapped_column(Integer, nullable=True)
    status: Mapped[Enum[Status] | None] = mapped_column(String, nullable=True)
    status_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
