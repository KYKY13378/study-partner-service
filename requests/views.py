"""Запросы на совместную учебу и карточка одного запроса."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from src.requests import find_request_by_id
from src.storage import load_requests, load_subjects, load_users


def requests(request: HttpRequest) -> HttpResponse:
    """Передать коллекцию StudyRequest в шаблон списка."""
    items = load_requests(load_users(), load_subjects())
    return render(request, "requests/request_list.html", {"study_requests": items})


def request_detail(request: HttpRequest, request_id: int) -> HttpResponse:
    """Вернуть запрос со связанными объектами либо ответ 404."""
    items = load_requests(load_users(), load_subjects())
    target = find_request_by_id(items, request_id)
    if target is None:
        return render(request, "404.html", {"message": "Запрос не найден"}, status=404)
    return render(request, "requests/request_detail.html", {"study_request": target})
