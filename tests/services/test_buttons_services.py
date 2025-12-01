import pytest
from unittest.mock import AsyncMock

from services.buttons_services import (
    get_selected_data,
    get_selected_end_time,
    ButtonWord,
)


class TestButtonHelpers:
    def test_get_selected_data(self):
        assert get_selected_data("btn_abc_123") == "123"
        assert get_selected_data("hello_world") == "world"
        assert get_selected_data("one") == "one"

    def test_get_selected_end_time(self):
        assert get_selected_end_time("prefix_10_20") == ("10", "20")
        assert get_selected_end_time("x_y_z") == ("y", "z")


class TestButtonWordParse:
    def test_button_word_parse_type_1_or_2(self):
        """
        button-word_{word_id}_{correct_id}_{type_id}_{correct}
        """
        b = ButtonWord(
            chat_id=99,
            callback_data="button-word_10_20_2_1",
        )

        assert b.chat_id == 99
        assert b.word_id == 10
        assert b.correct_id == 20
        assert b.type_id == 2
        assert b.correct is True

    def test_button_word_parse_incorrect(self):
        b = ButtonWord(
            chat_id=1,
            callback_data="button-word_5_5_1_0",
        )

        assert b.correct is False

    def test_button_already_learned(self):
        """
        button-already-learned_{word_id}_{type_id}
        """
        b = ButtonWord(
            chat_id=5,
            callback_data="button-already-learned_42_1",
        )

        assert b.word_id == 42
        assert b.correct_id == 42
        assert b.type_id == 1
        assert b.correct is True

    def test_button_letter(self):
        """
        button-letter_{word_id}_{index}
        """
        b = ButtonWord(
            chat_id=7,
            callback_data="button-letter_100_3",
        )

        assert b.word_id == 100
        assert b.correct_id == 100
        assert b.type_id == 3
        assert b.index == 3
        assert b.correct is None


class TestButtonWordMethods:
    @pytest.fixture
    def word_service(self):
        svc = AsyncMock()
        svc.process_word = AsyncMock(return_value="WORD_RESULT")
        svc.process_letters = AsyncMock(return_value=("TEXT", "KB"))
        svc.mark_word_as_never_learn = AsyncMock()
        svc.mark_word_as_already_know = AsyncMock()
        return svc

    @pytest.fixture
    def stats_service(self):
        svc = AsyncMock()
        return svc

    @pytest.mark.asyncio
    async def test_answer_message_for_word(self, word_service, stats_service):
        b = ButtonWord(10, "button-word_3_3_1_1")

        res = await b.answer_message_for_word(word_service, stats_service)

        word_service.process_word.assert_called_once()
        assert res == "WORD_RESULT"

    @pytest.mark.asyncio
    async def test_answer_message_for_letter(self, word_service, stats_service):
        b = ButtonWord(10, "button-letter_5_2")

        res = await b.answer_message_for_letter(word_service, stats_service)

        word_service.process_letters.assert_called_once()
        assert res == ("TEXT", "KB")

    @pytest.mark.asyncio
    async def test_mark_word_as_never_learn_default(self, word_service):
        b = ButtonWord(9, "button-word_10_10_1_1")

        await b.mark_word_as_never_learn(word_service)

        word_service.mark_word_as_never_learn.assert_called_once_with(9, 10)

    @pytest.mark.asyncio
    async def test_mark_word_as_never_learn_learned_type_1(self, word_service):
        b = ButtonWord(9, "button-word_10_10_1_1")

        await b.mark_word_as_never_learn(word_service, learned_type=1)

        word_service.mark_word_as_already_know.assert_called_once_with(9, 10)
