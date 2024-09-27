from database.database import load_users_words, load_users_settings, save_users_settings, save_users_settings
from lexicon.lexicon import LEXICON_RU

# Функция получения настроек
def get_user_settings(user_id:str):
    user_settings = load_users_settings().get(user_id, None)
    if user_settings == None:
        return LEXICON_RU["error_no_settings"]
    else:
        return (f"⚙️ ТВОИ НАСТРОЙКИ:\n"
        f"Время начала: {user_settings['start_time']}:00\n"
        f"Время окончания: {user_settings['end_time']}:00\n"
        f"Периодичность: каждый {user_settings['frequency']} час\n"
        f"Чтобы изменить настройки, нажми кнопки ниже")

# Сохранение в файл настроек пользователя
def save_user_settings(user_id: str, **kwargs):
    users_settings = load_users_settings()
    for name, value in kwargs.items():
        users_settings[user_id][name] = value
    save_users_settings(users_settings)

# Определение выбранного времени
def get_selected_number(data:str, pref:str = "button_start_time_"):
    return int(data.replace(pref, ""))

# Проверка периода времени
def verify_time(start_time, end_time):
    return True if start_time < end_time else False
