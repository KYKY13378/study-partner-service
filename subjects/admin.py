from django.contrib import admin

from homepage.admin_utils import UnicodeSearchAdminMixin
from requests.admin_inlines import SubjectRequestInline
from .models import Subject


@admin.register(Subject)
class SubjectAdmin(UnicodeSearchAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "slug")
    list_display_links = ("id", "name")
    search_fields = ("name",)
    ordering = ("name", "pk")
    list_per_page = 10
    readonly_fields = ("slug",)
    inlines = (SubjectRequestInline,)
    view_on_site = True
