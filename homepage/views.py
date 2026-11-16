"""Главная страница и общий обработчик 404."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from requests.queries import catalog_totals, get_recent_requests, get_subjects, request_totals


def index(request: HttpRequest) -> HttpResponse:
    totals, catalog = request_totals(), catalog_totals()
    return render(request, "homepage/index.html", {
        "subjects": get_subjects(), "recent_requests": get_recent_requests(),
        "active_count": totals["active"], "user_count": catalog["users"],
    })


def page_not_found(request: HttpRequest, exception: Exception) -> HttpResponse:
    return render(request, "404.html", status=404)
