"""Предметы и связанные с ними активные запросы."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from src.storage import load_requests, load_subjects, load_users
from src.subjects import find_subject_by_id


def subjects(request: HttpRequest) -> HttpResponse:
    """Показать предметы и число активных запросов по каждому из них."""
    subjects_list = load_subjects()
    requests_list = load_requests(load_users(), subjects_list)
    cards = [
        {"subject": subject, "active_count": sum(
            item.subject.id == subject.id and not item.is_closed for item in requests_list
        )}
        for subject in subjects_list
    ]
    return render(request, "subjects/subject_list.html", {"subject_cards": cards})


def subject_detail(request: HttpRequest, subject_id: int) -> HttpResponse:
    """Найти предмет по ID и передать в шаблон его активные запросы."""
    subjects_list = load_subjects()
    subject = find_subject_by_id(subjects_list, subject_id)
    if subject is None:
        return render(request, "404.html", {"message": "Предмет не найден"}, status=404)
    requests_list = load_requests(load_users(), subjects_list)
    active_requests = [item for item in requests_list
                       if item.subject.id == subject.id and not item.is_closed]
    return render(request, "subjects/subject_detail.html", {
        "subject": subject, "active_requests": active_requests,
    })
