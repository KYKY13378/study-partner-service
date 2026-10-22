"""Главная страница и общий обработчик 404."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from src.storage import load_requests, load_subjects, load_users


def index(request: HttpRequest) -> HttpResponse:
    """Передать на главную реальные предметы, запросы и сводные показатели."""
    users = load_users()
    subjects = load_subjects()
    requests = load_requests(users, subjects)
    return render(request, "homepage/index.html", {
        "subjects": subjects,
        "recent_requests": list(reversed(requests))[:3],
        "active_count": sum(not item.is_closed for item in requests),
        "user_count": len(users),
    })


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Ответить общей страницей 404 для неизвестного маршрута."""
    return render(request, "404.html", status=404)
