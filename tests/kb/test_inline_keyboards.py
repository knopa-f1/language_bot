import pytest
from unittest.mock import Mock

from keyboards.inline_keyboards import create_inline_kb, Keyboards


class TestKeyboards:
    @pytest.fixture
    def i18n(self):
        mock = Mock()
        mock.get = lambda key: f"txt-{key}"

        mock.button = Mock()
        mock.button.cancel = Mock()
        mock.button.cancel.learning = lambda: "cancel-learning"
        mock.button.next = lambda: "next"

        mock.schedule = Mock()
        mock.schedule.message = lambda: "schedule-msg"

        mock.error = Mock()
        mock.error.no = Mock()
        mock.error.no.current = Mock()
        mock.error.no.current.word = lambda: "no-current-word"

        mock.settings = Mock()
        mock.settings.desctiption = lambda **kw: "settings-desc"

        return mock

    # ===================================================================
    # create_inline_kb
    # ===================================================================

    def test_create_inline_kb_basic(self, i18n):
        kb = create_inline_kb(2, i18n, "button-a", "button-b")
        rows = kb.inline_keyboard

        assert len(rows) == 1
        assert len(rows[0]) == 2
        assert rows[0][0].callback_data == "button-a"
        assert rows[0][1].callback_data == "button-b"

    def test_create_inline_kb_last_btn(self, i18n):
        kb = create_inline_kb(2, i18n, "button-a", last_btn="button-cancel")
        rows = kb.inline_keyboard

        assert rows[1][0].callback_data == "button-cancel"

    # ===================================================================
    # Simple keyboards
    # ===================================================================

    def test_start_keyboard(self, i18n):
        kb = Keyboards.start_keyboard(i18n)
        rows = kb.inline_keyboard
        cbs = [btn.callback_data for r in rows for btn in r]

        assert set(cbs) == {
            "button-settings",
            "button-statistics",
            "button-start",
        }

    def test_reminder_keyboard(self, i18n):
        kb = Keyboards.reminder_keyboard(i18n)
        rows = kb.inline_keyboard

        assert rows[0][0].callback_data == "button-reminder"

    def test_stat_keyboard(self, i18n):
        kb = Keyboards.stat_keyboard(i18n)
        rows = kb.inline_keyboard
        cbs = [btn.callback_data for r in rows for btn in r]

        assert set(cbs) == {"button-settings", "button-start"}

    # ===================================================================
    # settings_keyboard
    # ===================================================================

    def test_settings_keyboard(self, i18n):
        kb = Keyboards.settings_keyboard(i18n)
        rows = kb.inline_keyboard
        cbs = [btn.callback_data for r in rows for btn in r]

        for key in (
            "button-change-time",
            "button-change-frequency",
            "button-change-word-count",
            "button-change-language",
        ):
            assert key in cbs

        assert "button-cancel-settings" in cbs

    # ===================================================================
    # time_keyboard / frequency_keyboard
    # ===================================================================

    def test_time_keyboard(self, i18n):
        kb = Keyboards.time_keyboard(i18n, pref="btn", start=0, end=2)
        rows = kb.inline_keyboard
        cbs = [btn.callback_data for r in rows for btn in r]

        assert set(cbs) == {
            "btn_0",
            "btn_1",
            "btn_2",
            "button-cancel-settings",
        }

    def test_frequency_keyboard(self, i18n):
        kb = Keyboards.frequency_keyboard(i18n, start=0, end=1)
        rows = kb.inline_keyboard
        cbs = [btn.callback_data for r in rows for btn in r]

        assert set(cbs) == {
            "button-frequency_0",
            "button-frequency_1",
            "button-cancel-settings",
        }

    # ===================================================================
    # language keyboards
    # ===================================================================

    def test_language_keyboard(self, i18n):
        kb = Keyboards.language_keyboard(i18n)
        rows = kb.inline_keyboard
        cbs = [btn.callback_data for r in rows for btn in r]

        # based on Language enum
        assert "button-language_ru" in cbs
        assert "button-language_en" in cbs
        assert "button-cancel-settings" in cbs

    def test_language_start_keyboard(self, i18n):
        kb = Keyboards.language_start_keyboard(i18n)
        rows = kb.inline_keyboard
        cbs = [btn.callback_data for r in rows for btn in r]

        assert "button-language-start_ru" in cbs
        assert "button-language-start_en" in cbs

    # ===================================================================
    # word_count_keyboard
    # ===================================================================

    def test_word_count_keyboard(self, i18n):
        class DS:
            answer_set = Mock()
            answer_set.vars_count_current = [3, 5]

        kb = Keyboards.word_count_keyboard(i18n, DS())
        rows = kb.inline_keyboard
        cbs = [btn.callback_data for r in rows for btn in r]

        assert "button-word-count_3" in cbs
        assert "button-word-count_5" in cbs
        assert "button-cancel-settings" in cbs

    # ===================================================================
    # guess_word_keyboard
    # ===================================================================

    def test_guess_word_keyboard(self, i18n):
        class W:
            def __init__(self, wid, word, tr):
                self.word_id = wid
                self.word = word
                self.translation_ru = tr

        words = [
            W(1, "a", "A"),
            W(2, "b", "B"),
        ]

        kb = Keyboards.guess_word_keyboard(i18n, words, type_id=1, correct_id=1, lang="ru")
        rows = kb.inline_keyboard
        cbs = [btn.callback_data for r in rows for btn in r]

        assert "button-word_1_1_1_1" in cbs
        assert "button-word_2_1_1_0" in cbs

    # ===================================================================
    # letters_keyboard
    # ===================================================================

    def test_letters_keyboard(self, i18n):
        letters = [(0, "c"), (1, "a"), (2, "t")]

        kb = Keyboards.letters_keyboard(i18n, word_id=5, shuffled_letters=letters)
        rows = kb.inline_keyboard
        cbs = [btn.callback_data for r in rows for btn in r]

        assert "button-letter_5_0" in cbs
        assert "button-letter_5_1" in cbs
        assert "button-letter_5_2" in cbs
        assert "button-cancel-learning" in cbs

    # ===================================================================
    # answer_word_keyboard
    # ===================================================================

    def test_answer_word_keyboard(self, i18n):
        info = Mock()
        info.correct_id = 1
        info.type_id = 2
        info.correct = True

        kb = Keyboards.answer_word_keyboard(i18n, info)
        rows = kb.inline_keyboard
        cbs = [btn.callback_data for r in rows for btn in r]

        assert "button-cancel-learning" in cbs
        assert "button-already-learned_1_2_1" in cbs
        assert "button-next" in cbs
