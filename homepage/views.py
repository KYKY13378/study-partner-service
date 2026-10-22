"""Главная страница и общий обработчик 404."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.database import query
from db.repository import get_recent_requests, get_subjects


def index(request: HttpRequest) -> HttpResponse:
    """Передать на главную реальные предметы, запросы и сводные показатели."""
    totals = query("request_totals")[0]
    catalog = query("catalog_totals")[0]
    return render(request, "homepage/index.html", {
        "subjects": get_subjects(),
        "recent_requests": get_recent_requests(),
        "active_count": totals["active"], "user_count": catalog["users"],
    })


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    """Ответить общей страницей 404 для неизвестного маршрута."""
    return render(request, "404.html", status=404)
