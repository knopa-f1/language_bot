from lexicon.lexicon import LEXICON_RU


# Определение выбранного времени
def get_selected_number(data:str, pref:str = "button_start_time_"):
    return int(data.replace(pref, ""))

# Проверка периода времени
def verify_time(start_time, end_time):
    return True if start_time < end_time else False
