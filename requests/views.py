# requests/views.py
from django.http import HttpResponse
from django.utils.html import escape
from homepage.views import page
from src.requests import find_request_by_id
from src.storage import load_requests, load_subjects, load_users


def requests(request):
    """Страница со списком запросов на партнёрство."""
    users_list = load_users()
    subjects_list = load_subjects()
    requests_list = load_requests(users_list, subjects_list)

    items = ""
    for r in requests_list:
        status = "закрыт" if r.is_closed else "активен"
        badge = "bg-secondary" if r.is_closed else "bg-success"
        items += f"""
<li class="list-group-item d-flex justify-content-between">
<a href="/requests/{r.id}/">
{escape(r.user.name)} – {escape(r.subject.name)} ({escape(r.date)})
</a>
<span class="badge {badge}">{status}</span>
</li>
"""
    if not items:
        items = '<li class="list-group-item">Запросов пока нет.</li>'
    content = f"""
<h1>Запросы на партнёрство</h1>
<ul class="list-group">{items}</ul>
"""
    return HttpResponse(page("Сервис – запросы", content))


def request_detail(request, request_id):
    """Страница отдельного запроса на партнёрство."""
    users_list = load_users()
    subjects_list = load_subjects()
    requests_list = load_requests(users_list, subjects_list)
    target = find_request_by_id(requests_list, request_id)
    if target is None:
        content = """
<h1 class="text-danger">Запрос не найден</h1>
<a href="/requests/" class="btn btn-outline-secondary">
← к списку запросов
</a>
"""
        return HttpResponse(
            page("Запрос не найден", content),
            status=404,
        )

    status = "закрыт" if target.is_closed else "активен"
    badge = "bg-secondary" if target.is_closed else "bg-success"
    content = f"""
<div class="card">
<div class="card-body">
<h5 class="card-title">Запрос №{target.id}</h5>
<p class="card-text">Автор: {escape(target.user.name)}
(группа {escape(target.user.group)})</p>
<p class="card-text">Предмет: {escape(target.subject.name)}</p>
<p class="card-text">Формат: {escape(target.format)}</p>
<p class="card-text">Дата: {escape(target.date)}</p>
<p class="card-text">Статус:
<span class="badge {badge}">{status}</span></p>
<a href="/requests/" class="btn btn-outline-secondary">
← к списку запросов
</a>
</div>
</div>
"""
    return HttpResponse(
        page(f"Запрос №{target.id}", content),
        status=200,
    )
