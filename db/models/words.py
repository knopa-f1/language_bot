

from db.base import Base
from sqlalchemy import BigInteger, String, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
import logging

logger = logging.getLogger(__name__)


class WordType(Enum):
    noun = "noun"
    verb = "verb"
    adjective = "adjective"
    adverb = "adverb"
    numeral = "numeral"
    phrase = "phrase"
    particle = "particle"
    pronoun = "pronoun"



class Word(Base):
    __tablename__ = "words"

    word_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    word: Mapped[str | None] = mapped_column(String, index=True)
    type: Mapped[Enum[WordType] | None] = mapped_column(String, index=True, nullable=True)
    translation_ru: Mapped[str | None] = mapped_column(String, index=True)
    translation_en: Mapped[str | None] = mapped_column(String, index=True)
    example: Mapped[str | None] = mapped_column(String)
    example_ru: Mapped[str | None] = mapped_column(String)
    example_en: Mapped[str | None] = mapped_column(String)

    chats = relationship('ChatCurrentWord', back_populates='word')


class ChatCurrentWord(Base):
    __tablename__ = "chats_current_words"

    chat_id: Mapped[int] = mapped_column(BigInteger,
                                         ForeignKey("chats.chat_id", ondelete="CASCADE"),
                                         primary_key=True)
    word_id: Mapped[int] = mapped_column(BigInteger,
                                         ForeignKey("words.word_id", ondelete="CASCADE"),
                                         primary_key=True)

    word: Mapped["Word"] = relationship("Word", back_populates="chats")
    chat: Mapped["Chat"] = relationship("Chat", back_populates="words")
