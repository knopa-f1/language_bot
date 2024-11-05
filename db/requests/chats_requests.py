from typing import cast

from db.models import Chat, ChatInfo
from sqlalchemy import select, and_, case, func
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

import logging

logger = logging.getLogger(__name__)


async def upsert_chat_info(session: AsyncSession,
                           chat_id: int,
                           **kwargs) -> None:
    kwargs["chat_id"] = chat_id
    stmt = upsert(ChatInfo).values(kwargs)
    stmt = stmt.on_conflict_do_update(
        index_elements=['chat_id'],
        set_=kwargs,
    )

    await session.execute(stmt)
    await session.commit()


async def upsert_chat(
        session: AsyncSession,
        chat_id: int,
        chat_info: dict,
        default_chat_settings: dict,
        **kwargs
) -> None:
    kwargs["chat_id"] = chat_id
    default_chat_settings.update(kwargs)

    stmt = upsert(Chat).values(default_chat_settings)
    stmt = stmt.on_conflict_do_update(
        index_elements=['chat_id'],
        set_=kwargs,
    )
    await session.execute(stmt)
    await session.commit()

    await upsert_chat_info(session, chat_id, **chat_info)


async def get_chat(
        session: AsyncSession,
        chat_id: int
) -> Chat | None:
    chat = await session.get(
        Chat, {"chat_id": chat_id}
    )
    return chat


async def get_chats_to_reminder(
        session: AsyncSession,
        current_hour: int
) -> list[Chat]:
    stmt = select(Chat).where(and_(
        Chat.start_time <= current_hour,
        Chat.end_time >= current_hour,
        func.coalesce(Chat.blocked_bot, False) == False,
        case(
            (Chat.frequency == 0, False),
            else_=(current_hour - Chat.start_time) % Chat.frequency == 0
        )
    )
    )
    result = await session.execute(stmt)
    chats = result.scalars().all()
    chats = cast(list[Chat], chats)
    return chats
