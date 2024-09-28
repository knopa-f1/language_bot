from config_data.constants import default_settings, file_name_settings, file_name_user_words
from utils.utils import load_dict, save_dict
from dataclasses import dataclass, field

user_word_template = {
    'viewed': False,
    'learned': False
}
class BotSettings:
    __instance = None
    # Создаем шаблон заполнения словаря с пользователями
    users_settings_dict_template = default_settings

    def __new__(cls):
        if not cls.__instance:
            cls.__instance = super(BotSettings, cls).__new__(cls)
            cls.__instance.initialize_settings()
        return cls.__instance

    def initialize_settings(self):
        # Логика инициализации настроек
        self.users_settings = load_dict(file_name_settings)
        self.users_cache = {}

    def add_user_users_settings(self, user_id):
        if user_id not in self.users_settings:
            self.users_settings.setdefault(user_id, deepcopy(BotSettings.users_settings_dict_template))
            self.users_cache.setdefault(user_id, deepcopy(BotSettings.users_settings_dict_template))
            save_users_settings(users_settings)

    def add_user_cache(self, user_id, name, value):
        if user_id not in self.users_cache:
            self.users_cache[user_id] = {}
        self.users_cache[user_id][name] = value

    def get_user_cache(self,user_id, name):
        return self.users_cache[user_id].get(name, None)

    def get_user_settings(self, user_id: str):
        user_settings = self.users_settings.get(user_id, None)
        if user_settings == None:
            return LEXICON_RU["error_no_settings"]
        else:
            return (f"⚙️ ТВОИ НАСТРОЙКИ:\n"
                    f"Время начала: {user_settings['start_time']}:00\n"
                    f"Время окончания: {user_settings['end_time']}:00\n"
                    f"Периодичность: каждый {user_settings['frequency']} час\n"
                    f"Чтобы изменить настройки, нажми кнопки ниже")

    def save_user_settings(self, user_id: str, **kwargs):
        for name, value in kwargs.items():
            self.users_settings[user_id][name] = value
        self.save_users_settings_to_file()

    #Функция сохраняет словарь пользовательских настроек в файл
    def save_users_settings_to_file(self):
        save_dict(self.users_settings, file_name_settings)


# Инициализируем настройки
bot_settings = BotSettings()