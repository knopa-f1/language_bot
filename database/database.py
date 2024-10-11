from config_data.constants import default_settings
from dotenv import find_dotenv
from lexicon.lexicon import LEXICON_RU, LEXICON_SETTINGS_RU, LEXICON_STATISTICS_RU
from dataclasses import dataclass
import psycopg2
from psycopg2.extensions import connection
import psycopg2.extras
from config_data.config import Config, load_config
from enum import Enum
from jinja2 import Template

class Status(Enum):
    "Статус изучения слова"
    new = "new"
    in_progress = "in_progress"
    never_learn = "never_learn"
    learned = "learned"

@dataclass
class BaseQueriesMixin:
    conn: connection

    def get_row_by_query(self, query: str, values: tuple = None) -> tuple:
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()
        if result:
            return result
        return (None,)

    def get_row_by_query_as_dict(self, query: str, values: tuple = None) -> (dict, None):
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()
            result_dict = dict(result)
        if result_dict:
            return result_dict
        return None

    def get_query_results(self, query: str, values: tuple = None) -> (list[tuple], None):
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchall()
        if result:
            return result
        return None

    def get_query_results_as_dict(self, query: str, values: tuple = None) -> list[dict]:
        with self.conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query, values)
            result = cursor.fetchall()
            result_dict = []
            for row in result:
                result_dict.append(dict(row))
        if result_dict:
            return result_dict
        return []

    def execute_query_and_commit(self, query, values: tuple = None):
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            self.conn.commit()

    def execute_queries_and_commit(self, query, values=None):
        with self.conn.cursor() as cursor:
            cursor.executemany(query, values)
            self.conn.commit()


class UsersCacheInterface():
    def __init__(self):
        self.users_cache = {}

    def add(self, user_id, name, value):
        if user_id not in self.users_cache:
            self.users_cache[user_id] = {}
        self.users_cache[user_id][name] = value

    def create(self, user_id):
        if user_id not in self.users_cache:
            self.users_cache.setdefault(user_id, {})

    def get(self, user_id, name):
        return self.users_cache[user_id].get(name, None)


class UsersSettingsInterface(BaseQueriesMixin):

    def _exists(self, user_id: int) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM users_settings WHERE user_id = %s);"
        values = (user_id,)
        result = self.get_row_by_query(query, values)
        return result[0]

    def create(self, user_id: int) -> None:
        if not self._exists(user_id):
            query = '''
                    INSERT INTO users_settings (user_id, frequency, start_time, end_time)
                    VALUES (%s, %s, %s, %s);
                    '''
            values = (user_id, default_settings.frequency, default_settings.start_time, default_settings.end_time)
            self.execute_query_and_commit(query, values)

    def get(self, user_id: int):
        query = "SELECT  start_time, end_time, frequency FROM users_settings WHERE user_id = %s;"
        values = (user_id,)
        user_settings = self.get_row_by_query_as_dict(query, values)
        if user_settings == None:
            return LEXICON_RU["error_no_settings"]
        else:
            settings = LEXICON_RU["user_settings"] + "\n".join(LEXICON_SETTINGS_RU.values())
            return Template(settings).render(user_settings = user_settings)


    def save(self, user_id: int, **kwargs):
        fields = ",".join([f'{field} = %s' for field in kwargs.keys()])
        query = f"UPDATE users_settings SET {fields} WHERE user_id = %s;"
        values = list(kwargs.values())
        values.append(user_id)
        self.execute_query_and_commit(query, tuple(values))

    # Возвращает список пользователей, для рассылки в текущий час
    def users_list_to_send(self, current_hour: int) -> list:
        # Нужно ли в этот час отправлять пользователю сообщение
        query = """select t.user_id from users_settings as t 
                where t.start_time <= %s and t.end_time >= %s
                and MOD((%s - t.start_time), t.frequency) = 0"""
        values = (current_hour, current_hour, current_hour)
        users_list = self.get_query_results(query, values)
        return users_list


