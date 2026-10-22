"""Предметы и связанные с ними активные запросы."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from db.repository import get_subject, get_subject_cards, get_requests_for_subject


def subjects(request: HttpRequest) -> HttpResponse:
    """Показать предметы и число активных запросов по каждому из них."""
    return render(request, "subjects/subject_list.html", {"subject_cards": get_subject_cards()})


def subject_detail(request: HttpRequest, subject_id: int) -> HttpResponse:
    """Найти предмет по ID и передать в шаблон его активные запросы."""
    subject = get_subject(subject_id)
    if subject is None:
        return render(request, "404.html", {"message": "Предмет не найден"}, status=404)
    active_requests = get_requests_for_subject(subject_id)
    return render(request, "subjects/subject_detail.html", {
        "subject": subject, "active_requests": active_requests,
    })
