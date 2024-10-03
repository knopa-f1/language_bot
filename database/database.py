from copy import deepcopy

from config_data.constants import default_settings
from dotenv import find_dotenv
from lexicon.lexicon import LEXICON_RU
from utils.utils import load_dict, save_dict
from dataclasses import dataclass, field
import psycopg2
from psycopg2.extensions import connection
import random
from config_data.config import Config, load_config

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

    def get_query_results(self, query: str, values: tuple = None) -> list[tuple]:
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchall()
        if result:
            return result
        return []

    def execute_query_and_commit(self, query, values=None):
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
            self.users_cache.setdefault(user_id, deepcopy(default_settings))

    def get(self,user_id, name):
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
            values = (user_id, *default_settings.values())
            self.execute_query_and_commit(query, values)

    def get(self, user_id: int):
        query = "SELECT  start_time, end_time, frequency FROM users_settings WHERE user_id = %s;"
        values = (user_id,)
        user_settings = self.get_row_by_query(query, values)

        if user_settings == None:
            return LEXICON_RU["error_no_settings"]
        else:
            return (f"⚙️ ТВОИ НАСТРОЙКИ:\n"
                    f"Время начала: {user_settings[0]}:00\n"
                    f"Время окончания: {user_settings[1]}:00\n"
                    f"Периодичность: каждый {user_settings[2]} час\n"
                    f"Чтобы изменить настройки, нажми кнопки ниже")

    def save(self, user_id: int, **kwargs):
        fields = ",".join([f'{field} = %s' for field in kwargs.keys()])
        query = f"UPDATE users_settings SET {fields} WHERE user_id = %s;"
        values = list(kwargs.values())
        values.append(user_id)
        self.execute_query_and_commit(query, values)

    # Возвращает список пользователей, для рассылки в текущий час
    def users_list_to_send(self, current_hour: int):
        # Нужно ли в этот час отправлять пользователю сообщение
        query = """select t.user_id from users_settings as t 
                where t.start_time <= %s and t.end_time >= %s
                and MOD((%s - t.start_time), t.frequency) = 0"""
        values = (current_hour, current_hour, current_hour)
        users_list = self.get_query_results(query, values)
        return users_list

class WordsInterface(BaseQueriesMixin):

    def get_random_word(self):
        query = """SELECT lithuanian, russian 
                FROM words_dictionary
                ORDER BY RANDOM()
                LIMIT 1;"""
        result = self.get_row_by_query(query)
        return f'{result[0]} = {result[1]}'

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
        self.words_interface = WordsInterface(self.conn)

    def get_row_by_query(self, query: str, values: tuple = None) -> tuple:
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            result = cursor.fetchone()
        if result:
            return result
        return (None,)

    def execute_query_and_commit(self, query, values=None):
        with self.conn.cursor() as cursor:
            cursor.execute(query, values)
            self.conn.commit()
    def get_table_data_as_dict(self, table_name: str) -> dict:
        with self.conn.cursor() as cursor:
            query = f"SELECT * FROM {table_name};"
            cursor.execute(query)
            results: list[tuple] = cursor.fetchall()
            return dict(results)


bot_database = Database()