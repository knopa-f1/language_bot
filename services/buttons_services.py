import logging

from aiogram.types import InlineKeyboardMarkup

from services.statistics_service import StatisticsService
from services.word_management_service import WordManagementService

logger = logging.getLogger(__name__)


def get_selected_data(data: str) -> str:
    data_lst = data.split("_")
    return data_lst[-1]


def get_selected_end_time(data: str) -> tuple:
    data_lst = data.split("_")
    return data_lst[-2], data_lst[-1]

class ButtonWord:
    def __init__(self, chat_id, callback_data):
        self.chat_id = chat_id
        parts = callback_data.split('_')

        if parts[0] == "button-word":
            self.word_id = int(parts[1])
            self.correct_id = int(parts[2])
            # guess tipe - 1 - translation by lithuanian word, 2 - lithuanian word by translation
            self.type_id = int(parts[3])
            self.correct = parts[4] == "1"
        elif parts[0] == "button-already-learned":
            self.word_id = int(parts[1])
            self.correct_id = int(parts[1])
            # guess tipe - 1 - translation by lithuanian word, 2 - lithuanian word by translation
            self.type_id = int(parts[2])
            self.correct = True
        elif parts[0] == "button-letter":
            self.word_id = int(parts[1])
            self.correct_id = self.word_id
            self.type_id = 3
            self.correct = None
            self.index = int(parts[2])

    async def answer_message_for_word(self,
                                      service:WordManagementService,
                                      statistics_service:StatisticsService) -> str:
        return await service.process_word(self, statistics_service)

    async def answer_message_for_letter(self,
                                        service:WordManagementService,
                                        statistics_service:StatisticsService) -> tuple[str, InlineKeyboardMarkup|None]:
        return await service.process_letters(self, statistics_service)

    async def mark_word_as_never_learn(self,
                                       word_service: WordManagementService,
                                       learned_type: int = 0) -> None:
        if learned_type == 1:
            await word_service.mark_word_as_already_know(self.chat_id, self.word_id)
        else:
            await word_service.mark_word_as_never_learn(self.chat_id, self.word_id)

# class ButtonLetter:
#     def __init__(self, chat_id, callback_data):
#         self.chat_id = chat_id
#         _, word_id_str, index_str = callback_data.split('_')
#         self.word_id = int(word_id_str)
#         self.index = int(index_str)
#         self.type_id = 3
#
#     async def answer_message(self, service, statistics_service):
#         return await service.process_letters(self, statistics_service)

# class ButtonWord:
#
#     # def __init__(self, chat_id: int, data: str):
#     #     data_lst = data.split("_")  # 'button-word_{word_id}_{correct_id}_{type}_{correct}' or
#     #                                 #  'button-already-learned_{word_id}_{type_id}'
#     #
#     #     if data_lst[0] == "button-word":
#     #         self.word_id = int(data_lst[1])
#     #         self.correct_id = int(data_lst[2])
#     #         # guess tipe - 1 - translation by lithuanian word, 2 - lithuanian word by translation
#     #         self.type_id = int(data_lst[3])
#     #         self.correct = data_lst[4] == "1"
#     #         self.chat_id = chat_id
#     #     elif data_lst[0] == "button-already-learned":
#     #         self.word_id = int(data_lst[1])
#     #         self.correct_id = int(data_lst[1])
#     #         # guess tipe - 1 - translation by lithuanian word, 2 - lithuanian word by translation
#     #         self.type_id = int(data_lst[2])
#     #         self.correct = True
#     #         self.chat_id = chat_id
#     #     elif data_lst[0] == "button-letter":
#     #         self.type_id = 3
#     #         self.chat_id = chat_id
#     #         self.word_id = int(data_lst[1])
#     #         self.index = int(data_lst[2])
#
#     async def answer_message(self,
#                              word_service: WordManagementService,
#                              statistics_service: StatisticsService) -> str:
#         correct_word = await word_service.get_word_by_id(self.correct_id)
#         await statistics_service.save_statistic(self.chat_id,
#                                                 self.word_id,
#                                                 (1 if self.correct else 0),
#                                                 (0 if self.correct else 1)
#                                                 )
#
#         return (f'{word_service.i18n.correct.answer() if self.correct else word_service.i18n.wrong.answer()}\n\n'
#                 f'{getattr(correct_word, f'translation_{word_service.lang}') if self.type_id == "1" else correct_word.word} '
#                 f'- {correct_word.word if self.type_id == "1" else getattr(correct_word, f'translation_{word_service.lang}')}\n\n'
#                 f'<code>{correct_word.example}\n'
#                 f'{getattr(correct_word, f'example_{word_service.lang}')}</code>')
#
#     async def mark_word_as_never_learn(self,
#                                        word_service: WordManagementService,
#                                        learned_type: int = 0) -> None:
#         if learned_type == 1:
#             await word_service.mark_word_as_already_know(self.chat_id, self.word_id)
#         else:
#             await word_service.mark_word_as_never_learn(self.chat_id, self.word_id)
