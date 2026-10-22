"""Регрессии хранения данных и идентификаторов с пропусками."""
import json

import pytest

from src import storage
from src.requests import StudyRequest, add_request
from src.subjects import Subject, add_subject
from src.users import User, add_user


def test_round_trip_restores_links_and_closed_state(tmp_path, monkeypatch):
    for attr, filename in [("USERS_FILE", "u.json"), ("SUBJECTS_FILE", "s.json"),
                           ("REQUESTS_FILE", "r.json")]:
        monkeypatch.setattr(storage, attr, tmp_path / filename)
    user, subject = User(3, "Анна", "Тест"), Subject(7, "Python")
    request = StudyRequest(5, user, subject, "онлайн", "22.10.2026")
    request.close()
    storage.save_users([user])
    storage.save_subjects([subject])
    storage.save_requests([request])
    users, subjects = storage.load_users(), storage.load_subjects()
    loaded = storage.load_requests(users, subjects)[0]
    assert loaded.user is users[0]
    assert loaded.subject is subjects[0]
    assert loaded.is_closed
    assert json.loads(storage.REQUESTS_FILE.read_text(encoding="utf-8"))[0]["user_id"] == 3


def test_ids_after_gaps_remain_unique():
    user, subject = User(3, "Анна", "Тест"), Subject(7, "Python")
    assert add_user([user], "Борис", "Тест").id == 4
    assert add_subject([subject], "Django").id == 8
    request = StudyRequest(10, user, subject, "онлайн", "22.10.2026")
    assert add_request([request], user, subject, "онлайн", "23.10.2026").id == 11


@pytest.mark.parametrize("content", ["{broken", "{}", "[1, 2]"])
def test_invalid_json_returns_empty_list(tmp_path, content):
    filename = tmp_path / "broken.json"
    filename.write_text(content, encoding="utf-8")
    assert storage._read_json(filename) == []


def test_data_paths_do_not_depend_on_working_directory(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert storage.load_subjects()
