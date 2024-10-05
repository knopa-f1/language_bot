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
    'cancel_settings': "✖️ Настройки оставлены без изменений",
    'message_text_1': "🧐 Вспомни, как переводится слово:",
    'message_text_2': "🧐 Вспомни, что значит слово:",
    'correct_answer': "🤩 Молодец! Это верный ответ!",
    'wrong_answer': "😔 Ошибка! Правильный ответ: ",
    'cancel_learning': "😎 Отлично поучились! \n\nЕсли захочешь вернуться к словам, просто нажми кнопку 'Поехали!'",
    'schedule_message': '😉 Привет! Время учить новые слова!',
    "user_settings": '''ТВОИ НАСТРОЙКИ :
*Время начала:*{user_settings["start_time"]}
*Время окончания:*{user_settings["end_time"]}
*Периодичность:* каждый {user_settings["frequency"]} час
Чтобы изменить настройки, нажми кнопки ниже.
'''

}

LEXICON_BUTTONS_RU: dict[str, str] = {
    'buttonStart':'Поехали!',
    'buttonSettings':'Мои настройки',
    'buttonChangeTime': 'Время работы напоминаний',
    'buttonChangeFrequency': 'Периодичность',
    'buttonCancelSettings': 'Отмена',
    'buttonCancelLearning': "Завершить"
}

LEXICON_COMMANDS_RU: dict[str, str] = {
    '/start': 'Запуск бота',
    '/help': 'Помощь по боту',
    '/settings': 'Настройки',
}

