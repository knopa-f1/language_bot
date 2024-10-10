LEXICON_RU: dict[str, str] = {
    '/start': 'Привет!\nЯ бот, который поможет тебе учить литовские слова. Я буду присылать тебе новые слова, чтобы ты учил их. Начнем?',
    '/help': 'Бот поможет тебе выучить литовские слова. \n.\n '
             'Настроить расписание напоминаний можно по кнопке "Настройки" или вызвав команду "Мои настройки"',
    'no_answer': 'Я тебя не понял :(',
    'change_start_time': "🕧 Выбери время начала напоминаний (час)",
    'change_end_time': "🕝 Выбери время окончания напоминаний (час)",
    'change_frequency': "⏳ Выбери раз в сколько часов будет приходить напоминание",
    'saved_settings': "✔️ Ура! Настройки сохранены. \nДавай начнем учиться прямо сейчас?",
    'error_no_settings': "⚠️Упс... Настройки не найдены. Давай внесем новые?",
    'error_no_stat': "⚠️ Похоже, ты еще не учил слова. Чтобы начать учиться прямо сейчас, просто нажми кнопку",
    'cancel_settings': "✖️ Настройки оставлены без изменений",
    'message_text_1': "переводится как:",
    'message_text_2': "значит:",
    'correct_answer': "🤩 Молодец! Это верный ответ!",
    'wrong_answer': "😔 Ошибка!",
    'cancel_learning': "😎 Отлично поучились! \n\nЕсли захочешь вернуться к словам, просто нажми кнопку 'Поехали!'",
    'already_learned': '👌 Договорились! Больше не буду показывать тебе это слово',
    'schedule_message': '😉 Привет! Время учить новые слова!',
    "user_settings": '⚙️ НАСТРОЙКИ:',
    "user_stat": '📊 ТВОЯ СТАТИСТИКА:'
    }

LEXICON_SETTINGS_RU: dict[str, str] = {
    'start_time': "Время начала: %s:00",
    'end_time': "Время окончания: %s:00",
    'frequency':  "Периодичность: каждый %s час"
    # 'language':  "Язык: "
    }

LEXICON_STATISTICS_RU: dict[str, str] = {
    'all': "Всего ответов: %s",
    'correct': "Из них правильных: %s",
    'correct_percent':  "Процент правильных: %s",
    'learned':  "Выучено слов: %s"
    }

LEXICON_BUTTONS_RU: dict[str, str] = {
    'buttonStart': 'Поехали!',
    'buttonContinue': "Далее",
    'buttonSettings': 'Настройки',
    'buttonStatistics': 'Статистика',
    'buttonChangeTime': 'Время работы напоминаний',
    'buttonChangeFrequency': 'Периодичность',
    'buttonCancelSettings': 'Отмена',
    'buttonCancelLearning': "Завершить",
    'buttonAlreadyLearned_0': "Не хочу учить это слово",
    'buttonAlreadyLearned_1': "Уже выучил это слово"
}

LEXICON_COMMANDS_RU: dict[str, str] = {
    '/start': 'Запуск бота',
    '/help': 'Помощь по боту',
    '/settings': 'Настройки',
    '/statistics': 'Статистика'
}

