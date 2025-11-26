import logging
from typing import cast

from sqlalchemy import and_, case, func, select
from sqlalchemy.dialects.postgresql import insert as upsert
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import Chat, ChatInfo
from db.repositories.base import BaseRepository

logger = logging.getLogger(__name__)


class ChatsRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(session)

    async def upsert_chat_info(self, chat_id: int, **kwargs) -> None:
        kwargs["chat_id"] = chat_id
        stmt = upsert(ChatInfo).values(kwargs)
        stmt = stmt.on_conflict_do_update(
            index_elements=["chat_id"],
            set_=kwargs,
        )

        await self.session.execute(stmt)
        await self.session.commit()

    async def upsert_chat(
        self,
        chat_id: int,
        chat_info: dict,
        default_chat_settings: dict,
        **kwargs,
    ) -> None:
        kwargs["chat_id"] = chat_id
        default_chat_settings.update(kwargs)

        stmt = upsert(Chat).values(default_chat_settings)
        stmt = stmt.on_conflict_do_update(
            index_elements=["chat_id"],
            set_=kwargs,
        )
        await self.session.execute(stmt)
        await self.session.commit()

        await self.upsert_chat_info(chat_id, **chat_info)

    async def get_chat(self, chat_id: int) -> Chat | None:
        chat = await self.session.get(Chat, {"chat_id": chat_id})
        return chat

    async def get_chats_to_reminder(self, current_hour: int) -> list[Chat]:
        stmt = select(Chat).where(
            and_(
                Chat.start_time <= current_hour,
                Chat.end_time >= current_hour,
                func.coalesce(Chat.blocked_bot, False) == False,
                case(
                    (Chat.frequency == 0, False),
                    else_=(current_hour - Chat.start_time) % Chat.frequency == 0,
                ),
            )
        )
        result = await self.session.execute(stmt)
        chats = result.scalars().all()
        chats = cast(list[Chat], chats)
        return chats
