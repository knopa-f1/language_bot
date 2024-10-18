from dataclasses import dataclass

@dataclass
class DefaultSettings:
    # general
    cache_time = 1800

    # user settings
    frequency: int = 24
    start_time: int = 12
    end_time: int = 12
    lang = "ru"

    # answers and stat
    count_correct: int = 10 # сколько раз надо отгадать слово, чтобы считать его изученным
    percent_correct: float = 0.8 # процент правильных ответов слова, чтобы считать его изученным
    count_current: int = 20 # одновременно изучающиеся слова
    repeat_after_days = 30 # слово может снова попасть в текущие после стольких дней

default_settings = DefaultSettings()