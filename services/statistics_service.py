import datetime

from db.repositories.statistics import StatisticsRepository
from services.base_service import BaseService


class StatisticsService(BaseService):
    def __init__(self, context, word_management_service, stats_repo: StatisticsRepository):
        super().__init__(context)
        self.word_management_service = word_management_service
        self.repo = stats_repo

    async def get_statistics_description(self, chat_id: int) -> str:
        chat_stat: None | dict = await self.repo.get_chat_statistic(chat_id)
        if chat_stat is None:
            return self.i18n.error.no.stat()
        else:
            return self.i18n.stat.description(**chat_stat)

    async def save_statistic(self, chat_id: int, word_id: int, correct: int = 0, wrong: int = 0):
        await self.repo.save_statistic_by_word(chat_id, word_id, correct, wrong)
        await self.word_management_service.update_current_words(chat_id, word_id)

    async def save_event(self, chat_id: int, date: datetime.date):
        await self.repo.upsert_chat_event_stat(chat_id, date)
