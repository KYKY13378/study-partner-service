"""Рабочие ORM-выражения ПР9. Все функции вызываются страницами приложения."""
import re

from django.db.models import Count, F, Max, Min, Q

from requests.models import StudyRequest
from subjects.models import Subject
from users.models import User

SORT_FIELDS = {
    "date": ("study_date", "pk"),
    "date_desc": ("-study_date", "-pk"),
    "subject": ("subject__name", "study_date", "pk"),
    "author": ("user__name", "study_date", "pk"),
}


def get_subjects():
    """Q01: список объектов для главной и выпадающих списков."""
    return Subject.objects.all()


def get_users():
    """Q02: только нужные поля авторов в форме поиска."""
    return User.objects.values("id", "name", "group_name").order_by("name", "pk")


def get_subject_cards(text=""):
    """Q03/Q04: статистика с нулевыми значениями; поиск по одному строковому полю."""
    items = Subject.objects.annotate(active_count=Count(
        "study_requests", filter=Q(study_requests__is_closed=False),
    )).order_by("pk")
    if text:
        # iregex в SQLite реализуется Django через Python re и поддерживает кириллицу.
        # re.escape превращает ввод в буквальный текст, а не пользовательскую регулярку.
        items = items.filter(name__iregex=re.escape(text))
    return [{"subject": subject, "active_count": subject.active_count} for subject in items]


def get_requests(status="all"):
    """Q05/Q06/Q07: связанные объекты, активные и закрытые запросы."""
    items = StudyRequest.objects.select_related("user", "subject")
    if status == "active":
        return items.filter(is_closed=False)
    if status == "closed":
        return items.filter(is_closed=True)
    return items


def filter_requests(items, filters):
    """Q08/Q09: несколько условий, поля связанных моделей и поиск через Q."""
    conditions = {}
    for field, key in (("study_date", "date"), ("subject_id", "subject"),
                       ("user_id", "user"), ("format", "format")):
        if filters.get(key):
            conditions[field] = filters[key]
    if conditions:
        items = items.filter(**conditions)
    text = filters.get("q")
    if text:
        pattern = re.escape(text)
        items = items.filter(Q(subject__name__iregex=pattern) | Q(user__name__iregex=pattern)
                             | Q(user__group_name__iregex=pattern))
    return items


def sort_requests(items, sort):
    """Q10/Q11: поля сортировки выбираются из фиксированного словаря."""
    return items.order_by(*SORT_FIELDS.get(sort, SORT_FIELDS["date"]))


def get_requests_for_subject(subject):
    """Q12: обратная связь, фильтрация и загрузка автора одним JOIN."""
    return subject.study_requests.filter(is_closed=False).select_related("user", "subject")


def get_recent_requests():
    """Q13: ограничение результата срезом QuerySet на главной."""
    return StudyRequest.objects.select_related("user", "subject").order_by("-pk")[:3]


def request_totals():
    """Q14: агрегаты над всей таблицей, включая корректные нули без записей."""
    return StudyRequest.objects.aggregate(
        total=Count("pk"), active=Count("pk", filter=Q(is_closed=False)),
        closed=Count("pk", filter=Q(is_closed=True)),
    )


def catalog_totals():
    """Q15/Q16: самостоятельные подсчёты участников и предметов."""
    return {"users": User.objects.count(), "subjects": Subject.objects.count()}


def subject_statistics():
    """Q17: LEFT JOIN сохраняет предметы без учебных запросов."""
    return Subject.objects.annotate(active_count=Count(
        "study_requests", filter=Q(study_requests__is_closed=False),
    )).order_by("pk")


def user_statistics():
    """Q18: условные подсчёты по каждому участнику."""
    return User.objects.annotate(
        total=Count("study_requests"),
        active=Count("study_requests", filter=Q(study_requests__is_closed=False)),
        closed=Count("study_requests", filter=Q(study_requests__is_closed=True)),
    ).order_by("pk")


def popular_subjects(minimum):
    """Q19: фильтрация по аннотации преобразуется в SQL HAVING."""
    return subject_statistics().filter(active_count__gte=minimum).order_by("-active_count", "pk")


def format_statistics():
    """Q20: группировка values + annotate по формату занятия."""
    return StudyRequest.objects.order_by().values("format").annotate(
        total=Count("pk"), active=Count("pk", filter=Q(is_closed=False)),
    ).order_by("format")


def date_range():
    """Q21: границы периода занятий."""
    return StudyRequest.objects.aggregate(first_date=Min("study_date"), last_date=Max("study_date"))


def users_without_requests_for_date(day):
    """Q22/Q23: подзапрос values_list и exclude; закрытые запросы не мешают."""
    busy = StudyRequest.objects.filter(study_date=day, is_closed=False).values_list(
        "user_id", flat=True,
    )
    return User.objects.exclude(pk__in=busy)


def distinct_formats():
    """Q24: уникальные значения для списка форматов."""
    return StudyRequest.objects.order_by("format").values_list("format", flat=True).distinct()


def request_rows(items):
    """Q25: F-выражения и values используются табличным видом каталога."""
    return items.annotate(
        user_name=F("user__name"), subject_name=F("subject__name"),
        user_group=F("user__group_name"),
    ).values("id", "user_id", "subject_id", "user_name", "subject_name", "user_group",
             "format", "study_date", "is_closed")
