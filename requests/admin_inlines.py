"""Связанные учебные запросы в карточках участников и предметов."""
from django.contrib import admin

from requests.models import StudyRequest


class StudyRequestInline(admin.TabularInline):
    model = StudyRequest
    extra = 0
    show_change_link = True
    ordering = ("study_date", "pk")

    def get_queryset(self, request):
        return super().get_queryset(request).select_related("user", "subject")


class SubjectRequestInline(StudyRequestInline):
    fk_name = "subject"
    fields = ("user", "format", "study_date", "status")
    autocomplete_fields = ("user",)


class UserRequestInline(StudyRequestInline):
    fk_name = "user"
    fields = ("subject", "format", "study_date", "status")
    autocomplete_fields = ("subject",)