class WordsStatisticInterface(BaseQueriesMixin):
    def _current_words_exists(self, user_id: int) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM users_current_words WHERE user_id = %s);"
        values = (user_id,)
        result = self.get_row_by_query(query, values)
        return result[0]

    def add_current_user_words(self, user_id: int, count: int = default_settings.count_current):
        query = """INSERT INTO users_current_words(user_id, word_id)
    	            (SELECT %s, d.word_id
                         FROM words_dictionary as d
                          LEFT JOIN users_statistics as s
                                on s.user_id = %s and s.word_id = d.word_id 
                          WHERE COALESCE(s.status, %s) = %s 
                                or (COALESCE(s.status, %s) = %s and s.status_date + INTERVAL '%s day' <= now())
                    ORDER BY RANDOM()
                    LIMIT %s);
                    """
        values = (user_id, user_id, Status.new.value, Status.new.value, Status.new.value,
                  Status.learned.value, default_settings.repeat_after_days, count)
        self.execute_query_and_commit(query, values)

    def should_del_current_word(self, user_id: int, word_id: int):
        query = """SELECT user_id, word_id FROM users_statistics 
	                WHERE user_id = %s and word_id = %s 
	                and correct >= %s and 
	                CASE WHEN correct+wrong = 0 THEN 0 ELSE correct/(correct+wrong) END >=%s
	            """

        values = (user_id, word_id,
                  default_settings.count_correct,
                  default_settings.percent_correct)

        result = self.get_row_by_query(query, values)
        return result[0] is not None

    def change_word_status(self, user_id: int, word_id: int, status):
        query = """INSERT INTO users_statistics(user_id, word_id, correct, wrong, status, status_date)
                    VALUES (%s, %s, 0, 0, %s, now())
                    ON CONFLICT (user_id, word_id)
                    DO UPDATE SET
                        status = %s,
                        status_date = now()"""
        values = (user_id, word_id, status, status)
        self.execute_query_and_commit(query, values)

    def update_current_words(self, user_id: int, word_id: int, del_word: bool = False):
        "Удаляет запись из текущих слов, если передан параметр или выучили слово"
        if del_word:
            status = Status.never_learn
        elif self.should_del_current_word(user_id, word_id):
            status = Status.learned
        else:
            return

        query = """DELETE FROM users_current_words
                   WHERE user_id = %s and word_id = %s
                """
        values = (user_id, word_id)
        self.execute_query_and_commit(query, values)

        self.add_current_user_words(user_id, 1)
        self.change_word_status(user_id, word_id, status.value)

    def get_words_to_learn(self, user_id: int, count: int = 4):
        "возвращает слова для отображения - 1 из текущих слов пользователя, остальные - из общего списка"

        if not self._current_words_exists(user_id):
            # выбираем слова из словаря, которые еще не учили, пишем в текущие
            self.add_current_user_words(user_id)
        query = """SELECT d.word_id, d.word, d.translation_ru 
                FROM words_dictionary as d
                inner join users_current_words as cw
                on cw.user_id = %s and cw.word_id = d.word_id 
                ORDER BY RANDOM()
                LIMIT 1;"""
        correct_word = self.get_row_by_query(query, (user_id, ))
        query = """SELECT d.word_id, d.word, d.translation_ru 
                        FROM words_dictionary as d
                        WHERE d.word_id != %s
                        ORDER BY RANDOM()
                        LIMIT %s;"""
        variants = self.get_query_results(query, (correct_word[0], count-1))

        return {"correct_word": correct_word,
                "variants": variants}

    def get_word_by_id(self, word_id: int) -> tuple:
        query = """SELECT word, translation_ru as translation
                        FROM words_dictionary
                        WHERE word_id = %s;"""
        return self.get_row_by_query_as_dict(query, (word_id,))

    def get_statistics(self, user_id: int):
        query = """SELECT SUM(correct + wrong) as all,
                    SUM(correct) as correct, 
                    CASE WHEN SUM(correct+ wrong) = 0 
                        THEN 0
                        ELSE (SUM(correct)*100/SUM(correct+ wrong))
                    END as correct_percent,
                    SUM(CASE WHEN COALESCE(status,  %s) =  %s THEN 1 ELSE 0 END) as learned 
                    FROM users_statistics 
                    WHERE user_id = %s;"""
        values = (Status.new.value, Status.learned.value, user_id)
        user_stat = self.get_row_by_query_as_dict(query, values)

        if user_stat == None:
            return LEXICON_RU["error_no_stat"]
        else:
            stat = LEXICON_RU["user_stat"] + "\n".join(LEXICON_STATISTICS_RU.values())
            print(type(stat))
            return Template(stat).render(user_stat=user_stat)

    def mark_word_as_never_learn(self, user_id: int, word_id: int):
        self.update_current_words(user_id, word_id, True)

    def save_statistic_by_word(self, user_id: int, word_id: int, correct: int = 0, wrong: int = 0):
        query = """INSERT INTO users_statistics(user_id, word_id, correct, wrong, status, status_date)
                    VALUES (%s, %s, %s, %s, %s, now())
                    ON CONFLICT (user_id, word_id)
                    DO UPDATE SET
                        correct = users_statistics.correct + %s,
                        wrong = users_statistics.wrong + %s,
                        status = %s
                """
        values = (user_id, word_id, correct, wrong, Status.in_progress.value, correct, wrong, Status.in_progress.value)
        self.execute_query_and_commit(query, values)
        self.update_current_words(user_id, word_id)


class Database(BaseQueriesMixin):
    def __init__(self):
        config: Config = load_config(find_dotenv('.env'))
        self.conn = psycopg2.connect(
            dbname=config.db.database,
            user=config.db.db_user,
            password=config.db.db_password,
            host=config.db.db_host,
            port=config.db.dp_port
        )

        self.users_cache = UsersCacheInterface()
        self.users_settings = UsersSettingsInterface(self.conn)
        self.words_interface = WordsStatisticInterface(self.conn)

    def get_table_data_as_dict(self, table_name: str) -> dict:
        with self.conn.cursor() as cursor:
            query = f"SELECT * FROM {table_name};"
            cursor.execute(query)
            results: list[tuple] = cursor.fetchall()
            return dict(results)


bot_database = Database()
