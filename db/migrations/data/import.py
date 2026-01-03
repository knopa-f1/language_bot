import asyncio
import json

from sqlalchemy import MetaData, insert
from sqlalchemy.ext.asyncio import create_async_engine

from config_data.config import ConfigSettings

TABLE_NAME = "words"
EXPORT_FILE = "table_data.json"


async def import_table_async():
    config = ConfigSettings()
    engine = create_async_engine(str(config.db.dsn))

    metadata = MetaData()
    async with engine.begin() as conn:
        await conn.run_sync(metadata.reflect, only=[TABLE_NAME])

    table = metadata.tables[TABLE_NAME]

    with open(EXPORT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    async with engine.begin() as conn:
        await conn.execute(insert(table), data)

    print(f"Данные из {EXPORT_FILE} импортированы в {TABLE_NAME}")


if __name__ == "__main__":
    asyncio.run(import_table_async())
