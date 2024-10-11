LEXICON_RU: dict[str, str] = {
    '/start': 'Привет!\nЯ бот, который поможет тебе учить литовские слова. Я буду присылать тебе новые слова, чтобы ты учил их. Начнем?',
    '/help': 'Этот бот поможет тебе выучить литовские слова легко и интересно. \n\n'
             'Чтобы начать, просто нажми на кнопку "Поехали" или используй команду /start.'
             ' Бот предложит тебе слово на литовском или русском языке с несколькими вариантами перевода.'
             ' Твоя задача — выбрать правильный.\n\n'
             'Если хочешь настроить расписание напоминаний, перейди в раздел "Настройки" или введи команду /settings. '
             'А статистику твоих успехов можно посмотреть с помощью команды /statistics.',
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
    "user_settings": '⚙️ НАСТРОЙКИ: \n',
    "user_stat": '📊 ТВОЯ СТАТИСТИКА:\n'
    }

LEXICON_SETTINGS_RU: dict[str, str] = {
    'start_time': "Время начала: {{user_settings.start_time}}:00",
    'end_time': "Время окончания: {{user_settings.end_time}}:00",
    'frequency':  "Периодичность: каждый {{user_settings.frequency}} час"
    # 'language':  "Язык: "
    }

LEXICON_STATISTICS_RU: dict[str, str] = {
    'all': "Всего ответов: {{user_stat.all}}",
    'correct': "Из них правильных: {{user_stat.correct}}",
    'correct_percent':  "Процент правильных: {{user_stat.all}}",
    'learned':  "Выучено слов: {{user_stat.learned}}"
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

