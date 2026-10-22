"""Запросы на совместную учебу и карточка одного запроса."""
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render

from datetime import date

from db.database import query
from db.repository import get_request, get_requests, get_subjects, search_requests


def requests(request: HttpRequest) -> HttpResponse:
    """Передать коллекцию StudyRequest в шаблон списка."""
    status = request.GET.get("status", "all")
    if status not in {"all", "active", "closed"}:
        return render(request, "requests/request_list.html", {
            "study_requests": [], "error": "Неизвестный статус запроса.",
        }, status=400)
    return render(request, "requests/request_list.html", {
        "study_requests": get_requests(status), "status": status,
    })


def request_detail(request: HttpRequest, request_id: int) -> HttpResponse:
    """Вернуть запрос со связанными объектами либо ответ 404."""
    target = get_request(request_id)
    if target is None:
        return render(request, "404.html", {"message": "Запрос не найден"}, status=404)
    return render(request, "requests/request_detail.html", {"study_request": target})


def _optional_id(value, label):
    if not value:
        return None
    if not value.isascii() or not value.isdecimal() or len(value) > 10 or int(value) < 1:
        raise ValueError(f"{label}: выберите корректный идентификатор.")
    return int(value)


def search(request: HttpRequest) -> HttpResponse:
    """Проверить GET и передать значения связанными параметрами в SQL."""
    filters = {key: request.GET.get(key, "")
               for key in ("date", "subject", "format", "user")}
    filters["status"] = request.GET.get("status", "active")
    items, participants, error = [], [], ""
    try:
        day = filters["date"] or None
        if day and date.fromisoformat(day).isoformat() != day:
            raise ValueError("Дата должна иметь формат ГГГГ-ММ-ДД.")
        subject = _optional_id(filters["subject"], "Предмет")
        user = _optional_id(filters["user"], "Автор")
        if filters["format"] not in {"", "онлайн", "офлайн"}:
            raise ValueError("Выберите формат онлайн или офлайн.")
        statuses = {"all": None, "active": 0, "closed": 1}
        if filters["status"] not in statuses:
            raise ValueError("Выберите корректный статус запроса.")
        items = search_requests(day, subject, filters["format"] or None,
                                user, statuses[filters["status"]])
        if day:
            participants = query("users_without_requests_for_date", (day,))
    except ValueError as exception:
        error = str(exception) if not filters["date"] else (
            "Проверьте дату (ГГГГ-ММ-ДД), предмет, автора, формат и статус."
        )
    return render(request, "requests/search.html", {
        "filters": filters, "study_requests": items, "participants": participants,
        "subjects": get_subjects(), "users": query("list_users"),
        "formats": query("distinct_formats"), "error": error,
    }, status=400 if error else 200)


def statistics(request: HttpRequest) -> HttpResponse:
    """Сводные показатели, GROUP BY и настраиваемый HAVING из SQLite."""
    raw = request.GET.get("min_count", "2")
    error = ""
    if not raw.isascii() or not raw.isdecimal() or len(raw) > 6 or int(raw) < 1:
        error = "Минимум запросов: введите целое число от 1 до 999999."
        threshold = 2
    else:
        threshold = int(raw)
    return render(request, "requests/statistics.html", {
        "totals": query("request_totals")[0], "catalog": query("catalog_totals")[0],
        "subject_stats": query("subjects_statistics"), "user_stats": query("users_statistics"),
        "format_stats": query("format_statistics"), "period": query("date_range")[0],
        "popular": query("popular_subjects", (threshold,)),
        "min_count": threshold, "error": error,
    }, status=400 if error else 200)
