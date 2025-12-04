from db.repositories.chats import ChatsRepository
from db.repositories.statistics import StatisticsRepository
from db.repositories.users import UsersRepository
from db.repositories.words import WordsRepository
from services.statistics_service import StatisticsService
from services.user_chat_service import UserChatService
from services.word_management_service import WordManagementService


class ServiceFactory:
    def __init__(self, global_context):
        self.global_context = global_context

    @staticmethod
    def _create_chats_repo(session) -> ChatsRepository:
        return ChatsRepository(session)

    @staticmethod
    def _create_users_repo(session) -> UsersRepository:
        return UsersRepository(session)

    @staticmethod
    def _create_words_repo(session) -> WordsRepository:
        return WordsRepository(session)

    @staticmethod
    def _create_statistics_repo(session) -> StatisticsRepository:
        return StatisticsRepository(session)

    def create_user_chat_service(self, request_context) -> UserChatService:
        return UserChatService(
            global_context=self.global_context,
            request_context=request_context,
            chats_repo=self._create_chats_repo(request_context.session),
            users_repo=self._create_users_repo(request_context.session),
        )

    def create_word_management_service(self, request_context) -> WordManagementService:
        return WordManagementService(
            global_context=self.global_context,
            request_context=request_context,
            user_chat_service=self.create_user_chat_service(request_context),
            words_repo=self._create_words_repo(request_context.session),
            stats_repo=self._create_statistics_repo(request_context.session),
        )

    def create_statistics_service(self, request_context) -> StatisticsService:
        return StatisticsService(
            global_context=self.global_context,
            request_context=request_context,
            word_management_service=self.create_word_management_service(request_context),
            stats_repo=self._create_statistics_repo(request_context.session),
        )
