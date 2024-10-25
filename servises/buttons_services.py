from dataclasses import dataclass

from servises.users_service import UsersService
import logging

logger = logging.getLogger(__name__)


def get_selected_data(data: str) -> str:
    data_lst = data.split("_")
    return data_lst[-1]


def get_selected_end_time(data: str) -> tuple:
    data_lst = data.split("_")
    return data_lst[-2], data_lst[-1]


@dataclass
class ButtonWord:
    user_id: int
    word_id: int
    type_id: int  # guess tipe - 1 - translation by lithuanian word, 2 - lithuanian word by translation
    correct_id: int
    correct: bool = False

    def __init__(self, user_id: int, data: str):
        super().__init__()
        data_lst = data.split("_")  # 'button-word_{word_id}_{correct_id}_{type}_{correct}' или
        # button-already-learned_{word_id}_{type_id}

        if data_lst[0] == "button-word":
            self.word_id = int(data_lst[1])
            self.correct_id = int(data_lst[2])
            self.type_id = int(data_lst[3])
            self.correct = data_lst[4] == "1"
            self.user_id = user_id
        elif data_lst[0] == "button-already-learned":
            self.word_id = int(data_lst[1])
            self.correct_id = int(data_lst[1])
            self.type_id = int(data_lst[2])
            self.correct = True
            self.user_id = user_id

    async def answer_message(self,
                             user_service: UsersService) -> str:
        correct_word = await user_service.get_word_by_id(self.correct_id)
        await user_service.save_statistic(self.user_id,
                                          self.word_id,
                                          (1 if self.correct else 0),
                                          (0 if self.correct else 1)
                                          )

        return (f'{user_service.i18n.correct.answer() if self.correct else user_service.i18n.wrong.answer()}\n\n'
                f'{getattr(correct_word, f'translation_{user_service.lang}') if self.type_id == "1" else correct_word.word} '
                f'- {correct_word.word if self.type_id == "1" else getattr(correct_word, f'translation_{user_service.lang}')}\n\n'
                f'● {correct_word.example}')

    async def mark_word_as_never_learn(self,
                                       user_service: UsersService) -> None:
        await user_service.mark_word_as_never_learn(self.user_id, self.word_id)
