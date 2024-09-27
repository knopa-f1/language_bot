from config_data.constants import default_settings, file_name_settings, file_name_user_words
from utils.utils import load_dict, save_dict

# Создаем шаблон заполнения словаря с пользователями
users_settings_dict_template = default_settings

user_word_template = {
    'viewed': False,
    'learned': False
}

users_cache = {}

# Функция загружает словарь пользовательских настроек из файла
def load_users_settings():
    return load_dict(file_name_settings)

# Функция загружает словарь пользовательских настроек слов из файла
def load_users_words():
    load_dict(file_name_user_words)

#Функция сохраняет словарь пользовательских настроек слов в файл
def save_users_words(users_words: dict):
    save_dict(users_words, file_name_user_words)

#Функция сохраняет словарь пользовательских настроек в файл
def save_users_settings(users_settings: dict):
    save_dict(users_settings, file_name_settings)


