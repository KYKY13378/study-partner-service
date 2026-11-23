# subjects/urls.py
from django.urls import path

from . import views

app_name = "subjects"

urlpatterns = [
    path("", views.subjects, name="list"),
    path("<int:subject_id>/", views.subject_detail, name="detail"),
    path("<slug:slug>/", views.subject_detail, name="detail_slug"),
]
