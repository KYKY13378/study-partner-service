# src/storage.py
import json
import os

from src.requests import StudyRequest
from src.subjects import Subject, find_subject_by_id
from src.users import User, find_user_by_id

USERS_FILE = "data/users.json"
SUBJECTS_FILE = "data/subjects.json"
REQUESTS_FILE = "data/requests.json"


def _read_json(filename: str) -> list:
    """Прочитать список данных из JSON-файла.

    Args:
        filename: Путь к файлу.

    Returns:
        Список данных; пустой список, если файла нет или он поврежден.
    """
    if not os.path.exists(filename):
        return []
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, ValueError):
        print(f"Ошибка: файл {filename} поврежден.")
        return []


def _write_json(filename: str, data: list) -> None:
    """Записать список данных в JSON-файл.

    Args:
        filename: Путь к файлу.
        data: Данные для сохранения.
    """
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except IOError as e:
        print(f"Ошибка записи в файл {filename}: {e}")


def load_users() -> list[User]:
    """Загрузить пользователей из JSON и создать объекты User.

    Returns:
        Список объектов User.
    """
    return [User.from_data(data) for data in _read_json(USERS_FILE)]


def load_subjects() -> list[Subject]:
    """Загрузить предметы из JSON и создать объекты Subject.

    Returns:
        Список объектов Subject.
    """
    return [Subject.from_data(data) for data in _read_json(SUBJECTS_FILE)]


def load_requests(
        users: list[User],
        subjects: list[Subject],
) -> list[StudyRequest]:
    """Загрузить запросы из JSON и восстановить связи с объектами.

    Args:
        users: Коллекция пользователей.
        subjects: Коллекция предметов.

    Returns:
        Список объектов StudyRequest со ссылками на User и Subject.
    """
    requests = []
    for data in _read_json(REQUESTS_FILE):
        user = find_user_by_id(users, data["user_id"])
        subject = find_subject_by_id(subjects, data["subject_id"])
        if user is None or subject is None:
            print(f"Ошибка: запрос {data['id']} пропущен "
                  "(не найден пользователь или предмет).")
            continue
        request = StudyRequest(
            request_id=data["id"],
            user=user,
            subject=subject,
            format_type=data["format"],
            study_date=data["date"],
        )
        request.is_closed = data["is_closed"]
        requests.append(request)
    return requests


def save_users(users: list[User]) -> None:
    """Сохранить объекты User в JSON-файл.

    Args:
        users: Список пользователей.
    """
    data = [{"id": u.id, "name": u.name, "group": u.group} for u in users]
    _write_json(USERS_FILE, data)


def save_subjects(subjects: list[Subject]) -> None:
    """Сохранить объекты Subject в JSON-файл.

    Args:
        subjects: Список предметов.
    """
    data = [{"id": s.id, "name": s.name} for s in subjects]
    _write_json(SUBJECTS_FILE, data)


def save_requests(requests: list[StudyRequest]) -> None:
    """Сохранить объекты StudyRequest в JSON-файл.

    Args:
        requests: Список запросов.
    """
    data = [
        {
            "id": r.id,
            "user_id": r.user.id,
            "subject_id": r.subject.id,
            "format": r.format,
            "date": r.date,
            "is_closed": r.is_closed,
        }
        for r in requests
    ]
    _write_json(REQUESTS_FILE, data)
