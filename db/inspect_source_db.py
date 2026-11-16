"""Инспекция исходной SQLite ПР7 без записи и создания пустой БД."""
import argparse
from contextlib import closing
import json
from pathlib import Path
import sqlite3

SOURCE_DB = Path(__file__).resolve().parent.parent / "data/study_partner.sqlite"
SOURCE_TABLES = ("users", "subjects", "study_requests")


def read_source(path=SOURCE_DB):
    target = Path(path).resolve()
    with closing(sqlite3.connect(target.as_uri() + "?mode=ro", uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        if connection.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
            raise ValueError("Повреждена исходная база ПР7.")
        if connection.execute("PRAGMA foreign_key_check").fetchall():
            raise ValueError("В исходной базе нарушены внешние ключи.")
        # Имена таблиц фиксированы в программе, пользователь в SQL не подставляется.
        return {table: [dict(row) for row in connection.execute(f"SELECT * FROM {table}")]
                for table in SOURCE_TABLES}


def inspect_source(path=SOURCE_DB):
    target = Path(path).resolve()
    data = read_source(target)
    with closing(sqlite3.connect(target.as_uri() + "?mode=ro", uri=True)) as connection:
        connection.row_factory = sqlite3.Row
        return {table: {
            "count": len(data[table]),
            "columns": [dict(row) for row in connection.execute(f"PRAGMA table_info({table})")],
            "foreign_keys": [dict(row) for row in connection.execute(
                f"PRAGMA foreign_key_list({table})")],
        } for table in SOURCE_TABLES}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE_DB)
    print(json.dumps(inspect_source(parser.parse_args().source), ensure_ascii=False, indent=2))
