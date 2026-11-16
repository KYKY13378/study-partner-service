"""ПР7: целостность БД, транзакции импорта и реальные SQL в веб-сценариях."""
from contextlib import closing
import json
from pathlib import Path
import sqlite3

import pytest

from db import database
from db.database import get_connection, initialize_database, query
from db.import_json import import_json


def test_connection_uses_expected_database_and_named_columns(isolated_sqlite):
    with closing(get_connection()) as connection:
        assert connection.execute("PRAGMA foreign_keys").fetchone()[0] == 1
        row = connection.execute("PRAGMA database_list").fetchone()
        assert Path(row["file"]) == isolated_sqlite
        assert connection.execute("SELECT name FROM users WHERE id = ?", (1,)).fetchone()[
            "name"] == "Алексей"


def test_missing_database_does_not_create_silent_empty_file(tmp_path):
    path = tmp_path / "missing.sqlite"
    with pytest.raises(sqlite3.OperationalError):
        get_connection(path)
    assert not path.exists()


def test_schema_and_import_can_repeat_without_overwriting(isolated_sqlite):
    with closing(get_connection()) as connection, connection:
        connection.execute("UPDATE users SET name = 'Новое имя' WHERE id = 1")
    initialize_database()
    _, counts = import_json()
    assert counts == {"users": 4, "subjects": 3, "study_requests": 5}
    assert query("list_users")[0]["name"] == "Новое имя"
    row = query("request_by_id", (5,))[0]
    assert row["study_date"] == "2026-10-01" and row["is_closed"] == 1


@pytest.mark.parametrize("statement,parameters", [
    ("INSERT INTO study_requests VALUES (99,99,1,'онлайн','2026-10-22',0)", ()),
    ("INSERT INTO study_requests VALUES (99,1,99,'онлайн','2026-10-22',0)", ()),
    ("DELETE FROM subjects WHERE id=1", ()),
    ("INSERT INTO users VALUES (1,'Повтор','Группа')", ()),
    ("INSERT INTO users VALUES (99,NULL,NULL)", ()),
    ("INSERT INTO subjects VALUES (99,' ')", ()),
    ("INSERT INTO study_requests VALUES (99,1,1,?,'2026-10-22',0)", ("гибрид",)),
    ("INSERT INTO study_requests VALUES (99,1,1,'онлайн',?,0)", ("2026-02-31",)),
    ("INSERT INTO study_requests VALUES (99,1,1,'онлайн',?,0)", ("22.10.2026",)),
    ("INSERT INTO study_requests VALUES (99,1,1,'онлайн','2026-10-22',2)", ()),
])
def test_constraints_reject_invalid_data(statement, parameters):
    with closing(get_connection()) as connection:
        with pytest.raises(sqlite3.IntegrityError):
            connection.execute(statement, parameters)


def test_import_rolls_back_all_rows_when_foreign_key_is_missing(tmp_path):
    source = tmp_path / "source"
    source.mkdir()
    data = {
        "users.json": [{"id": 99, "name": "Тест", "group": ""}],
        "subjects.json": [{"id": 99, "name": "Тестовый предмет"}],
        "requests.json": [{"id": 99, "user_id": 100, "subject_id": 99,
                           "format": "онлайн", "date": "22.10.2026", "is_closed": False}],
    }
    for filename, value in data.items():
        (source / filename).write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(sqlite3.IntegrityError):
        import_json(source_dir=source)
    assert len(query("list_users")) == 4
    assert len(query("list_subjects")) == 3


def test_grouping_having_and_participants_without_active_requests():
    assert dict(query("request_totals")[0]) == {"total": 5, "active": 4, "closed": 1}
    assert [r["active_count"] for r in query("subjects_statistics")] == [2, 1, 1]
    assert [r["id"] for r in query("popular_subjects", (2,))] == [1]
    assert query("popular_subjects", (3,)) == []
    assert {r["id"] for r in query("users_without_requests_for_date", ("2026-09-18",))} == {
        1, 2, 4,
    }
    assert len(query("users_without_requests_for_date", ("2026-10-01",))) == 4


