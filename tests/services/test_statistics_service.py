import datetime
import pytest
from unittest.mock import AsyncMock

from services.statistics_service import StatisticsService


class TestStatisticsService:
    @pytest.fixture
    def stats_repo(self):
        repo = AsyncMock()
        repo.get_chat_statistic = AsyncMock()
        repo.save_statistic_by_word = AsyncMock()
        repo.upsert_chat_event_stat = AsyncMock()
        return repo

    @pytest.fixture
    def word_management_service(self):
        svc = AsyncMock()
        svc.update_current_words = AsyncMock()
        return svc

    @pytest.fixture
    def service(self, global_context, request_context, word_management_service, stats_repo):
        return StatisticsService(
            global_context=global_context,
            request_context=request_context,
            word_management_service=word_management_service,
            stats_repo=stats_repo,
        )

    @pytest.mark.asyncio
    async def test_get_statistics_description(self, service, stats_repo, request_context):
        stats_repo.get_chat_statistic.return_value = None

        result = await service.get_statistics_description(chat_id=123)

        stats_repo.get_chat_statistic.assert_called_once_with(123)
        request_context.i18n.stat.description.assert_called_once()
        assert result == request_context.i18n.error.no.stat()

    @pytest.mark.asyncio
    async def test_save_statistic(self, service, stats_repo, word_management_service):
        await service.save_statistic(chat_id=1, word_id=2, correct=3, wrong=4)
        stats_repo.save_statistic_by_word.assert_called_once_with(1, 2, 3, 4)
        word_management_service.update_current_words.assert_called_once_with(1, 2)

    @pytest.mark.asyncio
    async def test_save_event(self, service, stats_repo):
        date = datetime.date(2025, 1, 1)
        await service.save_event(chat_id=77, date=date)
        stats_repo.upsert_chat_event_stat.assert_called_once_with(77, date)
