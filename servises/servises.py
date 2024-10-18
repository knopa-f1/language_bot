from dataclasses import dataclass, field
from enum import Enum

from config_data.constants import DefaultSettings
from fluentogram import TranslatorRunner
from database.database import Database
import random
from keyboards.inline_keyboards import Keyboards


# Определение выбранного времени
def get_selected_data(data: str, pref: str = "button-start-time_"):
    return data.replace(pref, "")


def get_selected_end_time(data: str) -> tuple:
    data_lst = data.split("_")
    return data_lst[-2], data_lst[-1]


@dataclass
class WordInfo:
    user_id: int
    word_id: int
    type_id: int
    correct_id: int
    correct: bool = False

    def __init__(self, user_id: int, data: str):
        super().__init__()
        data_lst = data.split("_")  # 'button-word_{word_id}_{correct_id}_{type}_{correct}' или
                                    # button-already-learned_{word_id}_{type_id}

        if data_lst[0] == "button-word":
            self.word_id = int(data_lst[1])
            self.correct_id = int(data_lst[2])
            self.type_id = int(data_lst[3])  # тип угадывания - 1 - угадываем перевод по слову, 2 - по переводу слово
            self.correct = data_lst[4] == "1"
            self.user_id = user_id
        elif data_lst[0] == "button-already-learned":
            self.word_id = int(data_lst[1])
            self.correct_id = int(data_lst[1])
            self.type_id = int(data_lst[2])  # тип угадывания - 1 - угадываем перевод по слову, 2 - по переводу слово
            self.correct = True
            self.user_id = user_id

    def answer_message(self,
                       i18n: TranslatorRunner,
                       lang: str,
                       bot_database: Database,
                       default_settings: DefaultSettings):
        correct_word = bot_database.words_interface.get_word_by_id(self.correct_id, lang)
        bot_database.words_interface.save_statistic_by_word(self.user_id,
                                                            self.word_id,
                                                            default_settings,
                                                            (1 if self.correct else 0),
                                                            (0 if self.correct else 1))

        return (f'{i18n.correct.answer() if self.correct else i18n.wrong.answer()}\n\n'
                f'{correct_word["translation"] if self.type_id == "1" else correct_word["word"]} '
                f'- {correct_word["word"] if self.type_id == "1" else correct_word["translation"]}')

    def mark_word_as_never_learn(self, bot_database: Database, default_settings: DefaultSettings) -> None:
        bot_database.words_interface.mark_word_as_never_learn(self.user_id, self.word_id, default_settings)


def prepare_words_to_learn(user_id: int,
                           i18n: TranslatorRunner,
                           lang: str,
                           bot_database: Database,
                           default_settings: DefaultSettings,
                           answer_text: str = "") -> dict:
    words = bot_database.words_interface.get_words_to_learn(user_id, lang, default_settings)
    words_list = words["variants"]
    words_list.append(words["correct_word"])

    type_id = random.randint(1, 2)  # тип угадывания - 1 - угадываем перевод по слову, 2 - по переводу слово
    message_text = (f'{answer_text}\n\n'
                    f'{words["correct_word"][type_id]}\n\n'
                    f'{i18n.get(f'message-text-{type_id}')}')
    answer_id = words["correct_word"][0]
    random.shuffle(words_list)

    keyboard = Keyboards.guess_word_keyboard(i18n, words_list, type_id, answer_id)

    return {"message_text": message_text,
            "keyboard": keyboard}
