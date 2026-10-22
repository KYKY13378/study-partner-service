# subjects/views.py
from django.http import HttpResponse
from django.utils.html import escape
from homepage.views import page
from src.requests import find_requests_by_subject
from src.storage import load_requests, load_subjects, load_users
from src.subjects import find_subject_by_id


def subjects(request):
    """Страница со списком предметов."""
    items = ""
    for subject in load_subjects():
        items += (
            f'<li class="list-group-item">'
            f'<a href="/subjects/{subject.id}/">{escape(subject.name)}</a>'
            f"</li>"
        )
    if not items:
        items = '<li class="list-group-item">Предметов пока нет.</li>'
    content = f"""
<h1>Предметы</h1>
<ul class="list-group">{items}</ul>
"""
    return HttpResponse(page("Сервис – предметы", content))


def subject_detail(request, subject_id):
    """Страница отдельного предмета."""
    subjects_list = load_subjects()
    subject = find_subject_by_id(subjects_list, subject_id)
    if subject is None:
        content = """
<h1 class="text-danger">Предмет не найден</h1>
<a href="/subjects/" class="btn btn-outline-secondary">
← к списку предметов
</a>
"""
        return HttpResponse(
            page("Предмет не найден", content),
            status=404,
        )

    users_list = load_users()
    requests_list = load_requests(users_list, subjects_list)
    active = [
        r
        for r in find_requests_by_subject(requests_list, subject.name)
        if not r.is_closed
    ]
    if active:
        status = f"активных запросов: {len(active)}"
        badge = "bg-success"
    else:
        status = "активных запросов нет"
        badge = "bg-secondary"

    items = ""
    for r in active:
        items += (
            f'<li class="list-group-item">'
            f'<a href="/requests/{r.id}/">{escape(r.user.name)}</a>'
            f" ({escape(r.format)}, {escape(r.date)})</li>"
        )
    if not items:
        items = '<li class="list-group-item">Запросов пока нет.</li>'

    content = f"""
<div class="card">
<div class="card-body">
<h5 class="card-title">{escape(subject.name)}</h5>
<p class="card-text"><strong>ID:</strong> {subject.id}</p>
<p class="card-text">Статус: <span class="badge {badge}">{status}</span></p>
<h6>Активные запросы:</h6>
<ul class="list-group">{items}</ul>
<a href="/subjects/" class="btn btn-outline-secondary">
← к списку предметов
</a>
</div>
</div>
"""
    return HttpResponse(page(subject.name, content), status=200)
