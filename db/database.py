"""Соединения, схема и выполнение именованных запросов из sql/queries.sql."""
from contextlib import closing
from pathlib import Path
import re
import sqlite3

ROOT = Path(__file__).resolve().parent.parent
DATABASE_FILE = ROOT / "data/study_partner.sqlite"
SQL_DIR = ROOT / "sql"


def get_connection(path=None, *, create=False):
    """Открыть именно существующую БД; создание разрешено только явно."""
    target = Path(path if path is not None else DATABASE_FILE).resolve()
    mode = "rwc" if create else "rw"
    connection = sqlite3.connect(f"{target.as_uri()}?mode={mode}", uri=True, timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database(path=None):
    """Создать таблицы и индексы, не удаляя существующие строки."""
    target = Path(path if path is not None else DATABASE_FILE).resolve()
    target.parent.mkdir(parents=True, exist_ok=True)
    with closing(get_connection(target, create=True)) as connection:
        connection.executescript((SQL_DIR / "schema.sql").read_text(encoding="utf-8"))
        connection.commit()
    return target


def read_queries():
    """Читать SQL из файла: правки на защите видны при следующем запросе."""
    source = (SQL_DIR / "queries.sql").read_text(encoding="utf-8")
    parts = re.split(r"^-- name: (\w+)\s*$", source, flags=re.MULTILINE)
    return {parts[i]: parts[i + 1].strip() for i in range(1, len(parts), 2)}


def query(name, parameters=()):
    """Выполнить фиксированный SQL, передав пользовательские значения отдельно."""
    statement = read_queries()[name]
    # SQLite ?1, ?2 ... — нумерованные имена, в DB-API передаем словарь.
    bindings = {str(index): value for index, value in enumerate(parameters, start=1)}
    with closing(get_connection()) as connection:
        return connection.execute(statement, bindings).fetchall()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Создание схемы SQLite")
    parser.add_argument("--path", type=Path, default=DATABASE_FILE)
    print(initialize_database(parser.parse_args().path))
