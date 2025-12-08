import asyncio
import json

from sqlalchemy import MetaData, select
from sqlalchemy.ext.asyncio import create_async_engine

from config_data.config import ConfigSettings

TABLE_NAME = "words"
EXPORT_FILE = "table_data.json"


async def export_table_async():
    config = ConfigSettings()

    engine = create_async_engine(str(config.db.dsn))

    metadata = MetaData()
    async with engine.begin() as conn:
        await conn.run_sync(metadata.reflect, only=[TABLE_NAME])

    table = metadata.tables[TABLE_NAME]

    async with engine.connect() as conn:
        result = await conn.execute(select(table))
        rows = result.mappings().all()
        data = [dict(r) for r in rows]

    with open(EXPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Данные из {TABLE_NAME} экспортированы в {EXPORT_FILE}")


if __name__ == "__main__":
    asyncio.run(export_table_async())
