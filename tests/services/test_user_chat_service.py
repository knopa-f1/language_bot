import pytest
from unittest.mock import AsyncMock, Mock

from services.user_chat_service import UserChatService


class TestUserChatService:
    @pytest.fixture
    def chats_repo(self):
        repo = AsyncMock()
        repo.get_chat = AsyncMock()
        repo.upsert_chat = AsyncMock()
        repo.upsert_chat_info = AsyncMock()
        return repo

    @pytest.fixture
    def users_repo(self):
        repo = AsyncMock()
        repo.get_user = AsyncMock()
        repo.upsert_user = AsyncMock()
        return repo

    @pytest.fixture
    def service(self, global_context, request_context, chats_repo, users_repo):
        return UserChatService(global_context, request_context, chats_repo, users_repo)

    @pytest.mark.asyncio
    async def test_user_exists_cache_true(self, service):
        service.cache.user_exists = AsyncMock(return_value=True)

        result = await service.user_exists(10, 20)

        service.cache.user_exists.assert_called_once_with(10)
        assert result is True

    @pytest.mark.asyncio
    async def test_user_exists_from_repo(self, service, users_repo):
        service.cache.user_exists = AsyncMock(return_value=False)

        # users_repo.get_user returns user object
        user_obj = Mock()
        users_repo.get_user.return_value = user_obj
        service.cache.set_user = AsyncMock()

        result = await service.user_exists(10, 20)

        users_repo.get_user.assert_called_once_with(10, 20)
        service.cache.set_user.assert_called_once_with(10, 20)
        assert result is True

    @pytest.mark.asyncio
    async def test_user_exists_not_found(self, service, users_repo):
        service.cache.user_exists = AsyncMock(return_value=False)
        users_repo.get_user.return_value = None

        result = await service.user_exists(10, 20)

        assert result is False

    @pytest.mark.asyncio
    async def test_set_user(self, service, users_repo):
        user = Mock(id=5)
        service.cache.set_user = AsyncMock()

        # get_user_info returns some dict
        import services.user_chat_service as module

        module.get_user_info = lambda user: {"first_name": "Ivan"}

        await service.set_user(user, chat_id=10)

        service.cache.set_user.assert_called_once_with(5, 10)
        users_repo.upsert_user.assert_called_once_with(5, 10, {"first_name": "Ivan"})

    @pytest.mark.asyncio
    async def test_chat_settings_exists_true(self, service, chats_repo):
        chats_repo.get_chat.return_value = Mock()

        result = await service.chat_settings_exists(123)

        chats_repo.get_chat.assert_called_once_with(123)
        assert result is True

    @pytest.mark.asyncio
    async def test_chat_settings_exists_false(self, service, chats_repo):
        chats_repo.get_chat.return_value = None

        result = await service.chat_settings_exists(123)

        assert result is False

    @pytest.mark.asyncio
    async def test_get_chat_settings_from_cache(self, service):
        service.cache.get_chat_settings = AsyncMock(return_value="ru")

        result = await service.get_chat_settings(10, "lang")

        assert result == "ru"
        service.cache.get_chat_settings.assert_called_once_with(10, "lang")

    @pytest.mark.asyncio
    async def test_get_chat_settings_from_repo(self, service, chats_repo):
        service.cache.get_chat_settings = AsyncMock(return_value=None)
        service.cache.set_chat_settings = AsyncMock()

        chat = Mock(lang="en")
        chats_repo.get_chat.return_value = chat

        result = await service.get_chat_settings(10, "lang")

        chats_repo.get_chat.assert_called_once_with(10)
        service.cache.set_chat_settings.assert_called_once_with(10, lang="en")
        assert result == "en"

    @pytest.mark.asyncio
    async def test_get_chat_settings_no_chat(self, service, chats_repo):
        service.cache.get_chat_settings = AsyncMock(return_value=None)
        chats_repo.get_chat.return_value = None

        result = await service.get_chat_settings(10, "lang")

        assert result is None

    @pytest.mark.asyncio
    async def test_set_chat_settings(self, service, chats_repo):
        chat = Mock(id=7)
        service.cache.set_chat_settings = AsyncMock()

        # get_chat_info returns dict
        import services.user_chat_service as module

        module.get_chat_info = lambda chat: {"title": "TestChat"}

        await service.set_chat_settings(chat, notifications=True)

        service.cache.set_chat_settings.assert_called_once_with(7, notifications=True)
        chats_repo.upsert_chat.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_chat_settings_description_no_chat(self, service, chats_repo):
        chats_repo.get_chat.return_value = None

        # i18n override
        service.i18n = Mock()
        service.i18n.error = Mock()
        service.i18n.error.no = Mock()
        service.i18n.error.no.settings = lambda: "NO_SETTINGS"

        result = await service.get_chat_settings_description(1)

        assert result == "NO_SETTINGS"

    @pytest.mark.asyncio
    async def test_get_chat_settings_description_ok(self, service, chats_repo):
        chat = Mock(attributes_dict={"x": 1})
        chats_repo.get_chat.return_value = chat

        service.i18n = Mock()
        service.i18n.settings = Mock()
        service.i18n.settings.desctiption = Mock(return_value="DESC")

        result = await service.get_chat_settings_description(1)

        service.i18n.settings.desctiption.assert_called_once_with(**{"x": 1})
        assert result == "DESC"

    @pytest.mark.asyncio
    async def test_set_chat_info(self, service, chats_repo):
        chat = Mock(id=15)

        await service.set_chat_info(chat, mute=True, slow=True)

        chats_repo.upsert_chat_info.assert_called_once_with(15, mute=True, slow=True)
