settings-desctiption = ⚙️ НАСТРОЙКИ:

                      Напоминания будут приходить:
                      с { $start_time }:00 по { $end_time }:00 каждый { $frequency } час

                      Количество текущих изучаемых слов: { $count_current } шт.

                      Язык: { $lang }


stat-description =  📊 ТВОЯ СТАТИСТИКА:

                    Всего ответов:  { $all }
                    Из них правильных: { $correct }
                    Процент правильных: { NUMBER($correct_percent, maximumFractionDigits: 2) }%
                    Выучено слов: { $learned }
