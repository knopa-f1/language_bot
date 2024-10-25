from dataclasses import dataclass, asdict

@dataclass
class DefaultUserSettings:
    frequency: int = 24
    start_time: int = 12
    end_time: int = 12
    lang = "ru"


@dataclass
class DefaultAnswerSettings:
    count_correct: int = 2  # count how much times you should answer correct
    percent_correct: float = 0.8  # процент правильных ответов слова, чтобы считать его изученным
    count_current: int = 20  # одновременно изучающиеся слова
    repeat_after_days = 30  # слово может снова попасть в текущие после стольких дней


@dataclass
class DefaultSettings:
    user_set: DefaultUserSettings
    answer_set: DefaultAnswerSettings

    def __init__(self):
        self.user_set = DefaultUserSettings()
        self.answer_set = DefaultAnswerSettings()