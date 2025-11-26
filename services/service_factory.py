from db.repositories.chats import ChatsRepository
from db.repositories.statistics import StatisticsRepository
from db.repositories.users import UsersRepository
from db.repositories.words import WordsRepository
from services.statistics_service import StatisticsService
from services.user_chat_service import UserChatService
from services.word_management_service import WordManagementService


class ServiceFactory:
    def __init__(self, context):
        self.context = context
        self._user_chat_service = None
        self._word_management_service = None
        self._statistics_service = None

    def _create_chats_repo(self) -> ChatsRepository:
        return ChatsRepository(self.context.session)

    def _create_users_repo(self) -> UsersRepository:
        return UsersRepository(self.context.session)

    def _create_words_repo(self) -> WordsRepository:
        return WordsRepository(self.context.session)

    def _create_statistics_repo(self) -> StatisticsRepository:
        return StatisticsRepository(self.context.session)

    def create_user_chat_service(self) -> UserChatService:
        if not self._user_chat_service:
            self._user_chat_service = UserChatService(
                context=self.context,
                chats_repo=self._create_chats_repo(),
                users_repo=self._create_users_repo(),
            )
        return self._user_chat_service

    def create_word_management_service(self) -> WordManagementService:
        if not self._word_management_service:
            self._word_management_service = WordManagementService(
                context=self.context,
                user_chat_service=self.create_user_chat_service(),
                words_repo=self._create_words_repo(),
                stats_repo=self._create_statistics_repo(),
            )
        return self._word_management_service

    def create_statistics_service(self) -> StatisticsService:
        if not self._statistics_service:
            self._statistics_service = StatisticsService(
                context=self.context,
                word_management_service=self.create_word_management_service(),
                stats_repo=self._create_statistics_repo(),
            )
        return self._statistics_service
