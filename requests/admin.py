from django.contrib import admin

from .models import StudyRequest


@admin.register(StudyRequest)
class StudyRequestAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "subject", "format", "study_date", "is_closed")
    list_filter = ("is_closed", "format", "subject")
    search_fields = ("user__name", "subject__name")
    list_select_related = ("user", "subject")
    date_hierarchy = "study_date"
    actions = ("close_search",)

    @admin.action(description="Завершить поиск по выбранным запросам")
    def close_search(self, request, queryset):
        count = queryset.update(is_closed=True)
        self.message_user(request, f"Завершено запросов: {count}.")
