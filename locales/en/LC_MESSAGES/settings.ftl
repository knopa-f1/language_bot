settings-desctiption = ⚙️ SETTINGS:

                       Reminder schedule:
                       from { $start_time }:00 to { $end_time }:00 every { $frequency } hour

                       Number of current learning words: { $count_current }

                       Language: { $lang }

stat-description =  📊 STATISTICS:

                    Total answers: { $all }
                    Correct answers: { $correct }
                    Correct percentage: { NUMBER($correct_percent, maximumFractionDigits: 2) }%
                    Words learned:  { $learned }
