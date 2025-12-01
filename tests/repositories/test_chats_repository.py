import pytest
from sqlalchemy import select

from db.models import Chat, ChatInfo


class TestChatsRepository:

    @pytest.mark.asyncio
    async def test_upsert_chat_info(self, chats_repo, session):
        await chats_repo.upsert_chat_info(10, first_name="Name", username="UserName")

        q = await session.execute(select(ChatInfo))
        info = q.scalars().first()

        assert info.chat_id == 10
        assert info.username == "UserName"

    @pytest.mark.asyncio
    async def test_upsert_chat(self, chats_repo, session):
        await chats_repo.upsert_chat(5, {"title": "Chat"}, {"start_time": 9}, end_time=20)

        q = await session.execute(select(Chat))
        chat = q.scalars().first()

        assert chat.chat_id == 5
        assert chat.end_time == 20

    @pytest.mark.asyncio
    async def test_get_chat(self, chats_repo, session):
        session.add(Chat(chat_id=99, start_time=9, end_time=18))
        await session.commit()

        c = await chats_repo.get_chat(99)
        assert c is not None
        assert c.chat_id == 99
