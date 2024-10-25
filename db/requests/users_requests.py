from typing import cast

from sqlalchemy import select, and_
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import User
import logging

logger = logging.getLogger(__name__)


async def upsert_user(
        session: AsyncSession,
        user_id: int,
        default_user_settings: dict,
        **kwargs
) -> None:
    kwargs["user_id"] = user_id
    default_user_settings.update(kwargs)

    stmt = upsert(User).values(default_user_settings)
    stmt = stmt.on_conflict_do_update(
        index_elements=['user_id'],
        set_=kwargs,
    )
    await session.execute(stmt)
    await session.commit()


async def get_user(
        session: AsyncSession,
        user_id: int
) -> User | None:

    user = await session.get(
        User, {"user_id": user_id}
    )
    return user


async def get_users_to_reminder(
        session: AsyncSession,
        current_hour: int
) -> list[User]:
    stmt = select(User).where(and_(
        User.start_time <= current_hour,
        User.end_time >= current_hour,
        (current_hour - User.start_time) % User.frequency == 0)
    )
    result = await session.execute(stmt)
    users = result.scalars().all()
    users = cast(list[User], users)
    return users