def test_empty_database_and_subject_without_requests(client):
    from requests.models import StudyRequest
    from users.models import User

    StudyRequest.objects.all().delete()
    User.objects.create(name="Без группы")
    with closing(get_connection()) as connection, connection:
        connection.execute("DELETE FROM study_requests")
        connection.execute("INSERT INTO users VALUES (99, 'Без группы', NULL)")
    assert dict(query("request_totals")[0]) == {"total": 0, "active": 0, "closed": 0}
    assert all(r["active_count"] == 0 for r in query("subjects_statistics"))
    response = client.get("/requests/statistics/")
    assert response.status_code == 200
    assert "Запросов пока нет" in response.content.decode()
    assert "Без группы" in response.content.decode()


def test_database_only_record_appears_on_site(client):
    from subjects.models import Subject

    with closing(get_connection()) as connection, connection:
        connection.execute("INSERT INTO subjects VALUES (99, 'Только в SQLite')")
    assert "Только в SQLite" not in client.get("/subjects/").content.decode()
    Subject.objects.create(name="Только в ORM")
    assert "Только в ORM" in client.get("/subjects/").content.decode()


@pytest.mark.parametrize("status,ids", [
    ("all", {1, 2, 3, 4, 5}), ("active", {1, 2, 3, 4}), ("closed", {5}),
])
def test_status_filter_is_done_on_server(client, status, ids):
    response = client.get("/requests/", {"status": status, "per_page": 20})
    assert {r.id for r in response.context["study_requests"]} == ids


def test_combined_search_and_preserved_inputs(client):
    response = client.get("/requests/search/", {
        "date": "2026-09-18", "subject": "1", "format": "онлайн", "user": "3",
        "status": "active",
    })
    assert response.status_code == 200
    assert [r.id for r in response.context["study_requests"]] == [3]
    assert {r.id for r in response.context["participants"]} == {1, 2, 4}
    html = response.content.decode()
    assert 'value="2026-09-18"' in html and "Дмитрий" in html
    assert 'value="онлайн" selected' in html


def test_empty_search_and_closed_search(client):
    response = client.get("/requests/search/", {"date": "2026-09-19"})
    assert response.status_code == 200 and not response.context["study_requests"]
    assert "Ничего не найдено" in response.content.decode()
    response = client.get("/requests/search/", {"status": "closed"})
    assert [r.id for r in response.context["study_requests"]] == [5]


@pytest.mark.parametrize("parameters", [
    {"date": "2026-02-31"}, {"date": "20260918"}, {"subject": "1 OR 1=1"},
    {"user": "-1"}, {"format": "онлайн' OR 1=1 --"}, {"status": "invalid"},
    {"subject": "9" * 100}, {"user": "²"},
])
def test_invalid_search_inputs_return_validation_error(client, parameters):
    response = client.get("/requests/search/", parameters)
    assert response.status_code == 400 and response.context["error"]
    assert len(query("all_requests")) == 5


def test_bound_parameter_does_not_change_sql_structure():
    assert query("subject_by_id", ("1 OR 1=1",)) == []


@pytest.mark.parametrize("raw", ["0", "-2", "text", "9999999", "²"])
def test_invalid_having_threshold(client, raw):
    response = client.get("/requests/statistics/", {"min_count": raw})
    assert response.status_code == 400


def test_threshold_changes_groups_on_page(client):
    response = client.get("/requests/statistics/", {"min_count": 1})
    assert len(response.context["popular"]) == 3
    response = client.get("/requests/statistics/", {"min_count": 3})
    assert len(response.context["popular"]) == 0
    assert "Уменьшите минимум" in response.content.decode()


def test_web_pages_no_longer_use_legacy_sql_queries(client, monkeypatch):
    def forbidden():
        raise AssertionError("Веб-страница вызвала старый SQL-слой")

    monkeypatch.setattr(database, "read_queries", forbidden)
    for url in ("/", "/subjects/", "/subjects/1/", "/requests/", "/requests/5/",
                "/requests/?status=active", "/requests/?status=closed",
                "/requests/search/?date=2026-09-18", "/requests/statistics/"):
        assert client.get(url).status_code == 200


def test_legacy_sql_error_is_not_hidden_as_empty_result(monkeypatch):
    original = database.read_queries

    def broken():
        statements = original()
        statements["search_requests"] = "SELECT unknown_column FROM study_requests"
        return statements

    monkeypatch.setattr(database, "read_queries", broken)
    with pytest.raises(sqlite3.OperationalError):
        query("search_requests")
