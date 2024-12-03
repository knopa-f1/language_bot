from services.statistics_service import StatisticsService
from services.user_chat_service import UserChatService
from services.word_management_service import WordManagementService


class ServiceFactory:
    def __init__(self, context):
        self.context = context
        self._user_chat_service = None
        self._word_management_service = None
        self._statistics_service = None

    def create_user_chat_service(self) -> UserChatService:
        if not self._user_chat_service:
            self._user_chat_service = UserChatService(self.context)
        return self._user_chat_service

    def create_word_management_service(self) -> WordManagementService:
        if not self._word_management_service:
            self._word_management_service = WordManagementService(self.context, self.create_user_chat_service())
        return self._word_management_service

    def create_statistics_service(self) -> StatisticsService:
        if not self._statistics_service:
            self._statistics_service = StatisticsService(self.context, self.create_word_management_service())
        return self._statistics_service
