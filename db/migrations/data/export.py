import json

from sqlalchemy import MetaData, Table, create_engine

from config_data.config import ConfigSettings

TABLE_NAME = "words"
EXPORT_FILE = "table_data.json"


def export_table():
    config = ConfigSettings()
    engine = create_engine(str(config.db.dsn))
    metadata = MetaData()
    metadata.reflect(engine, only=[TABLE_NAME])
    table = Table(TABLE_NAME, metadata, autoload_with=engine)

    with engine.connect() as conn:
        result = conn.execute(table.select()).mappings()
        data = [dict(row) for row in result]

    with open(EXPORT_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    print(f"Данные из {TABLE_NAME} экспортированы в {EXPORT_FILE}")


if __name__ == "__main__":
    export_table()
