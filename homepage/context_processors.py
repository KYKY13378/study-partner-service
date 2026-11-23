"""Общие данные вычисляются только если их использует шаблон."""
from django.utils.functional import SimpleLazyObject

from subjects.models import Subject


def site_info(request):
    return {"site_name": "Учимся вместе",
            "site_subject_count": SimpleLazyObject(lambda: Subject.objects.count())}
