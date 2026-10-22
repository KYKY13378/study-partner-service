# requests/urls.py
from django.urls import path

from . import views

app_name = "requests"

urlpatterns = [
    path("", views.requests, name="list"),
    path("search/", views.search, name="search"),
    path("statistics/", views.statistics, name="statistics"),
    path("<int:request_id>/", views.request_detail, name="detail"),
]
