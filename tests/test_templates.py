"""Поведение шаблонной версии при навигации, пустых данных и форматировании."""
from datetime import date
from unittest.mock import patch

import pytest
from django.contrib.staticfiles import finders
from django.urls import reverse
from django.template.loader import render_to_string

from src.requests import StudyRequest
from src.subjects import Subject
from src.users import User


@pytest.mark.parametrize("name,kwargs,url", [
    ("homepage:index", {}, "/"),
    ("subjects:list", {}, "/subjects/"),
    ("subjects:detail", {"subject_id": 1}, "/subjects/1/"),
    ("requests:list", {}, "/requests/"),
    ("requests:detail", {"request_id": 5}, "/requests/5/"),
])
def test_namespaces_generate_public_urls(name, kwargs, url):
    assert reverse(name, kwargs=kwargs) == url


@pytest.mark.parametrize("url,template", [
    ("/", "homepage/index.html"),
    ("/subjects/", "subjects/subject_list.html"),
    ("/subjects/1/", "subjects/subject_detail.html"),
    ("/requests/", "requests/request_list.html"),
    ("/requests/5/", "requests/request_detail.html"),
])
def test_pages_share_base_and_navigation(client, url, template):
    response = client.get(url)
    names = {item.name for item in response.templates}
    assert {template, "base.html", "includes/navigation.html", "includes/footer.html"} <= names
    html = response.content.decode()
    assert '/static/homepage/css/style.css' in html
    assert '/static/homepage/js/app.js' in html
    assert '<html lang="ru">' in html


def test_subject_shows_only_its_active_requests(client):
    response = client.get("/subjects/1/")
    items = response.context["active_requests"]
    assert {item.id for item in items} == {1, 3}
    assert all(item.subject.id == 1 and not item.is_closed for item in items)


def test_subject_with_no_active_requests_has_empty_state(client):
    with patch("subjects.views.get_requests_for_subject", return_value=[]):
        response = client.get("/subjects/1/")
    assert "Активных запросов пока нет" in response.content.decode()


def test_detail_passes_related_objects_and_closed_state(client):
    response = client.get("/requests/5/")
    item = response.context["study_request"]
    assert item.user.name == "Мария"
    assert item.subject.name == "Математика"
    assert item.is_closed
    html = response.content.decode()
    assert 'status-closed' in html
    assert "Завершён" in html
    assert "01 октября 2026" in html


def test_invalid_date_uses_template_fallback():
    item = StudyRequest(9, User(1, "Анна", ""), Subject(1, "Python"), "онлайн", "broken")
    html = render_to_string("requests/includes/request_card.html", {"item": item})
    assert "Дата не указана" in html
    assert "Группа не указана" in html


@pytest.mark.parametrize("value,expected", [
    ("22.10.2026", date(2026, 10, 22)), ("31.02.2026", None), ("", None),
])
def test_study_day_preserves_json_format(value, expected):
    item = StudyRequest(1, User(1, "А", "Б"), Subject(1, "Python"), "онлайн", value)
    assert item.study_day == expected
    assert item.date == value


@pytest.mark.parametrize("resource", [
    "homepage/css/style.css", "homepage/js/app.js", "homepage/images/study-mark.svg",
])
def test_static_resources_can_be_found(resource):
    assert finders.find(resource)
