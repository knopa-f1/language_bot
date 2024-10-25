from db.base import Base
from sqlalchemy import BigInteger, String, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import logging

logger = logging.getLogger(__name__)


class Word(Base):
    __tablename__ = "words"

    word_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    word: Mapped[str | None] = mapped_column(String, nullable=True)
    translation_ru: Mapped[str | None] = mapped_column(String, nullable=True)
    translation_en: Mapped[str | None] = mapped_column(String, nullable=True)
    example: Mapped[str | None] = mapped_column(String, nullable=True)

    users = relationship('UserCurrentWord', back_populates='word')


class UserCurrentWord(Base):
    __tablename__ = "users_current_words"

    user_id: Mapped[int] = mapped_column(BigInteger,
                                         ForeignKey("users.user_id", ondelete="CASCADE"),
                                         primary_key=True)
    word_id: Mapped[int] = mapped_column(BigInteger,
                                         ForeignKey("words.word_id", ondelete="CASCADE"),
                                         primary_key=True)

    word: Mapped["Word"] = relationship("Word", back_populates="users")
    user: Mapped["User"] = relationship("User", back_populates="words")
