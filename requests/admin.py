from django.contrib import admin

from homepage.admin_utils import UnicodeSearchAdminMixin
from .models import StudyRequest


@admin.register(StudyRequest)
class StudyRequestAdmin(UnicodeSearchAdminMixin, admin.ModelAdmin):
    list_display = ("id", "user", "subject", "format", "study_date", "status")
    list_display_links = ("id", "user")
    list_filter = ("status", "format", "subject", "study_date")
    search_fields = ("user__name", "user__group_name", "subject__name")
    search_help_text = "Поиск по имени, группе участника или названию предмета."
    list_select_related = ("user", "subject")
    autocomplete_fields = ("user", "subject")
    date_hierarchy = "study_date"
    ordering = ("-study_date", "-pk")
    list_per_page = 10
    actions = ("complete_search", "cancel_search", "reopen_search")
    fieldsets = (("Учебные планы", {"fields": ("user", "subject", "format", "study_date")}),
                 ("Состояние поиска", {"fields": ("status",)}))

    def set_status(self, request, queryset, status):
        count = queryset.exclude(status=status).update(status=status)
        self.message_user(request, f"Изменено запросов: {count}.")

    @admin.action(description="Завершить поиск по выбранным запросам", permissions=["change"])
    def complete_search(self, request, queryset):
        self.set_status(request, queryset, StudyRequest.Status.COMPLETED)

    @admin.action(description="Отменить выбранные запросы", permissions=["change"])
    def cancel_search(self, request, queryset):
        self.set_status(request, queryset, StudyRequest.Status.CANCELLED)

    @admin.action(description="Возобновить поиск", permissions=["change"])
    def reopen_search(self, request, queryset):
        self.set_status(request, queryset, StudyRequest.Status.ACTIVE)
