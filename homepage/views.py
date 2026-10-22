# homepage/views.py
from django.http import HttpResponse
from django.utils.html import escape


def page(title: str, content: str) -> str:
    """Собрать общий HTML-каркас страницы проекта.

    Args:
        title: Заголовок вкладки браузера.
        content: HTML-содержимое страницы.

    Returns:
        Готовый HTML-документ.
    """
    bootstrap = (
        "https://cdn.jsdelivr.net/npm/bootstrap@5.3.3"
        "/dist/css/bootstrap.min.css"
    )
    return f"""<!DOCTYPE html>
<html lang="ru">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(title)}</title>
<link rel="stylesheet" href="{bootstrap}">
</head>
<body>
<nav class="nav">
<a class="nav-link" href="/">Главная</a>
<a class="nav-link" href="/subjects/">Предметы</a>
<a class="nav-link" href="/requests/">Запросы</a>
</nav>
<main class="container">{content}</main>
</body>
</html>"""


def index(request):
    """Главная страница сервиса."""
    content = """
<h1 class="display-4">Сервис поиска партнеров для учебы</h1>
<p class="lead">Консольный проект ПР3 получил веб-интерфейс на Django.</p>
<p>Основные разделы:</p>
<a href="/subjects/" class="btn btn-primary me-2">Предметы</a>
<a href="/requests/" class="btn btn-secondary">Запросы</a>
"""
    return HttpResponse(page("Сервис поиска партнеров", content))


def page_not_found(request, exception):
    """Собственная страница ошибки 404."""
    content = """
<h1 class="text-danger">404 – страница не найдена</h1>
<p>Проверьте адрес или вернитесь на главную.</p>
<a href="/" class="btn btn-primary">На главную</a>
"""
    return HttpResponse(
        page("404 – страница не найдена", content),
        status=404,
    )
