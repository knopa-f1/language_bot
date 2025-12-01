import datetime

import pytest
from sqlalchemy import select

from db.models import ChatStatistic, Status
from db.models.statistics import ChatActivityStatistic


class TestStatisticsRepository:

    @pytest.mark.asyncio
    async def test_save_statistic_by_word(self, stats_repo, session):
        await stats_repo.save_statistic_by_word(10, 1, correct=2, wrong=1)

        q = await session.execute(select(ChatStatistic))
        row = q.scalars().first()

        assert row.correct == 2
        assert row.wrong == 1
        assert row.status == Status.in_progress

    @pytest.mark.asyncio
    async def test_change_word_status(self, stats_repo, session):
        await stats_repo.change_word_status(10, 1, Status.learned)

        q = await session.execute(select(ChatStatistic))
        row = q.scalars().first()
        assert row.status == Status.learned

    @pytest.mark.asyncio
    async def test_should_del_current_word(self, stats_repo, session):
        session.add(ChatStatistic(chat_id=10, word_id=1, correct=5, wrong=0))
        await session.commit()

        result = await stats_repo.should_del_current_word(10, 1, 3, 0.9)
        assert result is True

    @pytest.mark.asyncio
    async def test_get_chat_statistic(self, stats_repo, session):
        session.add(ChatStatistic(chat_id=10, word_id=1, correct=3, wrong=2, status=Status.learned))
        await session.commit()

        stat = await stats_repo.get_chat_statistic(10)

        assert stat["all"] == 5
        assert stat["correct"] == 3
        assert stat["learned"] == 1

    @pytest.mark.asyncio
    async def test_upsert_chat_event_stat(self, stats_repo, session):
        await stats_repo.upsert_chat_event_stat(10, date=datetime.date(2024, 1, 1))

        q = await session.execute(select(ChatActivityStatistic))
        row = q.scalars().first()
        assert row.event_count == 1
