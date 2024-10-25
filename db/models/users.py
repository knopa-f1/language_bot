from db.base import Base
from sqlalchemy import BigInteger, String, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
import logging

logger = logging.getLogger(__name__)


class User(Base):
    __tablename__ = "users"

    user_id: Mapped[int] = mapped_column(BigInteger, primary_key=True)
    frequency: Mapped[int | None] = mapped_column(Integer, nullable=True)
    start_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    end_time: Mapped[int | None] = mapped_column(Integer, nullable=True)
    lang: Mapped[str | None] = mapped_column(String, nullable=True)

    words = relationship('UserCurrentWord', back_populates='user')

    @property
    def attributes_dict(self):
        return {str(k): v for k, v in vars(self).items() if not k.startswith('_')}
