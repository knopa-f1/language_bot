from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

from db import User
from db.repositories.base import BaseRepository


class UsersRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def upsert_user(self, user_id: int, chat_id: int, user_info: dict) -> None:
        user_info["user_id"] = user_id
        user_info["chat_id"] = chat_id
        stmt = upsert(User).values(user_info)
        stmt = stmt.on_conflict_do_nothing()

        await self.session.execute(stmt)
        await self.session.commit()

    async def get_user(self, user_id: int, chat_id: int) -> User | None:
        user = await self.session.get(User, {"chat_id": chat_id, "user_id": user_id})
        return user
