import logging

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from db.base import Base

logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    chat_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    first_name: Mapped[str | None] = mapped_column(String, nullable=True)
    last_name: Mapped[str | None] = mapped_column(String, nullable=True)
    username: Mapped[str | None] = mapped_column(String, nullable=True)
    language_code: Mapped[str | None] = mapped_column(String, nullable=True)

    @classmethod
    def props(cls):
        return [
            attr
            for attr in cls.__dict__
            if not callable(getattr(cls, attr)) and not attr.startswith("_") and not attr.endswith("_id")
        ]
