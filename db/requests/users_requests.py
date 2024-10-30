from db import User
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.dialects.postgresql import insert as upsert


async def upsert_user(
        session: AsyncSession,
        user_id: int,
        chat_id: int,
        user_info: dict
) -> None:
    user_info["user_id"] = user_id
    user_info["chat_id"] = chat_id
    stmt = upsert(User).values(user_info)
    stmt = stmt.on_conflict_do_nothing()

    await session.execute(stmt)
    await session.commit()


async def get_user(
        session: AsyncSession,
        user_id: int,
        chat_id: int
) -> User | None:
    user = await session.get(
        User, {"chat_id": chat_id,
               "user_id": user_id}
    )
    return user
