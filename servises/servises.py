from lexicon.lexicon import LEXICON_RU
from database.database import bot_settings

# Определение выбранного времени
def get_selected_number(data:str, pref:str = "button_start_time_"):
    return int(data.replace(pref, ""))


