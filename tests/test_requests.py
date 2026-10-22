# tests/test_requests.py
from src.requests import (
    StudyRequest,
    add_request,
    close_request,
    filter_requests_by_format,
    find_request_by_id,
    find_requests_by_subject,
    get_partner_status,
)
from src.subjects import Subject
from src.users import User


def test_request_creation():
    user = User(1, "Иван", "ЭФБО-18-24")
    subject = Subject(1, "Математика")
    request = StudyRequest(1, user, subject, "онлайн", "15.09.2026")
    assert request.id == 1
    assert request.user is user
    assert request.subject is subject
    assert request.is_closed is False


def test_request_str():
    user = User(1, "Иван", "ЭФБО-18-24")
    subject = Subject(1, "Математика")
    request = StudyRequest(1, user, subject, "онлайн", "15.09.2026")
    assert "Иван" in str(request)
    assert "Математика" in str(request)
    assert "активен" in str(request)


def test_request_close():
    user = User(1, "Иван", "ЭФБО-18-24")
    subject = Subject(1, "Математика")
    request = StudyRequest(1, user, subject, "онлайн", "15.09.2026")
    request.close()
    assert request.is_closed is True
    assert "закрыт" in str(request)


def test_request_matches():
    user = User(1, "Иван", "ЭФБО-18-24")
    subject = Subject(1, "Математика")
    request = StudyRequest(1, user, subject, "онлайн", "15.09.2026")
    assert request.matches(subject_name="математика")
    assert request.matches(format_type="онлайн")
    assert not request.matches(subject_name="Физика")


def test_add_request():
    requests = []
    user = User(1, "Иван", "ЭФБО-18-24")
    subject = Subject(1, "Математика")
    request = add_request(requests, user, subject, "онлайн", "15.09.2026")
    assert len(requests) == 1
    assert requests[0] is request


def test_find_requests_by_subject():
    requests = []
    user = User(1, "Иван", "ЭФБО-18-24")
    math = Subject(1, "Математика")
    physics = Subject(2, "Физика")
    add_request(requests, user, math, "онлайн", "15.09.2026")
    add_request(requests, user, physics, "офлайн", "16.09.2026")
    found = find_requests_by_subject(requests, "математика")
    assert len(found) == 1
    assert found[0].subject.name == "Математика"


def test_filter_requests_by_format():
    requests = []
    user = User(1, "Иван", "ЭФБО-18-24")
    subject = Subject(1, "Математика")
    add_request(requests, user, subject, "онлайн", "15.09.2026")
    add_request(requests, user, subject, "офлайн", "16.09.2026")
    filtered = filter_requests_by_format(requests, "онлайн")
    assert len(filtered) == 1


def test_close_request():
    requests = []
    user = User(1, "Иван", "ЭФБО-18-24")
    subject = Subject(1, "Математика")
    add_request(requests, user, subject, "онлайн", "15.09.2026")
    assert close_request(requests, 1)
    assert requests[0].is_closed
    assert not close_request(requests, 99)


def test_get_partner_status():
    assert "найден" in get_partner_status(True).lower()
    assert "не найден" in get_partner_status(False).lower()


def test_find_request_by_id():
    requests = []
    user = User(1, "Иван", "ЭФБО-18-24")
    subject = Subject(1, "Математика")
    add_request(requests, user, subject, "онлайн", "15.09.2026")
    found = find_request_by_id(requests, 1)
    assert found is not None
    assert found.user is user
    assert find_request_by_id(requests, 99) is None
