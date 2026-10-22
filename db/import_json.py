"""Перенос исходных JSON в SQLite; повторный импорт не затирает данные БД."""
import argparse
from contextlib import closing
from datetime import datetime
import json
from pathlib import Path

from db.database import DATABASE_FILE, ROOT, get_connection, initialize_database


def import_json(database_path=None, source_dir=None):
    """Импортировать три коллекции одной транзакцией, сохраняя прежние ID."""
    source = Path(source_dir) if source_dir is not None else ROOT / "data"

    def load(filename):
        return json.loads((source / filename).read_text(encoding="utf-8"))

    users = [(u["id"], u["name"], u["group"] or None) for u in load("users.json")]
    subjects = [(s["id"], s["name"]) for s in load("subjects.json")]
    requests = []
    for item in load("requests.json"):
        if type(item["is_closed"]) is not bool:
            raise ValueError("is_closed должен быть логическим значением JSON")
        requests.append((
            item["id"], item["user_id"], item["subject_id"], item["format"],
            datetime.strptime(item["date"], "%d.%m.%Y").date().isoformat(),
            int(item["is_closed"]),
        ))
    target = initialize_database(database_path)
    with closing(get_connection(target)) as connection:
        with connection:
            connection.executemany(
                "INSERT INTO users (id, name, group_name) VALUES (?, ?, ?) "
                "ON CONFLICT(id) DO NOTHING", users,
            )
            connection.executemany(
                "INSERT INTO subjects (id, name) VALUES (?, ?) "
                "ON CONFLICT(id) DO NOTHING", subjects,
            )
            connection.executemany(
                "INSERT INTO study_requests "
                "(id, user_id, subject_id, format, study_date, is_closed) "
                "VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO NOTHING", requests,
            )
        counts = {table: connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
                  for table in ("users", "subjects", "study_requests")}
    return target, counts


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--database", type=Path, default=DATABASE_FILE)
    parser.add_argument("--source", type=Path, default=ROOT / "data")
    arguments = parser.parse_args()
    path, counts = import_json(arguments.database, arguments.source)
    print(f"SQLite: {path}")
    print(counts)
