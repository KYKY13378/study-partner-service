from django.contrib import admin

from homepage.admin_utils import UnicodeSearchAdminMixin
from requests.admin_inlines import UserRequestInline
from .models import User


@admin.register(User)
class UserAdmin(UnicodeSearchAdminMixin, admin.ModelAdmin):
    list_display = ("id", "name", "group_name", "display_name")
    list_display_links = ("id", "name")
    list_filter = ("group_name",)
    search_fields = ("name", "group_name")
    ordering = ("name", "pk")
    list_per_page = 10
    readonly_fields = ("display_name",)
    inlines = (UserRequestInline,)
