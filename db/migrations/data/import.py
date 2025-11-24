import json

from sqlalchemy import MetaData, Table, create_engine

from config_data.config import ConfigSettings

TABLE_NAME = "words"
EXPORT_FILE = "table_data.json"


def import_table():
    config = ConfigSettings()
    engine = create_engine(str(config.db.dsn))
    metadata = MetaData()
    metadata.reflect(engine, only=[TABLE_NAME])
    table = Table(TABLE_NAME, metadata, autoload_with=engine)

    with open(EXPORT_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    with engine.begin() as conn:
        conn.execute(table.insert(), data)

    print(f"Данные из {EXPORT_FILE} импортированы в {TABLE_NAME}")


if __name__ == "__main__":
    import_table()
