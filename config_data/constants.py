from dataclasses import dataclass


@dataclass
class DefaultSettings:
    frequency: int = 24
    start_time: int = 12
    end_time: int = 12

    count_correct: int = 5
    percent_correct: float = 0.8
    count_current: int = 5
    repeat_after_days = 30

default_settings = DefaultSettings()