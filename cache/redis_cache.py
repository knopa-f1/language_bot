import json

import redis.asyncio as redis  # type: ignore[import-untyped]


class RedisCache:
    def __init__(self, host: str, port: int, password: str | None = None, db: int = 0, ttl: int = 3600):
        self.ttl = ttl
        self.redis = redis.Redis(
            host=host,
            port=port,
            password=password,
            db=db,
            decode_responses=True,
        )

    async def set_chat_settings(self, chat_id: int, **kwargs):
        key = f"chat:{chat_id}:settings"
        mapping = {k: json.dumps(v) for k, v in kwargs.items()}
        await self.redis.hset(key, mapping=mapping)
        await self.redis.expire(key, self.ttl)

    async def get_chat_settings(self, chat_id: int, name: str):
        key = f"chat:{chat_id}:settings"
        raw = await self.redis.hget(key, name)
        if raw is None:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            return raw

    async def set_user(self, user_id: int, chat_id: int):
        key = f"user:{user_id}:chat"
        await self.redis.set(key, chat_id, ex=self.ttl)

    async def user_exists(self, user_id: int):
        key = f"user:{user_id}:chat"
        return await self.redis.exists(key) == 1
