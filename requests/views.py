"""Фильтрация, сортировка, пагинация и статистика средствами Django ORM."""
from django.core.paginator import Paginator
from django.http import Http404, HttpRequest, HttpResponse
from django.shortcuts import get_object_or_404, render

from requests.forms import RequestFiltersForm
from requests.models import StudyRequest
from requests.queries import (
    catalog_totals, date_range, distinct_formats, filter_requests, format_statistics,
    get_requests, get_subjects, get_users, popular_subjects, request_rows, request_totals,
    sort_requests, subject_statistics, user_statistics, users_without_requests_for_date,
)

PAGE_SIZE = 2
SORT_OPTIONS = [("date", "Дата: сначала ранние"), ("date_desc", "Дата: сначала поздние"),
                ("subject", "По предмету и дате"), ("author", "По автору и дате")]


def _catalog(request, *, is_search):
    parameters = request.GET.copy()
    parameters.setdefault("status", "active" if is_search else "all")
    parameters.setdefault("view", "cards")
    form = RequestFiltersForm(parameters)
    error, participants = "", []
    if form.is_valid():
        filters = form.cleaned_data
        items = filter_requests(get_requests(filters["status"]), filters)
        items = sort_requests(items, filters["sort"])
        if filters["view"] == "table":
            items = request_rows(items)
        if filters.get("date"):
            participants = users_without_requests_for_date(filters["date"])
        page_size = filters.get("per_page") or PAGE_SIZE
    else:
        error = " ".join(f"{form.fields[name].label}: {'; '.join(messages)}"
                         for name, messages in form.errors.items())
        items, page_size = [], PAGE_SIZE
    # Q26: get_page обрабатывает нечисловой и выходящий за границы номер.
    page_obj = Paginator(items, page_size).get_page(request.GET.get("page"))
    display_filters = parameters.dict()
    display_filters["sort"] = form.cleaned_data.get("sort", "date")
    display_filters["per_page"] = str(page_size)
    return render(request, "requests/search.html" if is_search else "requests/request_list.html", {
        "study_requests": page_obj.object_list, "page_obj": page_obj,
        "filters": display_filters, "status": parameters["status"],
        "subjects": get_subjects(), "users": get_users(), "formats": distinct_formats(),
        "participants": participants, "error": error, "is_search": is_search,
        "status_choices": StudyRequest.Status.choices, "sort_options": SORT_OPTIONS,
        "page_sizes": ["2", "5", "10", "20"],
    }, status=400 if error else 200)


def requests(request: HttpRequest) -> HttpResponse:
    return _catalog(request, is_search=False)


def search(request: HttpRequest) -> HttpResponse:
    return _catalog(request, is_search=True)


def request_detail(request: HttpRequest, request_id: int) -> HttpResponse:
    try:
        target = get_object_or_404(StudyRequest.objects.select_related("user", "subject"),
                                   pk=request_id)
    except Http404:
        return render(request, "404.html", {"message": "Запрос не найден"}, status=404)
    return render(request, "requests/request_detail.html", {"study_request": target})


def statistics(request: HttpRequest) -> HttpResponse:
    raw = request.GET.get("min_count", "2")
    error = ""
    if not raw.isascii() or not raw.isdecimal() or len(raw) > 6 or int(raw) < 1:
        error = "Минимум запросов: введите целое число от 1 до 999999."
        threshold = 2
    else:
        threshold = int(raw)
    return render(request, "requests/statistics.html", {
        "totals": request_totals(), "catalog": catalog_totals(),
        "subject_stats": subject_statistics(), "user_stats": user_statistics(),
        "format_stats": format_statistics(), "period": date_range(),
        "popular": popular_subjects(threshold), "min_count": threshold, "error": error,
    }, status=400 if error else 200)
