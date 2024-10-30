import logging
import redis
import ujson

from config_data.config import Config, load_config
from dotenv import find_dotenv

# класс наследуется от redis.StrictRedis
class Cache(redis.StrictRedis):
    def __init__(self, host, port, password,
                 charset="utf-8",
                 decode_responses=True):
        super(Cache, self).__init__(host, port,
                                    password=password,
                                    charset=charset,
                                    decode_responses=decode_responses)

    def jset(self, name, value, ex=0):
        """функция конвертирует python-объект в Json и сохранит"""
        r = self.get(name)
        if r is None:
            return r
        return ujson.loads(r)

    def jget(self, name):
        """функция возвращает Json и конвертирует в python-объект"""
        return ujson.loads(self.get(name))

    @staticmethod
    def cache_id(user_id, name):
        return f'user:{user_id}:{name}'

    def set_user_cache(self, user_id, name, value):
        self.setex(self.cache_id(user_id, name), 1800, value)

    def get_user_cache(self, user_id, name):
        return self.get(Cache.cache_id(user_id, name))


config: Config = load_config(find_dotenv('.env'))
cache = Cache(host=config.redis.redis_host,
              port=config.redis.redis_port,
              password=config.redis.redis_password)