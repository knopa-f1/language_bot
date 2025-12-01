import pytest
from unittest.mock import AsyncMock, Mock

from services.word_management_service import WordManagementService
from db.models import Status


class TestWordManagementService:
    @pytest.fixture
    def words_repo(self):
        repo = AsyncMock()
        repo.exists_short_word = AsyncMock(return_value=True)
        repo.get_words = AsyncMock()
        repo.get_word_by_id = AsyncMock()
        repo.add_current_chat_words = AsyncMock()
        repo.delete_current_word = AsyncMock()
        repo.current_words_exists = AsyncMock(return_value=True)
        repo.delete_random_current_words = AsyncMock()
        return repo

    @pytest.fixture
    def stats_repo(self):
        repo = AsyncMock()
        repo.should_del_current_word = AsyncMock()
        repo.change_word_status = AsyncMock()
        return repo

    @pytest.fixture
    def user_chat_service(self):
        svc = AsyncMock()
        svc.get_chat_settings = AsyncMock(return_value=3)
        svc.set_chat_settings = AsyncMock()
        return svc

    @pytest.fixture
    def service(self, context, user_chat_service, words_repo, stats_repo):
        return WordManagementService(
            context=context,
            user_chat_service=user_chat_service,
            words_repo=words_repo,
            stats_repo=stats_repo,
        )

    def test_letters_state(self, service, cache):
        service._letters_set_state(1, {"x": 1})
        cache.set_chat_settings.assert_called_with(1, letters_state={"x": 1})

        service._letters_clear_state(1)
        cache.set_chat_settings.assert_called_with(1, letters_state=None)

    def test_shuffle_letters_with_positions(self, service):
        result = service._shuffle_letters_with_positions("a b")
        assert isinstance(result, list)
        assert all(len(t) == 2 for t in result)

    @pytest.mark.asyncio
    async def test_set_count_current_words_increase(self, service, user_chat_service, words_repo):
        user_chat_service.get_chat_settings.return_value = 2

        await service.set_count_current_words(Mock(id=10), 5)

        words_repo.add_current_chat_words.assert_called_once()
        user_chat_service.set_chat_settings.assert_called()

    @pytest.mark.asyncio
    async def test_set_count_current_words_decrease(self, service, user_chat_service, words_repo):
        user_chat_service.get_chat_settings.return_value = 6

        await service.set_count_current_words(Mock(id=10), 3)

        words_repo.delete_random_current_words.assert_called_once_with(10, 3)

    @pytest.mark.asyncio
    async def test_update_current_words_del_word(self, service, words_repo, stats_repo):
        await service.update_current_words(1, 2, del_word=True)

        words_repo.delete_current_word.assert_called_once_with(1, 2)
        stats_repo.change_word_status.assert_called_once_with(1, 2, Status.never_learn)

    @pytest.mark.asyncio
    async def test_update_current_words_already_know(self, service, words_repo, stats_repo):
        await service.update_current_words(1, 2, del_word=True, already_know=True)

        stats_repo.change_word_status.assert_called_once_with(1, 2, Status.already_know)

    @pytest.mark.asyncio
    async def test_update_current_words_should_delete(self, service, words_repo, stats_repo):
        stats_repo.should_del_current_word.return_value = True

        await service.update_current_words(1, 2)

        stats_repo.change_word_status.assert_called_once_with(1, 2, Status.learned)

    @pytest.mark.asyncio
    async def test_update_current_words_no_action(self, service, stats_repo, words_repo):
        stats_repo.should_del_current_word.return_value = False

        await service.update_current_words(1, 2)

        stats_repo.change_word_status.assert_not_called()
        words_repo.delete_current_word.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_words_to_learn(self, service, words_repo):
        words_repo.get_words.return_value = {"x": 1}

        result = await service.get_words_to_learn(10)

        words_repo.get_words.assert_called_once()
        assert result == {"x": 1}

    @pytest.mark.asyncio
    async def test_prepare_words_type_1_or_2(self, service, words_repo, monkeypatch):
        class w:
            word = "test"
            word_id = 1
            translation_ru = "перевод"

        words_repo.get_words.return_value = {
            "variants": [],
            "correct_word": w,
        }

        monkeypatch.setattr("services.word_management_service.random.choice", lambda x: 1)

        res = await service.prepare_words_to_learn(10)

        assert "test" in res["message_text"]

    @pytest.mark.asyncio
    async def test_prepare_words_type_3_letters(self, service, words_repo, monkeypatch):
        class w:
            word = "cat"
            word_id = 2
            translation_ru = "кот"

        words_repo.get_words.return_value = {"correct_word": w, "variants": []}

        monkeypatch.setattr("services.word_management_service.random.choice", lambda x: 3)

        res = await service.prepare_words_to_learn(10)

        assert "кот" in res["message_text"]

    @pytest.mark.asyncio
    async def test_process_word_correct(self, service, words_repo):
        class w:
            translation_ru = "кот"
            word = "cat"
            example = "ex"
            example_ru = "пр"

        words_repo.get_word_by_id.return_value = w

        btn = Mock()
        btn.correct = True
        btn.chat_id = 10
        btn.word_id = 1
        btn.type_id = "1"

        stats = AsyncMock()

        text = await service.process_word(btn, stats)

        assert "кот" in text
        assert "cat" in text

    @pytest.mark.asyncio
    async def test_process_letters_correct_step(self, service, cache, words_repo):
        class w:
            word = "cat"
            word_id = 1
            translation_ru = "кот"

        words_repo.get_word_by_id.return_value = w

        cache.get_chat_settings.return_value = {
            "word_id": 1,
            "target": "cat",
            "current_pos": 0,
            "wrong_attempts": 0,
            "letters": [(0, "c"), (1, "a"), (2, "t")],
        }

        btn = Mock()
        btn.index = 0
        btn.chat_id = 10
        btn.word_id = 1

        stats = AsyncMock()

        text, kb = await service.process_letters(btn, stats)

        assert "кот" in text
