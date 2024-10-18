from typing import Dict, Any

from config_data.constants import DefaultSettings
from database.cache import cache
from dotenv import find_dotenv
from fluentogram import TranslatorRunner
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


# class UsersCacheInterface():
#     def __init__(self):
#         self.users_cache = {}
#
#     def add(self, user_id, name, value):
#         if user_id not in self.users_cache:
#             self.users_cache[user_id] = {}
#         self.users_cache[user_id][name] = value
#
#     def create(self, user_id):
#         if user_id not in self.users_cache:
#             self.users_cache.setdefault(user_id, {})
#
#     def get(self, user_id, name):
#         return self.users_cache[user_id].get(name, None)
#
#
# class StorageInterface():
#     def __init__(self, redis_conn):
#         self.redis_conn: redis.Redis = redis_conn
#
#     @staticmethod
#     def cache_id(user_id, name):
#         return f'user:{user_id}:{name}'
#
#     async def set(self, key, value):
#         await self.redis_conn.set(key, value)
#
#     async def get(self, key):
#         return await self.redis_conn.get(key)
#
#     async def set_user_cache(self, user_id, name, value):
#         await self.redis_conn.setex(self.cache_id(user_id, name), value, default_settings.cache_time)
#
#     async def get_user_cache(self, user_id, name):
#         return await self.get(self, self.cache_id(user_id, name))


class UsersSettingsInterface(BaseQueriesMixin):

    def _exists(self, user_id: int) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM users_settings WHERE user_id = %s);"
        values = (user_id,)
        result = self.get_row_by_query(query, values)
        return result[0]

    def create(self, user_id: int, default_settings: DefaultSettings, lang: str = None) -> None:
        if not self._exists(user_id):
            query = '''
                    INSERT INTO users_settings (user_id, frequency, start_time, end_time, lang)
                    VALUES (%s, %s, %s, %s, %s);
                    '''
            values = (user_id, default_settings.frequency,
                      default_settings.start_time, default_settings.end_time,
                      lang)
            self.execute_query_and_commit(query, values)

    def get_description(self, user_id: int, i18n: TranslatorRunner):
        query = "SELECT  start_time, end_time, frequency, lang FROM users_settings WHERE user_id = %s;"
        values = (user_id,)
        user_settings = self.get_row_by_query_as_dict(query, values)
        if user_settings is None:
            return i18n.error.no.settings()
        else:
            return i18n.settings.desctiption(**user_settings)

    def get(self, user_id: int, name: str):
        query = f"SELECT {name} from users_settings WHERE user_id = %s;"
        values = (user_id,)
        user_settings = self.get_row_by_query_as_dict(query, values)
        return user_settings[name]

    def set(self, user_id: int, default_settings: DefaultSettings, **kwargs):
        self.create(user_id, default_settings)
        fields = ",".join([f'{field} = %s' for field in kwargs.keys()])
        query = f"UPDATE users_settings SET {fields} WHERE user_id = %s;"
        values = list(kwargs.values())
        values.append(user_id)
        self.execute_query_and_commit(query, tuple(values))

    # Возвращает список пользователей, для рассылки в текущий час
    def users_list_to_send(self, current_hour: int) -> list:
        # Нужно ли в этот час отправлять пользователю сообщение
        query = """select t.user_id as user_id, t.lang as lang  from users_settings as t
                where t.start_time <= %s and t.end_time >= %s
                and MOD((%s - t.start_time), t.frequency) = 0"""
        values = (current_hour, current_hour, current_hour)
        users_list = self.get_query_results_as_dict(query, values)
        return users_list


class WordsStatisticInterface(BaseQueriesMixin):
    def _current_words_exists(self, user_id: int) -> bool:
        query = "SELECT EXISTS(SELECT 1 FROM users_current_words WHERE user_id = %s);"
        values = (user_id,)
        result = self.get_row_by_query(query, values)
        return result[0]

    def add_current_user_words(self, user_id: int, default_settings: DefaultSettings = None, count: int = None):
        if count is None:
            count: int = default_settings.count_current

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

    def should_del_current_word(self, user_id: int, word_id: int, default_settings:DefaultSettings):
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

    def update_current_words(self,
                             user_id: int,
                             word_id: int,
                             default_settings:DefaultSettings,
                             del_word: bool = False):
        "Удаляет запись из текущих слов, если передан параметр или выучили слово"
        if del_word:
            status = Status.never_learn
        elif self.should_del_current_word(user_id, word_id, default_settings):
            status = Status.learned
        else:
            return

        query = """DELETE FROM users_current_words
                   WHERE user_id = %s and word_id = %s
                """
        values = (user_id, word_id)
        self.execute_query_and_commit(query, values)

        self.add_current_user_words(user_id, default_settings, count = 1)
        self.change_word_status(user_id, word_id, status.value)

    def get_words_to_learn(self, user_id: int, lang:str, default_settings: DefaultSettings, count: int = 4) -> dict[str, tuple | Any]:
        "возвращает слова для отображения - 1 из текущих слов пользователя, остальные - из общего списка"

        if not self._current_words_exists(user_id):
            # выбираем слова из словаря, которые еще не учили, пишем в текущие
            self.add_current_user_words(user_id, default_settings=default_settings)
        query = f"""SELECT d.word_id, d.word, d.translation_{lang} 
                FROM words_dictionary as d
                inner join users_current_words as cw
                on cw.user_id = %s and cw.word_id = d.word_id 
                ORDER BY RANDOM()
                LIMIT 1;"""
        correct_word = self.get_row_by_query(query, (user_id,))
        query = f"""SELECT d.word_id, d.word, d.translation_{lang} 
                        FROM words_dictionary as d
                        WHERE d.word_id != %s
                        ORDER BY RANDOM()
                        LIMIT %s;"""
        variants = self.get_query_results(query, (correct_word[0], count - 1))

        return dict(correct_word=correct_word, variants=variants)

    def get_word_by_id(self, word_id: int, lang:str) -> tuple:
        query = f"""SELECT word, translation_{lang} as translation
                        FROM words_dictionary
                        WHERE word_id = %s;"""
        return self.get_row_by_query_as_dict(query, (word_id,))

    def get_statistics(self, user_id: int, i18n: TranslatorRunner) -> str:
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
            return i18n.error.no_stat()
        else:
            return i18n.stat.description(**user_stat)

    def mark_word_as_never_learn(self, user_id: int, word_id: int, default_settings: DefaultSettings):
        self.update_current_words(user_id, word_id, default_settings, True)

    def save_statistic_by_word(self, user_id: int, word_id: int, default_settings:DefaultSettings, correct: int = 0, wrong: int = 0):
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
        self.update_current_words(user_id, word_id, default_settings)


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
        # self.redis_conn = redis.StrictRedis(
        #     host=config.redis.redis_host,
        #     port=config.redis.redis_port,
        #     password=config.redis.redis_password,
        #     charset="utf-8",
        #     decode_responses=True
        # )
        #
        # self.cache = StorageInterface(self.redis_conn)
        self.users_settings = UsersSettingsInterface(self.conn)
        self.words_interface = WordsStatisticInterface(self.conn)

    def get_table_data_as_list_dict(self, table_name: str) -> dict:
        with self.conn.cursor() as cursor:
            query = f"SELECT * FROM {table_name};"
            return self.get_query_results_as_dict(query)

bot_database = Database()