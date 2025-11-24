from db.base import Base
from db.models import ChatCurrentWord, ChatInfo, ChatStatistic, User, Word

__all__ = ["Base", "User", "Word", "ChatStatistic", "ChatCurrentWord", "ChatInfo"]
