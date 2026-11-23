from django.conf import settings
# study_partner/urls.py
from django.contrib import admin
from django.urls import include, path

admin.site.site_header = "Учимся вместе — управление сервисом"
admin.site.site_title = "Учебные партнерства"
admin.site.index_title = "Предметы, участники и учебные запросы"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("homepage.urls")),
    path("subjects/", include("subjects.urls")),
    path("requests/", include("requests.urls")),
]
handler404 = "homepage.views.page_not_found"


if settings.DEBUG_TOOLBAR_ENABLED:
    from debug_toolbar.toolbar import debug_toolbar_urls
    urlpatterns += debug_toolbar_urls()
