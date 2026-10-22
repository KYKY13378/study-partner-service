"""Преобразование строк SQLite в объекты ПР3 и данные шаблонов ПР6."""
from datetime import date

from db.database import query
from src.requests import StudyRequest
from src.subjects import Subject
from src.users import User


def _request(row):
    item = StudyRequest(
        row["id"], User(row["user_id"], row["user_name"], row["group_name"] or ""),
        Subject(row["subject_id"], row["subject_name"]), row["format"],
        date.fromisoformat(row["study_date"]).strftime("%d.%m.%Y"),
    )
    item.is_closed = bool(row["is_closed"])
    return item


def get_subjects():
    return [Subject(row["id"], row["name"]) for row in query("list_subjects")]


def get_subject(subject_id):
    rows = query("subject_by_id", (subject_id,))
    return Subject(rows[0]["id"], rows[0]["name"]) if rows else None


def get_subject_cards():
    return [{"subject": Subject(row["id"], row["name"]), "active_count": row["active_count"]}
            for row in query("subjects_statistics")]


def get_requests(status="all"):
    names = {"all": "all_requests", "active": "active_requests", "closed": "closed_requests"}
    return [_request(row) for row in query(names[status])]


def get_request(request_id):
    rows = query("request_by_id", (request_id,))
    return _request(rows[0]) if rows else None


def get_requests_for_subject(subject_id):
    return [_request(row) for row in query("requests_for_subject", (subject_id,))]


def get_recent_requests():
    return [_request(row) for row in query("recent_requests", (3,))]


def search_requests(study_date=None, subject=None, format_type=None, user=None, status=None):
    return [_request(row) for row in query(
        "search_requests", (study_date, subject, format_type, user, status),
    )]
