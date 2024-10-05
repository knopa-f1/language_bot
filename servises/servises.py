from lexicon.lexicon import LEXICON_RU
from database.database import bot_database
import random
from keyboards.inline_keyboards import guess_word_keyboard

# Определение выбранного времени
def get_selected_number(data: str, pref: str = "buttonStartTime_"):
    return int(data.replace(pref, ""))

def check_if_answer_correct(data: str):
    return True if data.endswith("1") else False

def answer_message(data: str):
    data_lst  = data.split("_") # 'buttonWord_{word_id}_{answer_id}_{type}_{correct}'
    is_correct = True if data_lst[4] == "1" else False
    if is_correct:
        return LEXICON_RU['correct_answer']
    else:
        correct_id = int(data_lst[2])
        type = data_lst[3] # тип угадывания - 1 - угадываем перевод по слову, 2 - по переводу слово
        correct_word = bot_database.words_interface.get_word_by_id(correct_id)
        return (f'{LEXICON_RU['wrong_answer']}'
                f'{correct_word[1] if type == "1" else correct_word[0]}')

def prepare_words_to_learn(answer_text: str = 0) -> dict:
    words_list = bot_database.words_interface.get_random_words()
    type = random.randint(1,2) # тип угадывания - 1 - угадываем перевод по слову, 2 - по переводу слово
    message_text = (f'{answer_text}\n\n'
                    f'{LEXICON_RU[f'message_text_{type}']}\n'
                    f'{words_list[0][type]}')
    answer_id = words_list[0][0]
    random.shuffle(words_list)

    keyboard = guess_word_keyboard(words_list, type, answer_id)

    return {"message_text": message_text,
            "keyboard": keyboard}
