import pytest
from sqlalchemy import select

from db.models import User


class TestUsersRepository:

    @pytest.mark.asyncio
    async def test_upsert_user(self, users_repo, session):
        await users_repo.upsert_user(5, 10, {"first_name": "Ivan"})
        q = await session.execute(select(User))
        rows = q.scalars().all()
        assert len(rows) == 1
        assert rows[0].user_id == 5
        assert rows[0].chat_id == 10

    @pytest.mark.asyncio
    async def test_get_user(self, users_repo, session):
        session.add(User(user_id=7, chat_id=77, first_name="Test"))
        await session.commit()

        user = await users_repo.get_user(7, 77)
        assert user is not None
        assert user.first_name == "Test"
