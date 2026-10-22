"""Проверка страниц, источника данных и двух различных путей ответа 404."""
from unittest.mock import patch

import pytest
from django.test import override_settings
from django.urls import Resolver404, resolve

from src.subjects import Subject


@pytest.mark.parametrize("url,text", [
    ("/", "Сервис поиска партнеров"),
    ("/subjects/", "Математика"),
    ("/subjects/1/", "Алексей"),
    ("/requests/", "Запросы"),
    ("/requests/5/", "Мария"),
])
def test_pages_show_json_data(client, url, text):
    response = client.get(url)
    assert response.status_code == 200
    assert text in response.content.decode()


@pytest.mark.parametrize("url", ["/subjects/999/", "/requests/999/"])
def test_missing_object_does_not_call_global_handler(client, url):
    with patch("homepage.views.page_not_found") as handler:
        response = client.get(url)
    assert response.status_code == 404
    handler.assert_not_called()


@override_settings(DEBUG=False)
def test_missing_route_uses_custom_404(client):
    response = client.get("/does-not-exist/")
    assert response.status_code == 404
    assert "страница не найдена" in response.content.decode()


def test_converter_rejects_text_before_view():
    with pytest.raises(Resolver404):
        resolve("/subjects/abc/")
    assert resolve("/subjects/999/").kwargs == {"subject_id": 999}


@pytest.mark.parametrize("url,module,loader,text", [
    ("/subjects/", "subjects.views", "load_subjects", "Предметов пока нет"),
    ("/requests/", "requests.views", "load_requests", "Запросов пока нет"),
])
def test_empty_collections_have_message(client, url, module, loader, text):
    with patch(f"{module}.{loader}", return_value=[]):
        response = client.get(url)
    assert response.status_code == 200
    assert text in response.content.decode()


def test_json_text_is_escaped(client):
    subject = Subject(99, "<script>alert('test')</script>")
    with patch("subjects.views.load_subjects", return_value=[subject]):
        html = client.get("/subjects/").content.decode()
    assert "<script>alert" not in html
    assert "&lt;script&gt;" in html
