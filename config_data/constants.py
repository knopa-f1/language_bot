from dataclasses import dataclass, asdict


@dataclass
class DefaultChatSettings:
    frequency: int = 24
    start_time: int = 18
    end_time: int = 18
    lang = "ru"
    count_current: int = 10  # now learning words


@dataclass
class DefaultAnswerSettings:
    count_correct: int = 10  # count how much times you should answer correct
    percent_correct: float = 0.8  # percent correct words
    repeat_after_days = 30  # repeat word after these days after learning
    vars_count_current = [5, 7, 10, 12, 15, 20]


@dataclass
class DefaultSettings:
    chat_set: DefaultChatSettings
    answer_set: DefaultAnswerSettings

    def __init__(self):
        self.chat_set = DefaultChatSettings()
        self.answer_set = DefaultAnswerSettings()
