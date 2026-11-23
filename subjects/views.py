"""Предметы и активные запросы из Django ORM."""
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from requests.queries import get_requests_for_subject, get_subject_cards
from subjects.models import Subject


def subjects(request: HttpRequest) -> HttpResponse:
    text = request.GET.get("q", "").strip()
    error = "Поисковая строка должна содержать не более 100 символов." if len(text) > 100 else ""
    cards = [] if error else get_subject_cards(text)
    return render(request, "subjects/subject_list.html", {
        "subject_cards": cards, "q": text, "error": error,
    }, status=400 if error else 200)


def subject_detail(request: HttpRequest, subject_id=None, slug=None) -> HttpResponse:
    try:
        subject = get_object_or_404(Subject, **({"slug": slug} if slug else {"pk": subject_id}))
    except Http404:
        # Сохраняем оформленный ответ ПР6 и при DEBUG=True.
        return render(request, "404.html", {"message": "Предмет не найден"}, status=404)
    return render(request, "subjects/subject_detail.html", {
        "subject": subject, "active_requests": get_requests_for_subject(subject),
    })
